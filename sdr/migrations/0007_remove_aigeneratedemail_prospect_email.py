# Generated by Django 4.2.7 on 2023-12-02 01:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sdr', '0006_contacts_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aigeneratedemail',
            name='prospect_email',
        ),
    ]
