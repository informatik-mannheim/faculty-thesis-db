from django.db import models


class Thesis(models.Model):
    title = models.CharField(max_length=200)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    assessor = models.ForeignKey('Assessor', on_delete=models.CASCADE)

    def __str__(self):
        return "{0}".format(self.title)


class Supervisor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    id = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name, self.last_name, self.id)

    __repr__ = __str__


class Assessor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=80)

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name,
                                      self.last_name,
                                      self.email)

    __repr__ = __str__
