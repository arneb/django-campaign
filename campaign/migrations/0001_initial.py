# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailTemplate'
        db.create_table('campaign_mailtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('plain', self.gf('django.db.models.fields.TextField')()),
            ('html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('campaign', ['MailTemplate'])

        # Adding model 'SubscriberList'
        db.create_table('campaign_subscriberlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('filter_condition', self.gf('campaign.fields.JSONField')(default='{}')),
            ('email_field_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('campaign', ['SubscriberList'])

        # Adding model 'Campaign'
        db.create_table('campaign_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['campaign.MailTemplate'])),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('online', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('campaign', ['Campaign'])

        # Adding M2M table for field recipients on 'Campaign'
        db.create_table('campaign_campaign_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('campaign', models.ForeignKey(orm['campaign.campaign'], null=False)),
            ('subscriberlist', models.ForeignKey(orm['campaign.subscriberlist'], null=False))
        ))
        db.create_unique('campaign_campaign_recipients', ['campaign_id', 'subscriberlist_id'])

        # Adding model 'BlacklistEntry'
        db.create_table('campaign_blacklistentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('campaign', ['BlacklistEntry'])

        # Adding model 'BounceEntry'
        db.create_table('campaign_bounceentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('exception', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('campaign', ['BounceEntry'])


    def backwards(self, orm):
        # Deleting model 'MailTemplate'
        db.delete_table('campaign_mailtemplate')

        # Deleting model 'SubscriberList'
        db.delete_table('campaign_subscriberlist')

        # Deleting model 'Campaign'
        db.delete_table('campaign_campaign')

        # Removing M2M table for field recipients on 'Campaign'
        db.delete_table('campaign_campaign_recipients')

        # Deleting model 'BlacklistEntry'
        db.delete_table('campaign_blacklistentry')

        # Deleting model 'BounceEntry'
        db.delete_table('campaign_bounceentry')


    models = {
        'campaign.blacklistentry': {
            'Meta': {'ordering': "('-added',)", 'object_name': 'BlacklistEntry'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'campaign.bounceentry': {
            'Meta': {'ordering': "('email',)", 'object_name': 'BounceEntry'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'exception': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'campaign.campaign': {
            'Meta': {'ordering': "('name', 'sent')", 'object_name': 'Campaign'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['campaign.SubscriberList']", 'symmetrical': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['campaign.MailTemplate']"})
        },
        'campaign.mailtemplate': {
            'Meta': {'ordering': "('name',)", 'object_name': 'MailTemplate'},
            'html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'plain': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'campaign.subscriberlist': {
            'Meta': {'ordering': "('name',)", 'object_name': 'SubscriberList'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'email_field_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'filter_condition': ('campaign.fields.JSONField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['campaign']