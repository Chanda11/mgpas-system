from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        TEACHER = 'TEACHER', _('Teacher')
        VIEWER = 'VIEWER', _('Viewer')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.TEACHER,
        verbose_name=_('User Role')
    )
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"