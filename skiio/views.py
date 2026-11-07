from django.shortcuts import render
from django.http import Http404, HttpResponse
from datetime import datetime
from collections import Counter

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

    def dictionar_proprietati(self):
        return {
            "id": self.id,
            "ip_client": self.ip_client,
            "url": self.string_url(),
            "pagina": self.pagina(),
            "data": self.calculeaza_data(tip_afisare="str_simplu"),
            "parametri": self.lista_parametri()
        }

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
    return render(request, "skiio/index.html")

def info(request):
    accesare = inregistreaza_accesare(request)
    optiune_data = request.GET.get("data", "")
    sectiune_html = accesare.calculeaza_data(tip_afisare=optiune_data)
    return render(request, "skiio/info.html", {"sectiune_data_html": sectiune_html})

def despre(request):
    inregistreaza_accesare(request)
    return render(request, "skiio/despre.html")

def istoric(request):
    inregistreaza_accesare(request)
    return render(request, "skiio/istoric.html")

def in_lucru(request):
    inregistreaza_accesare(request)
    return render(request, "skiio/in_lucru.html")

def log_view(request):
    inregistreaza_accesare(request)
    lista_afisare = list(ISTORIC_ACCESARI)
    eroare = None

    nume_parametri = list(request.GET.keys())
    nr_parametri = len(nume_parametri)

    lista_iduri_raw = request.GET.getlist("iduri")
    accepta_dubluri = request.GET.get("dubluri", "false").lower() == "true"

    if lista_iduri_raw:
        iduri_extrase = []
        for grup in lista_iduri_raw:
            for elem in grup.split(","):
                elem = elem.strip()
                if elem.isdigit():
                    id_int = int(elem)
                    if accepta_dubluri or id_int not in iduri_extrase:
                        iduri_extrase.append(id_int)
        mapare_id = {acc.id: acc for acc in ISTORIC_ACCESARI}
        lista_afisare = [mapare_id[i] for i in iduri_extrase if i in mapare_id]

    param_ultimele = request.GET.get("ultimele")
    if param_ultimele is not None:
        try:
            n = int(param_ultimele)
            if n < 0:
                raise ValueError()
            k = len(lista_afisare)
            if n > k:
                eroare = f"Exista doar {k} accesari fata de {n} accesari cerute"
            else:
                lista_afisare = lista_afisare[-n:] if n > 0 else []
        except ValueError:
            eroare = "Eroare: parametrul 'ultimele' trebuie să conțină o valoare numerică întreagă pozitivă!"

    param_accesari = request.GET.get("accesari")
    afiseaza_nr_total = (param_accesari == "nr")
    afiseaza_detalii_data = (param_accesari == "detalii")

    param_tabel = request.GET.get("tabel")
    coloane_tabel = []
    randuri_tabel = []
    if param_tabel:
        toate_coloanele = ["id", "ip_client", "url", "pagina", "data", "parametri"]
        if param_tabel == "tot":
            coloane_tabel = toate_coloanele
        else:
            coloane_tabel = [c.strip() for c in param_tabel.split(",") if c.strip() in toate_coloanele]
        for acc in lista_afisare:
            props = acc.dictionar_proprietati()
            randuri_tabel.append([props[col] for col in coloane_tabel])

    contor_pagini = Counter(acc.pagina() for acc in ISTORIC_ACCESARI)
    pagina_max = contor_pagini.most_common(1)[0][0] if contor_pagini else "-"
    pagina_min = contor_pagini.most_common()[-1][0] if contor_pagini else "-"

    context = {
        "accesari_afisate": lista_afisare,
        "eroare": eroare,
        "nr_parametri": nr_parametri,
        "nume_parametri": nume_parametri,
        "afiseaza_nr_total": afiseaza_nr_total,
        "nr_total_sesiune": len(ISTORIC_ACCESARI),
        "afiseaza_detalii_data": afiseaza_detalii_data,
        "coloane_tabel": coloane_tabel,
        "randuri_tabel": randuri_tabel,
        "pagina_max": pagina_max,
        "pagina_min": pagina_min,
    }
    return render(request, "skiio/log.html", context)

def detalii_accesare(request, id_accesare):
    inregistreaza_accesare(request)
    id_cautat = int(id_accesare)
    accesare_gasita = next((a for a in ISTORIC_ACCESARI if a.id == id_cautat), None)
    if not accesare_gasita:
        raise Http404("Accesarea cerută nu a fost găsită.")
    return render(request, "skiio/detalii_accesare.html", {"accesare": accesare_gasita})                      
