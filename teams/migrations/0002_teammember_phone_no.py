# Generated by Django 4.0.4 on 2022-08-16 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='phone_no',
            field=models.CharField(default='', max_length=10, unique=True),
            preserve_default=False,
        ),
    ]
