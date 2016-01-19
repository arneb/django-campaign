# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0003_delete_bounceentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='from_email',
            field=models.EmailField(max_length=75, null=True, verbose_name='Sending Address', blank=True),
            preserve_default=True,
        ),
    ]
