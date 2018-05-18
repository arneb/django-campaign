# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import campaign.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'ordering': ('-added',),
                'verbose_name': 'blacklist entry',
                'verbose_name_plural': 'blacklist entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('plain', models.TextField(verbose_name='Plaintext Body')),
                ('html', models.TextField(null=True, verbose_name='HTML Body', blank=True)),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'mail template',
                'verbose_name_plural': 'mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'newsletter',
                'verbose_name_plural': 'newsletters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BounceEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=255, null=True, verbose_name='recipient', blank=True)),
                ('exception', models.TextField(null=True, verbose_name='exception', blank=True)),
            ],
            options={
                'ordering': ('email',),
                'verbose_name': 'bounce entry',
                'verbose_name_plural': 'bounce entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriberList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', to_field='id')),
                ('filter_condition', campaign.fields.JSONField(default='{}', help_text='Django ORM compatible lookup kwargs which are used to get the list of objects.')),
                ('email_field_name', models.CharField(help_text='Name of the model field which stores the recipients email address', max_length=64, verbose_name='Email-Field name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'subscriber list',
                'verbose_name_plural': 'subscriber lists',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('newsletter', models.ForeignKey(verbose_name='Newsletter', to_field='id', blank=True, to='campaign.Newsletter', null=True)),
                ('template', models.ForeignKey(to='campaign.MailTemplate', to_field='id', verbose_name='Template')),
                ('sent', models.BooleanField(default=False, verbose_name='sent out', editable=False)),
                ('sent_at', models.DateTimeField(null=True, verbose_name='sent at', blank=True)),
                ('online', models.BooleanField(default=True, help_text='make a copy available online', verbose_name='available online')),
                ('recipients', models.ManyToManyField(to='campaign.SubscriberList', verbose_name='Subscriber lists')),
            ],
            options={
                'ordering': ('name', 'sent'),
                'verbose_name': 'campaign',
                'verbose_name_plural': 'campaigns',
            },
            bases=(models.Model,),
        ),
    ]
