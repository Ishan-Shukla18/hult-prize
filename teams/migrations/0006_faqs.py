# Generated by Django 4.0.4 on 2022-12-04 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_alter_teammember_email_alter_teammember_phone_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=200)),
                ('answer', models.CharField(max_length=400)),
            ],
        ),
    ]