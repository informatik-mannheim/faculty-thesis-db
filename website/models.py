from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import connections
from django.utils import timezone

import uuid


class User(AbstractUser):
    initials = models.CharField(max_length=10, blank=True, null=True)


class ThesisManager(models.Manager):

    def for_supervisor(self, supervisor_id):
        theses = self.filter(
            supervisor__id=supervisor_id).order_by('due_date')

        return theses


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

    APPLIED = 'AP'
    PROLONGED = 'PL'
    HANDED_IN = 'HI'
    GRADED = 'GD'
    STATUS_CHOICES = (
        (APPLIED, 'Angemeldet'),
        (PROLONGED, 'Verlängert'),
        (HANDED_IN, 'Abgegeben'),
        (GRADED, 'Benotet'),
    )

    title = models.CharField(max_length=200)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    assessor = models.ForeignKey(
        'Assessor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    begin_date = models.DateField()
    due_date = models.DateField()
    external = models.BooleanField(default=False)
    external_where = models.CharField(max_length=200, blank=True)
    surrogate_key = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=APPLIED,
    )
    student_contact = models.EmailField(blank=True)
    grade = models.DecimalField(max_digits=2,
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
    restriction_note = models.NullBooleanField(blank=True)

    objects = ThesisManager()

    def assign_grade(self, grade, examination_date, restriction_note=False):
        """Assign grade and set status to GRADED
        if grade is valid and thesis hasn't been graded yet"""
        if self.is_graded():
            return False

        self.grade = grade
        self.examination_date = examination_date
        self.restriction_note = restriction_note
        self.clean_fields()
        self.status = Thesis.GRADED
        self.save()

        return True

    def prolong(self, prolongation_date, reason, weeks):
        if self.status != Thesis.APPLIED and self.status != Thesis.PROLONGED:
            return False

        self.prolongation_date = prolongation_date
        self.prolongation_reason = reason
        self.prolongation_weeks = weeks

        self.full_clean()
        self.status = Thesis.PROLONGED
        self.save()

        return True

    def is_graded(self):
        return self.status == Thesis.GRADED

    def was_prolonged(self):
        return self.prolongation_date is not None

    def is_late(self):
        if self.was_prolonged():
            return self.handed_in_date and self.handed_in_date > self.prolongation_date
        else:
            return self.handed_in_date and self.handed_in_date > self.due_date

    def clean(self):
        self.clean_fields()

        if self.was_prolonged() and self.prolongation_date <= self.due_date:
            raise ValidationError(
                {'prolongation_date':
                    'prolongation date must be later than due date'})

    def __str__(self):
        return "'{0}' ({1})".format(self.title, self.student)


class Supervisor(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Vorname")
    last_name = models.CharField(max_length=30, verbose_name="Nachname")
    initials = models.CharField(max_length=10, verbose_name="Kürzel")
    id = models.CharField(max_length=30, primary_key=True)

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


class Assessor(models.Model):
    first_name = models.CharField(
        max_length=30, verbose_name="Vorname")
    last_name = models.CharField(
        max_length=30, verbose_name="Nachname")
    email = models.EmailField(
        max_length=80, verbose_name="E-Mail")

    @property
    def short_name(self):
        return "{0}.{1}".format(self.first_name[0], self.last_name)

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name,
                                      self.last_name,
                                      self.email)

    __repr__ = __str__
