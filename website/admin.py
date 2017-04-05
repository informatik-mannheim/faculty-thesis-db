from django.contrib import admin
from website.models import Thesis, Assessor, Supervisor, Student


admin.site.register(Thesis)
admin.site.register(Assessor)
admin.site.register(Supervisor)
admin.site.register(Student)
