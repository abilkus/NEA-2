# Generated by Django 2.1.5 on 2019-12-01 14:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20191201_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicinstancereservation',
            name='duedate',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]