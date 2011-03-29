from django.conf import settings
from django.db.models import get_model

DEFAULT_SETTINGS = {
    'MULTIPLE_SITES': False,
    'USER_MODEL': 'auth.User',
    'URL_MONTH_FORMAT': r'%b',
}

DEFAULT_SETTINGS.update(getattr(settings, GEOPOLL_SETTINGS, {}))

MULTIPLE_SITES = DEFAULT_SETTINGS['MULTIPLE_SITES']
USER_MODEL = get_model(DEFAULT_SETTINGS['USER_MODEL'])
MONTH_FORMAT = DEFAULT_SETTINGS['URL_MONTH_FORMAT']