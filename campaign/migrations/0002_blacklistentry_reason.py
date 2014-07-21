# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blacklistentry',
            name='reason',
            field=models.TextField(null=True, verbose_name='reason', blank=True),
            preserve_default=True,
        ),
    ]
