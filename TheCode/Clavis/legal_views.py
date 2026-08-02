from django.conf import settings
from django.shortcuts import render


def legal_context():
    return {
        "app_name": getattr(settings, "LEGAL_APP_NAME", "The Code ARC"),
        "company_name": getattr(settings, "LEGAL_COMPANY_NAME", "CLAVIS"),
        "contact_email": getattr(settings, "LEGAL_CONTACT_EMAIL", "privacy@clavis.dev"),
        "effective_date": getattr(settings, "LEGAL_EFFECTIVE_DATE", "2026\ub144 1\uc6d4 1\uc77c"),
    }


def terms(request):
    return render(request, "legal/terms.html", legal_context())


def privacy_policy(request):
    return render(request, "legal/privacy_policy.html", legal_context())


def account_deletion(request):
    return render(request, "legal/account_deletion.html", legal_context())
