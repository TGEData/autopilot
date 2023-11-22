# Generated by Django 4.2.7 on 2023-11-22 02:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_userprofile_company_company_userprofile'),
        ('sdr', '0003_campaign_aigeneratedemail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aigeneratedemail',
            old_name='campaign_generated_email',
            new_name='campaign_generated_email_template',
        ),
        migrations.RenameField(
            model_name='aigeneratedemail',
            old_name='email_identifier',
            new_name='campaign_identifier',
        ),
        migrations.AddField(
            model_name='aigeneratedemail',
            name='prospect_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='approval_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='campaign',
            name='campaign_identifier',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='campaign',
            name='userprofile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.userprofile'),
        ),
    ]
