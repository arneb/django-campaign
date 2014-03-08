# encoding: utf8
from django.db import models, migrations
import django.utils.timezone
import campaign.fields


class Migration(migrations.Migration):

    dependencies = [
        (u'contenttypes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistEntry',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                u'ordering': ('-added',),
                u'verbose_name': u'blacklist entry',
                u'verbose_name_plural': u'blacklist entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=u'Name')),
                ('plain', models.TextField(verbose_name=u'Plaintext Body')),
                ('html', models.TextField(null=True, verbose_name=u'HTML Body', blank=True)),
                ('subject', models.CharField(max_length=255, verbose_name=u'Subject')),
            ],
            options={
                u'ordering': ('name',),
                u'verbose_name': u'mail template',
                u'verbose_name_plural': u'mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=u'Name')),
                ('description', models.TextField(null=True, verbose_name=u'Description', blank=True)),
            ],
            options={
                u'ordering': ('name',),
                u'verbose_name': u'newsletter',
                u'verbose_name_plural': u'newsletters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BounceEntry',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=255, null=True, verbose_name=u'recipient', blank=True)),
                ('exception', models.TextField(null=True, verbose_name=u'exception', blank=True)),
            ],
            options={
                u'ordering': ('email',),
                u'verbose_name': u'bounce entry',
                u'verbose_name_plural': u'bounce entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriberList',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=u'Name')),
                ('content_type', models.ForeignKey(to=u'contenttypes.ContentType', to_field=u'id')),
                ('filter_condition', campaign.fields.JSONField(default='{}', help_text=u'Django ORM compatible lookup kwargs which are used to get the list of objects.')),
                ('email_field_name', models.CharField(help_text=u'Name of the model field which stores the recipients email address', max_length=64, verbose_name=u'Email-Field name')),
            ],
            options={
                u'ordering': ('name',),
                u'verbose_name': u'subscriber list',
                u'verbose_name_plural': u'subscriber lists',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=u'Name')),
                ('newsletter', models.ForeignKey(verbose_name=u'Newsletter', to_field=u'id', blank=True, to='campaign.Newsletter', null=True)),
                ('template', models.ForeignKey(to='campaign.MailTemplate', to_field=u'id', verbose_name=u'Template')),
                ('sent', models.BooleanField(default=False, verbose_name=u'sent out', editable=False)),
                ('sent_at', models.DateTimeField(null=True, verbose_name=u'sent at', blank=True)),
                ('online', models.BooleanField(default=True, help_text=u'make a copy available online', verbose_name=u'available online')),
                ('recipients', models.ManyToManyField(to='campaign.SubscriberList', verbose_name=u'Subscriber lists')),
            ],
            options={
                u'ordering': ('name', 'sent'),
                u'verbose_name': u'campaign',
                u'verbose_name_plural': u'campaigns',
            },
            bases=(models.Model,),
        ),
    ]
