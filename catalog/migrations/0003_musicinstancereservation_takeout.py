# Generated by Django 2.1.5 on 2019-12-01 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20191125_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicinstancereservation',
            name='takeout',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
