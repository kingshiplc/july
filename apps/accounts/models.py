from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.user)
