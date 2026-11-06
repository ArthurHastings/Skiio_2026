from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

ZILE_RO = {
    "Monday": "Luni", "Tuesday": "Marti", "Wednesday": "Miercuri",
    "Thursday": "Joi", "Friday": "Vineri", "Saturday": "Sambata", "Sunday": "Duminica"
}

LUNI_RO = {
    "January": "Ianuarie", "February": "Februarie", "March": "Martie",
    "April": "Aprilie", "May": "Mai", "June": "Iunie",
    "July": "Iulie", "August": "August", "September": "Septembrie",
    "October": "Octombrie", "November": "Noiembrie", "December": "Decembrie"
}


class Accesare:
    contor_id = 0

    def __init__(self, ip_client, url, parametri=None):
        Accesare.contor_id += 1
        self.id = Accesare.contor_id
        self.ip_client = ip_client
        self.url = url
        self.parametri = parametri if parametri is not None else {}
        self.data = datetime.now()

    def lista_parametri(self):
        rezultat = []
        for cheie, valoare in self.parametri.items():
            val = valoare if valoare != "" else None
            rezultat.append((cheie, val))

        return rezultat

    def string_url(self):
        return self.url

    def pagina(self):
        cale_fara_query = self.url.split('?')[0]
        if cale_fara_query.startswith('/skiio'):
            cale_fara_query = cale_fara_query[len('/skiio'):]

        return cale_fara_query if cale_fara_query else "/"

    def traduce_data(self, format_str):
        text_data = self.data.strftime(format_str)
        for en, ro in ZILE_RO.items():
            text_data = text_data.replace(en, ro)
        for en, ro in LUNI_RO.items():
            text_data = text_data.replace(en, ro)

        return text_data

    def calculeaza_data(self, tip_afisare="", format="%A, %d %B %Y"):
        if tip_afisare == "zi":
            text_afisat = self.traduce_data(format)
        elif tip_afisare == "timp":
            text_afisat = self.traduce_data("%H:%M:%S")
        elif tip_afisare == "str_simplu":
            return self.traduce_data(format + " %H:%M:%S")
        else:
            text_afisat = self.traduce_data(format + ", ora %H:%M:%S")

        return f"<section><h2>Data si ora</h2><p>{text_afisat}</p></section>"

    def __str__(self):
        return (
            f"id: {self.id} | "
            f"ip_client: {self.ip_client} | "
            f"string_url: {self.string_url()} | "
            f"pagina: {self.pagina()} | "
            f"calculeaza_data: {self.calculeaza_data(tip_afisare='str_simplu')} | "
            f"lista_parametri: {self.lista_parametri()}"
        )


ISTORIC_ACCESARI = []

def inregistreaza_accesare(request):
    accesare = Accesare(
        ip_client=getattr(request, 'ip_client', 'necunoscut'),
        url=request.get_full_path(),
        parametri=request.GET.dict()
        )
    ISTORIC_ACCESARI.append(accesare)
    print(accesare)
    return accesare

def index(request):
    inregistreaza_accesare(request)
    descriere = ("<h1>Skiio - Magazinul de schiuri</h1>"
        "<p>Bun venit pe Skiio. Aceasta este nu numai cel mai bun magazin de schiuri"
        "din Romania, dar este si un ghid practic pentru a-ti alege modelul potrivit"
        "de clapari si schiuri.</p>"
    )
    return HttpResponse(descriere)

def info(request):
    accesare = inregistreaza_accesare(request)
    optiune_data = request.GET.get("data", "")

    sectiune_data_html = accesare.calculeaza_data(tip_afisare=optiune_data)

    html = f"""
    <!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8">
        <title>Informatii despre server</title>
    </head>
    <body>
        <h1>Informatii despre server</h1>
        {sectiune_data_html}
    </body>
    </html>
    """
    return HttpResponse(html)
