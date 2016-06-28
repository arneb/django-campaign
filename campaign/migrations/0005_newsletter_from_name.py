# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0004_newsletter_from_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='from_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Sender Name', blank=True),
            preserve_default=True,
        ),
    ]
