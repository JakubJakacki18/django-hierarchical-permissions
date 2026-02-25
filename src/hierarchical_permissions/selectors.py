from collections.abc import Iterable
from typing import Optional, Any

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from hierarchical_permissions.conf import PermissionType
from hierarchical_permissions.models import UserGroup, OrganizationalUnit


def get_content_type_by_model(model: Model) -> ContentType:
    return ContentType.objects.get_for_model(model)


def get_all_permissions_for_model(model, fields_included=False, action=None):
    """Get all permissions for model. Use ``action`` argument to filter all permissions"""
    content_type = get_content_type_by_model(model)
    permissions = Permission.objects.filter(content_type=content_type)
    if action:
        permissions = permissions.filter(codename__contains=action.value)
    if not fields_included:
        permissions = permissions.exclude(
            codename__startswith=PermissionType.FIELD.value
        )
    return [
        f"{content_type.app_label}.{permission.codename}" for permission in permissions
    ]


def get_user_groups(user: User) -> Iterable[UserGroup]:
    return UserGroup.objects.filter(users=user).prefetch_related(
        "permission_groups", "organizational_units"
    )


def get_permissions_from_user_groups(
    user_groups: Iterable[UserGroup],
) -> set[str]:
    permission_groups_set = set()
    for user_group in user_groups:
        permission_groups_set.update(user_group.permission_groups.all())
    permissions_set = set()
    for group in permission_groups_set:
        perms = group.permissions.all()
        formatted_perms = {
            f"{perm.content_type.app_label}.{perm.codename}" for perm in perms
        }
        permissions_set.update(formatted_perms)
    return permissions_set


def check_user_has_permission(
    user: User,
    permission: str,
    organizational_unit: Optional[Iterable[OrganizationalUnit]] = None,
) -> bool:
    app_label, codename = permission.split(".")

    filters: dict[str, Any] = {
        "codename": codename,
        "content_type__app_label": app_label,
        "group__user_groups__users": user,
    }

    if organizational_unit:
        filters["group__user_groups__organizational_units__in"] = organizational_unit
    query = Permission.objects.filter(**filters)
    print(str(query.query))
    return Permission.objects.filter(**filters).exists()


def get_hierarchy_of_organizational_units(
    obj: Any,
) -> Iterable[OrganizationalUnit]:
    parent_organizational_unit = obj.parent
    list_of_organizational_units = parent_organizational_unit.get_ancestors(
        ascending=True
    )
    # In test method get_ancestors() with include_self=True doesn't work
    list_of_organizational_units = [parent_organizational_unit] + list(
        list_of_organizational_units
    )
    return list_of_organizational_units
