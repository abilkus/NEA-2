# Generated by Django 3.0.3 on 2020-02-17 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_20200217_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musicinstancereservation',
            name='duedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='musicinstancereservation',
            name='returneddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='musicinstancereservation',
            name='takenoutdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
