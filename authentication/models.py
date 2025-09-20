# authentication/models.py
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
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of Birth')
    )
    
    # Add profile picture field
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('Profile Picture')
    )
    
    # Add bio field
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Bio')
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_administrator(self):
        return self.role == self.Role.ADMIN
    
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    def is_viewer(self):
        return self.role == self.Role.VIEWER