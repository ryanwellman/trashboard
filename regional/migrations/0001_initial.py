# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table('regional_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('areacode', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('regional', ['Region'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table('regional_region')


    models = {
        'regional.region': {
            'Meta': {'object_name': 'Region'},
            'areacode': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['regional']