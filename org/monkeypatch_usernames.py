USERNAME_LENGTH = 128

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

User._meta.get_field('username').max_length = USERNAME_LENGTH
User._meta.get_field('username').validators[0].limit_value = USERNAME_LENGTH
UserAdmin.form.base_fields['username'].max_length = USERNAME_LENGTH
UserAdmin.form.base_fields['username'].validators[0].limit_value = USERNAME_LENGTH