from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CampaignConfig(AppConfig):
    name = 'campaign'
    verbose_name = _("campaign management")
    default_auto_field = 'django.db.models.AutoField'
