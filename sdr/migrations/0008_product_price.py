# Generated by Django 4.2.7 on 2023-11-29 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sdr', '0007_remove_aigeneratedemail_approval_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
