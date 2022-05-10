from django.urls import path, re_path

from approvals import views

urlpatterns = [
    #re_path(r'.*', views.index, name='index'),
    re_path(r'approve/(?P<key>[0-9a-f\-]+)', views.approve, name="approve"),
    re_path(r'reject/(?P<key>[0-9a-f\-]+)', views.reject, name="reject"),
    re_path(r'.*', views.index, name='index'),
]
