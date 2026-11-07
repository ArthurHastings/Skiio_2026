from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("info", views.info, name="info"),
    path("log", views.log_view, name="log"),
    path("despre", views.despre, name="despre"),
    path("istoric", views.istoric, name="istoric"),
    path("produse", views.in_lucru, name="produse"),
    path("contact", views.in_lucru, name="contact"),
    path("cos_virtual", views.in_lucru, name="cos_virtual"),
    re_path(r"^accesare(?P<id_accesare>\d+)$", views.detalii_accesare, name="detalii_accesare"),
    ]