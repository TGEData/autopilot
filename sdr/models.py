from __future__ import unicode_literals
from django.db import models
import uuid
from io import BytesIO
import six
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
import requests
import json
import sys
from core.utils import ChoiceEnum
from django.views.generic import CreateView, ListView, UpdateView


class EmailProvider(models.Model):
    provider_name =  models.CharField(max_length=100)
    active_status = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return "{0}".format(provider_name)


class CompanyEmailProvider(models.Model):
    user_company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    email_provider =  models.ForeignKey(EmailProvider, on_delete=models.CASCADE)
    provider_creds = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return "{0}: {1}".format(self.user_company, self.email_provider)


class Property(models.Model):
    user_company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    property_identifier = models.UUIDField(default=uuid.uuid4)
    property_name = models.CharField(max_length=255)
    property_sector = models.CharField(max_length=100)
    property_description = models.TextField(null=True, blank=True)
    property_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return "{0}: {1}".format(self.user_company, self.property_name)


class Prospect(models.Model):
    user_company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    prospect_identifier = models.UUIDField(default=uuid.uuid4)
    source_identifier = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    current_title = models.CharField(max_length=255, null=True, blank=True)
    current_company = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return "{0}: {1} {2}".format(self.user_company, self.first_name, self.last_name)


class EmailActivity(models.Model):
    user_company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    email_provider = models.ForeignKey(CompanyEmailProvider, on_delete=models.CASCADE)
    email_send_identifier = models.CharField(max_length=100, null=True, blank=True)
    send_status = models.CharField(max_length=100, null=True, blank=True) #multiple items
    send_status_details = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return "{0}: {1}({2})".format(self.user_company, self.prospect, self.email_status)


class Conversion(models.Model):
    user_company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    conversion_date = models.DateField()
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)

