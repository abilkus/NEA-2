# Generated by Django 3.0.3 on 2020-02-23 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_review_reviewdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='music',
            name='genre',
        ),
        migrations.AddField(
            model_name='music',
            name='genre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Genre'),
        ),
    ]
