from django.db import models


class Thesis(models.Model):
    title = models.CharField(max_length=200)
    supervisor = models.ForeignKey('Supervisor')
    assessor = models.ForeignKey('Assessor')


class Supervisor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    id = models.CharField(max_length=30, primary_key=True)


class Assessor(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=80)
