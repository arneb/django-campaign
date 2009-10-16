import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

__all__ = ('backend')

CAMPAIGN_BACKEND = getattr(settings, 'CAMPAIGN_BACKEND', 'send_mail')

def get_backend(import_path):
    if not '.' in import_path:
        import_path = "campaign.backends.%s" % import_path
    try:
        mod = __import__(import_path, {}, {}, [''])
    except ImportError, e_user:
        # No backend found, display an error message and a list of all
        # bundled backends.
        backend_dir = __path__[0]
        available_backends = [f.split('.py')[0] for f in os.listdir(backend_dir) if not f.startswith('_') and not f.startswith('.') and not f.endswith('.pyc')]
        available_backends.sort()
        if CAMPAIGN_BACKEND not in available_backends:
            raise ImproperlyConfigured("%s isn't an available campaign backend. Available options are: %s" % \
                                        (CAMPAIGN_BACKEND, ', '.join(map(repr, available_backends))))
        # if the CAMPAIGN_BACKEND is available in the backend directory
        # and an ImportError is raised, don't suppress it
        else: 
            raise
    try:
        return getattr(mod, 'backend')
    except AttributeError:
        raise ImproperlyConfigured('Backend "%s" does not define a "backend" instance.' % import_path)

backend = get_backend(CAMPAIGN_BACKEND)