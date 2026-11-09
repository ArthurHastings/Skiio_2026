from django.contrib import admin
from .models import Categorie, Brand, ServiciuAditional, Schi, SediuCompanie, Raion


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'nivel_recomandat', 'culoare', 'sigla')
    list_filter = ('nivel_recomandat',)
    search_fields = ('nume',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('nume', 'tara_origine', 'an_infiintare', 'website')
    search_fields = ('nume', 'tara_origine')


@admin.register(ServiciuAditional)
class ServiciuAditionalAdmin(admin.ModelAdmin):
    list_display = ('nume_serviciu', 'pret_serviciu', 'durata_minute')


@admin.register(Schi)
class SchiAdmin(admin.ModelAdmin):
    list_display = ('nume_model', 'brand', 'categorie', 'lungime_cm', 'pret', 'stoc', 'profil', 'data_adaugare')
    list_filter = ('brand', 'categorie', 'profil', 'include_legaturi')
    search_fields = ('nume_model', 'cod_model')
    prepopulated_fields = {'slug': ('nume_model',)}


@admin.register(SediuCompanie)
class SediuCompanieAdmin(admin.ModelAdmin):
    list_display = ('oras', 'adresa', 'telefon', 'email_sediu')
    search_fields = ('oras', 'adresa')


@admin.register(Raion)
class RaionAdmin(admin.ModelAdmin):
    list_display = ('nume_raion', 'sediu', 'etaj')
    list_filter = ('sediu', 'etaj')