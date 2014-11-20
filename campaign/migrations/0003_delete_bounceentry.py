# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_blacklistentry_reason'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BounceEntry',
        ),
    ]
