# Generated by Django 2.1.5 on 2019-08-07 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0026_auto_20190802_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(help_text="Enter the music's natural language (e.g. English, French, Japanese etc.)", max_length=200),
        ),
    ]
