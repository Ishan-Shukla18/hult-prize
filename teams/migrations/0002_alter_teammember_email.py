# Generated by Django 4.0.4 on 2022-11-08 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]