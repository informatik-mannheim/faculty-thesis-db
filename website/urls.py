from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

from . import views
from thesispool.pdf import *

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.ThesispoolLoginView.as_view(),
         name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    re_path(r'overview/(?P<key>student|title|due_date|status|assessor)?', views.overview, name='overview'),
    path('find-student/', views.find_student, name='find_student'),
    re_path(r'create/(?P<student_id>\d+)',
        login_required(views.CreateThesis.as_view()), name='create'),
    re_path(r'download/application/(?P<key>[0-9a-f\-]+)',
        login_required(views.PdfView.as_view()),
        {"type": ApplicationPDF},
        name='application_pdf'),
    re_path(r'download/prolongation/(?P<key>[0-9a-f\-]+)',
        login_required(views.PdfView.as_view()),
        {"type": ProlongationPDF},
        name='prolongation_pdf'),
    re_path(r'download/prolong_illness/(?P<key>[0-9a-f\-]+)',
        login_required(views.PdfView.as_view()),
        {"type": ProlongIllnessPDF},
        name='prolong_illness_pdf'),
    re_path(r'download/grading/(?P<key>[0-9a-f\-]+)',
        login_required(views.PdfView.as_view()),
        {"type": GradingPDF},
        name='grading_pdf'),
    re_path(r'prolong/(?P<key>[0-9a-f\-]+)', views.prolong, name="prolong"),
    re_path(r'grade/(?P<key>[0-9a-f\-]+)', views.grade, name="grade"),
    re_path(r'handin/(?P<key>[0-9a-f\-]+)', views.handin, name="handin"),
    re_path(r'change/(?P<key>[0-9a-f\-]+)',
        login_required(views.ChangeView.as_view()), name="change"),
]
