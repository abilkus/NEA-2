# Generated by Django 2.1.5 on 2019-07-22 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_auto_20190718_1542'),
    ]

    operations = [
        migrations.RenameField(
            model_name='music',
            old_name='author',
            new_name='composer',
        ),
    ]