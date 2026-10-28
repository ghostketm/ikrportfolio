from .models import About

def about_context(request):
    """
    Global context processor to make the singleton About object
    available across all templates, including system error pages (400, 403, 404, 500).
    """
    try:
        return {'about': About.objects.first()}
    except Exception:
        return {'about': None}
