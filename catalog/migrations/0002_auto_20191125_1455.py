# Generated by Django 2.1.5 on 2019-11-25 14:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicinstancereservation',
            name='returned',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='musicinstancereservation',
            name='returneddate',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
