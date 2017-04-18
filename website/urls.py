from django.conf.urls import url
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', login, {'template_name': 'website/login.html'},
        name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': 'login'}, name='logout'),
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^create/step-one/$', views.create_step_one, name='create_step_one'),
    url(r'^create/step-two/(?P<student_id>\d+)$',
        login_required(views.CreateStepTwo.as_view()), name='create_step_two'),
    url(r'^delete/(?P<pk>\d+)$', views.delete_thesis, name='delete_thesis'),
    url(r'^download/(?P<pk>\d+)$', views.download, name='download'),
]
