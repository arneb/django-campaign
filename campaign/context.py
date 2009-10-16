# heavily based on Django's RequestContext
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Context

_mail_context_processors = None

# This is a function rather than module-level procedural code because we only
# want it to execute if somebody uses MailContext.
def get_mail_processors():
    global _mail_context_processors
    if _mail_context_processors is None:
        processors = []
        for path in getattr(settings, 'CAMPAIGN_CONTEXT_PROCESSORS', ()):
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, {}, {}, [attr])
            except ImportError, e:
                raise ImproperlyConfigured('Error importing campaign processor module %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" callable campaign processor' % (module, attr))
            processors.append(func)
        _mail_context_processors = tuple(processors)
    return _mail_context_processors
    
class MailContext(Context):
    """
    This subclass of template.Context automatically populates itself using
    the processors defined in CAMPAIGN_CONTEXT_PROCESSORS.
    Additional processors can be specified as a list of callables
    using the "processors" keyword argument.
    """
    def __init__(self, subscriber, dict=None, processors=None):
        Context.__init__(self, dict)
        if processors is None:
            processors = ()
        else:
            processors = tuple(processors)
        for processor in get_mail_processors() + processors:
            self.update(processor(subscriber))
        self.update({'recipient': subscriber})
