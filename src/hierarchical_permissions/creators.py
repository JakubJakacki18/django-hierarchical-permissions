import logging
from collections.abc import Iterable
from typing import Any, Callable, Optional, Protocol
import rules
from django.contrib.auth.models import User, Permission

from .conf import (
    PERMISSION_TYPES_LABELS,
    Action,
    PermissionType,
)
from .utils import (
    action_values_to_list,
)
from django.contrib.contenttypes.models import ContentType


def create_crud_permissions_by_type(
    model_name: str, permission_type: PermissionType, description: str = None
) -> list:
    if permission_type not in PERMISSION_TYPES_LABELS.keys() and description is None:
        raise KeyError(
            f"Key {permission_type} doesn't exist in PERMISSION_TYPES_LABELS and description is None."
        )
    if permission_type == PermissionType.FIELD:
        raise TypeError(
            "Argument 'permission_type' cannot be 'PermissionType.FIELD'. Use 'create_fields_permissions' method."
        )
    permissions_list = []
    action_values = action_values_to_list(*list(Action))
    for action_value in action_values:
        permissions_list.append(
            tuple(
                (
                    f"{permission_type.value}_{action_value}_{model_name}",
                    (
                        PERMISSION_TYPES_LABELS[permission_type](
                            action_value, model_name
                        )
                        if description is None
                        else f"Can {action_value} {model_name} {description}"
                    ),
                )
            )
        )
    return permissions_list


# TODO przemyśleć czy uprawnienia typu fields nie powinny być bardziej dynamiczne
#  czy powinny przyjmować akcje inne niż view/change
def create_fields_permissions(model) -> list:
    if PermissionType.FIELD not in PERMISSION_TYPES_LABELS.keys():
        raise KeyError(
            "Key 'PermissionType.FIELD' doesn't exist in PERMISSION_TYPES_LABELS"
        )
    model_name = model.__name__.lower()
    fields = [field.name for field in model._meta.get_fields()]
    permissions_list = []
    action_values = action_values_to_list(Action.VIEW, Action.CHANGE)
    for action_value in action_values:
        for field in fields:
            permissions_list.append(
                tuple(
                    (
                        f"{PermissionType.FIELD.value}_{field}_{action_value}_{model_name}",
                        PERMISSION_TYPES_LABELS[PermissionType.FIELD](
                            action_value, model_name, field
                        ),
                    )
                )
            )
    return permissions_list
