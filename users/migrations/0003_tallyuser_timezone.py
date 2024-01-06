# Generated by Django 5.0.1 on 2024-01-05 12:12

import timezone_field.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_tallyuser_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='tallyuser',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='Africa/Lagos', verbose_name='user timezone'),
        ),
    ]
