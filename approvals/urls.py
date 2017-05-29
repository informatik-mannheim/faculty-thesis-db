from django.conf.urls import url

from approvals import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^approve/(?P<key>[0-9a-f\-]+)$', views.approve, name="approve"),
    url(r'^reject/(?P<key>[0-9a-f\-]+)$', views.reject, name="reject"),
]
