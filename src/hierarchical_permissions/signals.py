from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .conf import Action
from .defaults import ACTION


def add_custom_action_to_default_django_permissions(sender, **kwargs):
    for model in sender.get_models():
        content_type = ContentType.objects.get_for_model(model)
        all_action_values = {action.value for action in Action}
        custom_action_values = all_action_values - set(ACTION.values())
        for action_value in custom_action_values:
            codename = f"{action_value}_{model._meta.model_name}"
            name = f"Can {action_value} {model._meta.verbose_name}"
            Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={"name": name[:255]},
            )
