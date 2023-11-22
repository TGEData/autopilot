from __future__ import unicode_literals
import uuid
from io import BytesIO
import six
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from core.utils import ChoiceEnum
from django.template.loader import render_to_string
from django.utils import timezone
from .utils import parse_isnan
import json
from django.db import transaction
from datetime import datetime, timedelta
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin
from django.contrib.sites.models import Site



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_identifier = models.UUIDField(default=uuid.uuid4)
    active_status = models.BooleanField(default=False)
    def __str__(self):
        return "{0}: {1}".format(self.user, self.company)

class Company(models.Model):
    company_identifier = models.UUIDField(default=uuid.uuid4)
    company_name = models.CharField(max_length=250)
    company_website = models.URLField(null=True, blank=True)
    active_status = models.BooleanField(default=False)
    userprofile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company_name





