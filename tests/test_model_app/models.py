from django.contrib.auth.models import User
from django.db import models
from hierarchical_permissions.models import BaseModel


class FakeModel(BaseModel):
    name = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        app_label = "test_model_app"
