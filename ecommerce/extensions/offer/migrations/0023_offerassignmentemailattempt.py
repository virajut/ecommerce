# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-20 10:03
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0022_offerassignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferAssignmentEmailAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_id', models.CharField(max_length=255, unique=True)),
                ('offer_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offer.OfferAssignment')),
            ],
        ),
    ]
