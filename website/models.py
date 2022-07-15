from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, connections, transaction

from thesispool.settings import AUTH_LDAP_USER_DN_TEMPLATE
from thesispool.settings import AUTH_LDAP_SERVER_URI
from thesispool.settings import AUTH_LDAP_PROF_DN

from datetime import datetime
import ldap
import uuid


class User(AbstractUser):
    initials = models.CharField(max_length=10, blank=True, null=True)
    is_prof = models.BooleanField(default=False)
    is_secretary = models.BooleanField(default=False)
    is_excom = models.BooleanField(default=False)
    is_head = models.BooleanField(default=False)


class ThesisManager(models.Manager):

    def for_supervisor(self, supervisor_id):
        theses = self.filter(
            supervisor__id=supervisor_id).order_by('status', 'due_date')

        return theses


class SupervisorManager(models.Manager):

    def fetch_supervisor(self, uid, con=None):
        need_unbind = False

        try:
            con = ldap.initialize(AUTH_LDAP_SERVER_URI, trace_level=0)
            con.start_tls_s()
            need_unbind = True
        finally:
            dn = AUTH_LDAP_USER_DN_TEMPLATE % {'user': uid}

            results = con.search_s(dn, ldap.SCOPE_SUBTREE, "(objectClass=*)")

            try:
                entity = results[0][1]
                return Supervisor(first_name=entity["givenName"][0].decode(),
                                  last_name=entity["sn"][0].decode(),
                                  initials=entity["initials"][0].decode(),
                                  id=entity["uid"][0].decode())
            except Exception:
                return None

            finally:
                if need_unbind:
                    con.unbind()

    def fetch_supervisors_from_ldap(self):
        con = ldap.initialize(AUTH_LDAP_SERVER_URI, trace_level=0)
        
        try:
            con.start_tls_s()
        finally:
            _, entry = con.search_s(AUTH_LDAP_PROF_DN, ldap.SCOPE_BASE)[0]

            uids = [uid.decode() for uid in entry['memberUid']]

            supervisors = [self.fetch_supervisor(uid, con) for uid in uids]

            con.unbind()

            return [s for s in supervisors if s is not None]


class StudentManager(models.Manager):
    """Custom manager that allows for reading from an external DB"""

    def find(self, matnr):
        """
        Fetch student from external database, return None if matnr is invalid.
        """
        sql = """select id,
                        firstname,
                        lastname,
                        program
                from student where id = %s"""

        cursor = connections['faculty'].cursor()
        cursor.execute(sql, [matnr],)
        row = cursor.fetchone()

        return None if not row else Student.from_raw(row)


class Student(models.Model):
    """Model for students. Model is a little bit tricky as students are read from
    a read-only MySQL DB (a.k.a. the faculty DB) and saved to the internal
    database. In order to make it testable the table name and all column names
    need to be the same internally and externally so that all mappings work
    even if the DB is being switched.
    """

    class Meta:
        """Same as in faculty DB"""
        db_table = 'student'

    id = models.IntegerField(primary_key=True, db_column='id')
    first_name = models.CharField(max_length=30, db_column='firstname')
    last_name = models.CharField(max_length=30, db_column='lastname')
    program = models.CharField(max_length=10, db_column='program')

    objects = StudentManager()

    @property
    def email(self):
        """Generate email address using the default pattern"""
        return "{0}@stud.hs-mannheim.de".format(self.id)

    def is_master(self):
        """Checks if the student is a master student"""
        return self.program == 'IM'

    def is_bachelor(self):
        """Checks if the student is a bachelor student"""
        return not self.is_master()

    @classmethod
    def from_raw(cls, record):
        """Create a student instance from a raw record
        that was fetched from the faculty DB"""
        return cls(id=record[0],
                   first_name=record[1],
                   last_name=record[2],
                   program=record[3])

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name,
                                      self.last_name,
                                      self.program)


class Thesis(models.Model):

    class Meta:
        verbose_name_plural = "theses"

    APPLIED = 0
    PROLONGED = 1
    HANDED_IN = 2
    GRADED = 3
    STATUS_CHOICES = (
        (APPLIED, 'Angemeldet'),
        (PROLONGED, 'Verlängert'),
        (HANDED_IN, 'Abgegeben'),
        (GRADED, 'Benotet'),
    )
    EXCOM_APPROVED = 1
    EXCOM_REJECTED = 2
    EXCOM_STATUS_CHOICES = (
        (APPLIED, 'Angemeldet'),
        (EXCOM_APPROVED, 'Genehmigt'),
        (EXCOM_REJECTED, 'Abgelehnt'),
    )

    title = models.CharField(max_length=200)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    assessor = models.ForeignKey(
        'Assessor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    thesis_program = models.CharField(max_length=3)
    begin_date = models.DateField()
    due_date = models.DateField()
    external = models.BooleanField(default=False)
    external_where = models.CharField(max_length=200, blank=True)
    surrogate_key = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=APPLIED,
    )
    excom_status = models.IntegerField(
        choices=EXCOM_STATUS_CHOICES,
        default=APPLIED,
    )
    excom_reject_reason = models.CharField(
        blank=True,
        null=True,
        max_length=2000)
    excom_chairman = models.ForeignKey(
        'ExcomChairman', on_delete=models.CASCADE, blank=True, null=True)
    excom_approval_date = models.DateField(blank=True, null=True)
    student_contact = models.EmailField(blank=True)
    grade = models.DecimalField(max_digits=2,
                                decimal_places=1,
                                blank=True,
                                null=True,
                                validators=[
                                    MinValueValidator(1.0),
                                    MaxValueValidator(5.0)])
    assessor_grade = models.DecimalField(max_digits=2,
                                decimal_places=1,
                                blank=True,
                                null=True,
                                validators=[
                                    MinValueValidator(1.0),
                                    MaxValueValidator(5.0)])
    prolongation_date = models.DateField(blank=True, null=True)
    prolongation_reason = models.CharField(
        blank=True,
        null=True,
        max_length=2000)
    prolongation_weeks = models.IntegerField(blank=True, null=True)
    examination_date = models.DateField(blank=True, null=True)
    handed_in_date = models.DateField(blank=True, null=True)
    restriction_note = models.BooleanField(blank=True, null=True)

    objects = ThesisManager()

    @transaction.atomic
    def approve(self, user):
        if self.excom_status == Thesis.EXCOM_APPROVED:
            return False

        excom_chairman = ExcomChairman.from_user(user)
        excom_chairman.save()

        self.excom_chairman = excom_chairman
        self.excom_approval_date = datetime.now().date()
        self.excom_status = Thesis.EXCOM_APPROVED

        self.clean_fields()
        self.save()

        return True

    def reject(self, user, reason):
        if self.excom_status > Thesis.APPLIED:
            return False

        excom_chairman = ExcomChairman.from_user(user)
        excom_chairman.save()

        self.excom_chairman = excom_chairman

        self.excom_status = Thesis.EXCOM_REJECTED
        self.excom_reject_reason = reason
        self.clean_fields()
        self.save()

        return True

    def assign_grade(self, grade, assessor_grade, examination_date, restriction_note=False):
        """Assign grade and set status to GRADED
        if grade is valid and thesis hasn't been graded yet"""
        if self.status >= Thesis.GRADED:
            return False

        self.grade = grade
        self.assessor_grade = assessor_grade
        self.examination_date = examination_date
        self.restriction_note = restriction_note
        self.clean_fields()
        self.status = Thesis.GRADED
        self.save()

        return True

    def prolong(self, prolongation_date, reason, weeks):
        if self.status >= Thesis.HANDED_IN:
            return False

        self.prolongation_date = prolongation_date
        self.prolongation_reason = reason
        self.prolongation_weeks = weeks

        self.full_clean()
        self.status = Thesis.PROLONGED
        self.save()

        return True

    def hand_in(self, handed_in_date, restriction_note=False):
        """Set the handed_in_date of a thesis.
        It is possible to hand in a thesis before or after grading. Handing in
        a thesis after it was graded does not change the GRADED status."""
        if self.status == Thesis.HANDED_IN:
            return False

        self.handed_in_date = handed_in_date
        self.restriction_note = restriction_note
        self.full_clean()
        if self.status < Thesis.HANDED_IN:
            self.status = Thesis.HANDED_IN
        self.save()

        return True

    @property
    def deadline(self):
        return self.prolongation_date if self.is_prolonged() else self.due_date

    def status_changed(self):
        return self.status == 0 and self.excom_status == 0

    def is_handed_in(self):
        return self.handed_in_date is not None

    def is_graded(self):
        return self.status == Thesis.GRADED

    def is_prolonged(self):
        return self.prolongation_date is not None

    def is_late(self):
        if not self.is_handed_in():
            return False

        if self.is_prolonged():
            return self.handed_in_date > self.prolongation_date
        else:
            return self.handed_in_date > self.due_date

    def is_approved(self):
        return self.excom_status == Thesis.EXCOM_APPROVED

    def is_rejected(self):
        return self.excom_status == Thesis.EXCOM_REJECTED

    def is_master(self):
        return self.thesis_program == 'IM'

    def is_bachelor(self):
        return not self.is_master()

    def clean(self):
        self.clean_fields()

        if self.is_prolonged() and self.prolongation_date <= self.due_date:
            raise ValidationError(
                {'prolongation_date':
                    'prolongation date must be later than due date'})

    def __str__(self):
        return "'{0}' ({1})".format(self.title, self.student)


class ExcomChairman(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Vorname")
    last_name = models.CharField(max_length=30, verbose_name="Nachname")
    initials = models.CharField(max_length=10, verbose_name="Kürzel")
    id = models.CharField(max_length=30, primary_key=True)

    objects = SupervisorManager()

    @classmethod
    def from_user(cls, user):
        initials = user.initials if hasattr(user, 'initials') else ""

        return cls(id=user.username,
                   first_name=user.first_name,
                   last_name=user.last_name,
                   initials=initials)

    def __str__(self):
        return "{0} {1} ({2})".format(
            self.first_name,
            self.last_name,
            self.initials)

    __repr__ = __str__


class Supervisor(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Vorname")
    last_name = models.CharField(max_length=30, verbose_name="Nachname")
    initials = models.CharField(max_length=10, verbose_name="Kürzel")
    id = models.CharField(max_length=30, primary_key=True)

    objects = SupervisorManager()

    @classmethod
    def from_user(cls, user):
        initials = user.initials if hasattr(user, 'initials') else ""

        return cls(id=user.username,
                   first_name=user.first_name,
                   last_name=user.last_name,
                   initials=initials)

    @property
    def short_name(self):
        return "{0}.{1}".format(self.first_name[0], self.last_name)

    def __str__(self):
        return "{0} {1} ({2})".format(
            self.first_name,
            self.last_name,
            self.initials)

    __repr__ = __str__


class Assessor(models.Model):
    first_name = models.CharField(
        max_length=30, verbose_name="Vorname")
    last_name = models.CharField(
        max_length=30, verbose_name="Nachname")
    email = models.EmailField(
        max_length=80, verbose_name="E-Mail", blank=True, null=True)

    @property
    def short_name(self):
        return "{0}.{1}".format(self.first_name[0], self.last_name)

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name,
                                      self.last_name,
                                      self.email)

    __repr__ = __str__
