from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Categorie(models.Model):
    NIVEL_CHOICES = [
        ('incepator', 'Incepator'),
        ('intermediar', 'Intermediar'),
        ('avansat', 'Avansat / Expert'),
    ]

    nume = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            'unique': 'Exista deja o categorie de schiuri cu acest nume.',
            'max_length': 'Numele categoriei nu poate depasi 50 de caractere.'
        }
    )
    descriere = models.TextField(null=True, blank=True)
    culoare = models.CharField(
        max_length=20,
        default='#0b2545',
        blank=True,
        help_text='Codul HEX al culorii (ex: #0b2545) folosit pentru eticheta categoriei.'
    )
    sigla = models.CharField(
        max_length=100,
        help_text='Clasa FontAwesome (ex: fa-solid fa-person-skiing) sau calea catre iconita.'
    )
    nivel_recomandat = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='intermediar'
    )

    class Meta:
        ordering = ['nume']
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categorii'

    def __str__(self):
        return f"{self.nume} ({self.get_nivel_recomandat_display()})"


class Brand(models.Model):
    nume = models.CharField(
        max_length=60,
        unique=True,
        error_messages={
            'unique': 'Acest brand este deja inregistrat in baza de date.',
            'max_length': 'Numele brandului nu poate depasi 60 de caractere.'
        }
    )
    tara_origine = models.CharField(max_length=50)
    an_infiintare = models.PositiveIntegerField()
    website = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['nume']
        verbose_name = 'Brand'
        verbose_name_plural = 'Branduri'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(an_infiintare__gte=1850) & models.Q(an_infiintare__lte=2026),
                name='brand_an_infiintare_valid'
            )
        ]

    def __str__(self):
        return f"{self.nume} ({self.tara_origine})"


class ServiciuAditional(models.Model):
    nume_serviciu = models.CharField(
        max_length=80,
        unique=True,
        error_messages={
            'unique': 'Acest serviciu de atelier exista deja.',
            'max_length': 'Numele serviciului nu poate depasi 80 de caractere.'
        }
    )
    pret_serviciu = models.DecimalField(max_digits=6, decimal_places=2)
    durata_minute = models.PositiveIntegerField(
        default=30,
        blank=True,
        help_text='Durata medie in minute necesara in atelier pentru aceasta operatiune.'
    )
    detalii_tehnice = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Serviciu Aditional'
        verbose_name_plural = 'Servicii Aditionale'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pret_serviciu__gt=0) & models.Q(durata_minute__gte=10),
                name='serviciu_pret_si_durata_valide'
            )
        ]

    def __str__(self):
        return f"{self.nume_serviciu} - {self.pret_serviciu} RON"


class Schi(models.Model):
    PROFIL_CHOICES = [
        ('camber', 'Camber'),
        ('rocker', 'Rocker'),
        ('hybrid', 'Hybrid (Camber + Rocker)'),
    ]

    nume_model = models.CharField(max_length=100, db_index=True)
    cod_model = models.CharField(
        max_length=30,
        unique=True,
        error_messages={
            'unique': 'Codul de model (SKU) trebuie sa fie unic pentru fiecare schi.',
            'max_length': 'Codul modelului nu poate depasi 30 de caractere.'
        }
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text='Identificator URL unic (doar litere mici, cifre si cratime).',
        error_messages={
            'unique': 'Acest slug URL este deja folosit de un alt model de schi.',
            'invalid': 'Slug-ul poate contine doar litere, cifre, underscore sau cratime.'
        }
    )
    pret = models.DecimalField(max_digits=8, decimal_places=2, db_index=True)
    lungime_cm = models.PositiveIntegerField(db_index=True)
    raza_viraj = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Raza de viraj in metri (ex: 13.5 pentru viraje scurte de slalom).'
    )
    include_legaturi = models.BooleanField(default=False)
    profil = models.CharField(max_length=20, choices=PROFIL_CHOICES, default='hybrid')
    stoc = models.IntegerField(default=1, blank=True)
    temperaturi_optime = ArrayField(
        models.IntegerField(),
        size=2,
        help_text='Doua valori intregi separate prin virgula (ex: -15, -2) reprezentand intervalul in C.'
    )
    imagine = models.ImageField(upload_to='schiuri/', null=True, blank=True)
    data_adaugare = models.DateTimeField(default=timezone.now)

    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='schiuri')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='schiuri')
    servicii_compatibile = models.ManyToManyField(ServiciuAditional, blank=True, related_name='schiuri')

    class Meta:
        ordering = ['-data_adaugare', 'pret']
        verbose_name = 'Schi'
        verbose_name_plural = 'Schiuri'
        indexes = [
            models.Index(fields=['nume_model'], name='idx_schi_nume'),
            models.Index(fields=['pret'], name='idx_schi_pret'),
            models.Index(fields=['lungime_cm'], name='idx_schi_lungime'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pret__gt=0),
                name='schi_pret_pozitiv'
            ),
            models.CheckConstraint(
                condition=models.Q(lungime_cm__gte=80) & models.Q(lungime_cm__lte=220),
                name='schi_lungime_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(stoc__gte=0),
                name='schi_stoc_nenegativ'
            ),
        ]

    def __str__(self):
        return f"{self.brand.nume} {self.nume_model} ({self.lungime_cm} cm) - {self.pret} RON"


class SediuCompanie(models.Model):
    oras = models.CharField(max_length=50, db_index=True)
    adresa = models.CharField(max_length=150)
    telefon = models.CharField(max_length=20)
    email_sediu = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        error_messages={
            'unique': 'Acest email este deja asociat unui alt sediu Skiio.',
            'invalid': 'Introduceti o adresa de email valida (ex: brasov@skiio.ro).'
        }
    )

    class Meta:
        ordering = ['oras']
        verbose_name = 'Sediu Companie'
        verbose_name_plural = 'Sedii Companie'
        indexes = [
            models.Index(fields=['oras'], name='idx_sediu_oras'),
        ]

    def __str__(self):
        return f"Sediu Skiio {self.oras} ({self.adresa})"


class Raion(models.Model):
    sediu = models.ForeignKey(SediuCompanie, on_delete=models.CASCADE, related_name='raioane')
    nume_raion = models.CharField(max_length=60)
    etaj = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name = 'Raion'
        verbose_name_plural = 'Raioane'

    def __str__(self):
        return f"Raion {self.nume_raion} (Etaj {self.etaj}) - {self.sediu.oras}"