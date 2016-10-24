# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0005_newsletter_from_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaign',
            options={'ordering': ('name', 'sent'), 'verbose_name': 'campaign', 'verbose_name_plural': 'campaigns', 'permissions': (('send_campaign', 'Can send campaign'),)},
        ),
    ]
