from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', login, {'template_name': 'website/login.html'},
        name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': 'login'}, name='logout'),
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^create/$', views.create, name='create'),
    url(r'^delete/(?P<pk>\d+)$', views.delete_thesis, name='delete_thesis'),
]
