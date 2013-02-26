# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Newsletter'
        db.create_table('campaign_newsletter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('campaign', ['Newsletter'])

        # Adding field 'Campaign.newsletter'
        db.add_column('campaign_campaign', 'newsletter',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['campaign.Newsletter'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Newsletter'
        db.delete_table('campaign_newsletter')

        # Deleting field 'Campaign.newsletter'
        db.delete_column('campaign_campaign', 'newsletter_id')


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
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['campaign.Newsletter']", 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['campaign.SubscriberList']", 'symmetrical': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
        'campaign.newsletter': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Newsletter'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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