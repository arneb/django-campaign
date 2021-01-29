from django.template import Library


register = Library()


@register.filter
def get_field(val, arg):
    return getattr(val, arg)
