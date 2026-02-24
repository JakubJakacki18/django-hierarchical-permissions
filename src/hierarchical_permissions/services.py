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
    actions_to_list,
)
from django.contrib.contenttypes.models import ContentType


class PermissionCreationService:
    # TODO Poprawić opisy klas/funkcji!
    """Permission Creation Service is used to create codenames and assign rules to permission"""

    @staticmethod
    def create_crud_permissions_by_type(
        model_name: str, permission_type: PermissionType, description: str = None
    ) -> list:
        if (
            permission_type not in PERMISSION_TYPES_LABELS.keys()
            and description is None
        ):
            raise KeyError(
                f"Key {permission_type} doesn't exist in PERMISSION_TYPES_LABELS and description is None."
            )
        if permission_type == PermissionType.FIELD:
            raise TypeError(
                "Argument 'permission_type' cannot be 'PermissionType.FIELD'. Use 'create_fields_permissions' method."
            )
        permissions_list = []
        action_values = actions_to_list(
            Action.ADD,
            Action.VIEW,
            Action.CHANGE,
            Action.DELETE,
        )
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

    @staticmethod
    def create_fields_permissions(model) -> list:
        if PermissionType.FIELD not in PERMISSION_TYPES_LABELS.keys():
            raise KeyError(
                "Key 'PermissionType.FIELD' doesn't exist in PERMISSION_TYPES_LABELS"
            )
        model_name = model.__name__.lower()
        fields = [field.name for field in model._meta.get_fields()]
        permissions_list = []
        action_values = actions_to_list(Action.VIEW, Action.CHANGE)
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

    @staticmethod
    def add_rule_to_permission(
        app_name: str, codename: str, description: str, rule: Callable
    ):
        rules.add_rule(
            f"{app_name}.{codename}",
            rule,
        )
        return codename, description

    @staticmethod
    def add_rules_to_permissions(
        app_name: str,
        codenames_with_descriptions: list[tuple[str, str]],
        rules_to_assign: list[Callable],
    ) -> list[tuple[str, str]]:

        if (
            len(rules_to_assign) != len(codenames_with_descriptions)
            and len(rules_to_assign) != 1
        ):
            raise ValueError(
                "Count of rules and permissions must be the same or rules must be 1"
            )
        permissions_list = []
        for i, (codename, description) in enumerate(codenames_with_descriptions):
            if len(rules_to_assign) == 1:
                rule = rules_to_assign[0]
            else:
                rule = rules_to_assign[i]
            permissions_list.append(
                PermissionCreationService.add_rule_to_permission(
                    app_name, codename, description, rule
                )
            )
        return permissions_list

    @staticmethod
    def add_permissions_to_permissions_groups(
        group_permissions: dict[str, list[dict[str, Any]]],
    ):
        """
        Method to add permissions to groups.
        This method should be called after creating permissions.

        Args:
        group_permissions (dict): A dictionary where keys are role names (str) and values are lists of dictionaries.
                      Each dictionary must contain:
                      - "model": A model class (e.g., Product).
                      - "codenames": A list of permission codenames (list[str]).
        """
        from django.contrib.auth.models import Group

        # Validation of group_permissions structure should be done.
        for group_name, permissions_list in group_permissions.items():
            group, _ = Group.objects.get_or_create(name=group_name)

            for perm_info in permissions_list:
                content_type = ContentType.objects.get_for_model(perm_info["model"])
                for codename in perm_info["codenames"]:
                    permission = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    group.permissions.add(permission)
