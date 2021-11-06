from datetime import datetime


def year(request):
    """Возвращает текущий год."""
    return {
        'year': datetime.now().year
    }