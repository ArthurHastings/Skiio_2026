from django.conf import settings

def date_globale(request):
    return {
        "firma": settings.DATE_FIRMA,
        "ip_utilizator": getattr(request, "ip_client", "necunoscut")
    }