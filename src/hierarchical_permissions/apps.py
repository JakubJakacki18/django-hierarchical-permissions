from django.apps import AppConfig
from django.db.models.signals import post_migrate


class HierarchicalPermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hierarchical_permissions"

    def ready(self):
        from .signals import add_custom_action_to_default_django_permissions

        post_migrate.connect(add_custom_action_to_default_django_permissions)
