from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^browse$', views.browse),
    url(r'^query$', views.query),
    url(r'^upload$', views.upload)
]