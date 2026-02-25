import logging
from collections.abc import Iterable
from typing import Any, Callable, Optional, Protocol
import rules
from django.contrib.auth.models import User, Permission
from django.db.models import QuerySet

from .conf import (
    PERMISSION_TYPES_LABELS,
    Action,
    PermissionType,
)
from .defaults import PermissionStrategy
from .selectors import (
    get_all_permissions_for_model,
    check_user_has_permission,
    get_permissions_from_user_groups,
    get_hierarchy_of_organizational_units,
)
from .strategies import (
    PermissionCheckerStrategy,
    RegularPermissionCheckerStrategy,
    ObjectPermissionCheckerStrategy,
    HardcodedPermissionCheckerStrategy,
)
from .utils import (
    permissions_divider,
)
from .models import UserGroup, OrganizationalUnit
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


class PermissionChecker:
    """Class responsible for checking permissions."""

    # TODO Przeanalizować pod kątem optymalizacji, rozważyć cache/inny czas życia
    def __init__(self, user: User):
        self.user = user
        self.permissions_checker_functions: dict[
            PermissionStrategy, PermissionCheckerStrategy
        ] = {
            PermissionStrategy.MODEL: RegularPermissionCheckerStrategy,
            PermissionStrategy.OBJECT: ObjectPermissionCheckerStrategy,
            PermissionStrategy.HARDCODED: HardcodedPermissionCheckerStrategy,
        }

    @staticmethod
    def _is_permission_in_user_groups(
        permission: str, user_groups: QuerySet[UserGroup]
    ) -> bool:
        """
        Check if permission is in any of user groups.

        Args:
            permission (str): Permission codename in format 'app_label.codename'.
            user_groups (QuerySet): UserGroups queryset.

        Returns:
            bool: True if user has permission, False otherwise.
        """
        permissions_in_user_groups = get_permissions_from_user_groups(user_groups)
        return permission in permissions_in_user_groups

    def _model_level_has_permission(self, permission) -> bool:
        """Check if user has permission in any of his user groups."""
        # return self._repository.check_user_has_permission(permission, self.user_groups)
        return check_user_has_permission(self.user, permission)

    def _object_level_has_permission(self, permission, obj) -> bool:
        """Check if user has permission in any of his user groups in scope of organizational units"""
        hierarchy_of_organizational_units = get_hierarchy_of_organizational_units(obj)
        return check_user_has_permission(
            self.user, permission, hierarchy_of_organizational_units
        )

    def has_permission(self, permission, obj=None) -> bool:
        if obj is not None and (not hasattr(obj, "parent") or not obj.parent):
            raise AttributeError(
                f"{obj.__class__.__module__}.{obj.__class__.__name__} doesn't have parent attribute or parent is null."
            )
        return (
            self._object_level_has_permission(permission, obj)
            if obj is not None
            else self._model_level_has_permission(permission)
        )

    def has_perm_to_action(self, model, action: Action, obj=None) -> bool:
        # print("------------------------------------\n")
        # print("Model", model)
        # print("Obj", obj)
        # print("Action", action)
        # print("------------------------------------\n")
        all_permissions_for_model = get_all_permissions_for_model(model, False, action)
        return self.has_perm_by_permissions_codenames(obj, *all_permissions_for_model)

    def has_perm_by_permissions_codenames(self, obj, *permissions) -> bool:
        if self.user.is_superuser:
            return True
        permissions_divider_by_strategy = permissions_divider(*permissions)

        for (
            permission_strategy,
            permission_checker_function,
        ) in self.permissions_checker_functions.items():
            if (
                permissions := permissions_divider_by_strategy.get(
                    permission_strategy.value
                )
            ) and permission_checker_function.check(permissions, obj, self):
                logger.debug("PermissionStrategy: %s", permission_strategy.value)
                return True
        return False

    def has_field_permission_checker(self, model, field_name, obj=None):
        # TODO Walidacja field_name do napisania
        content_type = ContentType.objects.get_for_model(model)
        view_permission, change_permission = (
            self.has_perm_by_permissions_codenames(
                obj,
                f"{content_type.app_label}.{PermissionType.FIELD.value}_{field_name}_{action.value}_{model.__name__.lower()}",
            )
            for action in (Action.VIEW, Action.CHANGE)
        )

        return view_permission, change_permission
