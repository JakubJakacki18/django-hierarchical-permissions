import pytest
from django.contrib.auth.models import Group

from hierarchical_permissions.conf import Action
from hierarchical_permissions.models import UserGroup
from hierarchical_permissions.services import (
    PermissionService,
    PermissionCreationService,
    DjangoPermissionRepository,
)
from test_model_app.models import FakeModel

# test_*ACTION*_permission_for_fakemodel_when_user_in_group_is_granted is broken down for readability


@pytest.fixture
def permission_groups(db, permissions_codenames):
    _permission_groups = {
        "Teacher": [
            {"model": FakeModel, "codenames": ["view_fakemodel"]},
        ],
        "Leading teacher": [
            {
                "model": FakeModel,
                "codenames": [
                    "view_fakemodel",
                    "change_fakemodel",
                ],
            },
        ],
        "Mesh administrator": [
            {
                "model": FakeModel,
                "codenames": [
                    "view_fakemodel",
                    "change_fakemodel",
                    "delete_fakemodel",
                ],
            },
        ],
    }
    PermissionCreationService.add_permissions_to_permissions_groups(_permission_groups)
    return {
        "teacher": Group.objects.get(name="Teacher"),
        "leading_teacher": Group.objects.get(name="Leading teacher"),
        "mesh_admin": Group.objects.get(name="Mesh administrator"),
    }


@pytest.mark.parametrize(
    "person,has_permission",
    [
        ("teacher_janek", True),
        ("teacher_franek", True),
        ("teacher_piotrek", True),
        ("adm_maciek", True),
        ("admin", True),
    ],
)
def test_view_permission_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert ps.has_perm_to_action(FakeModel, Action.VIEW) is has_permission


@pytest.mark.parametrize(
    "person,has_permission",
    [
        ("teacher_janek", True),
        ("teacher_franek", False),
        ("teacher_piotrek", False),
        ("adm_maciek", True),
        ("admin", True),
    ],
)
def test_change_permission_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert ps.has_perm_to_action(FakeModel, Action.CHANGE) is has_permission


@pytest.mark.parametrize(
    "person,has_permission",
    [
        ("teacher_janek", False),
        ("teacher_franek", False),
        ("teacher_piotrek", False),
        ("adm_maciek", True),
        ("admin", True),
    ],
)
def test_delete_permission_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert ps.has_perm_to_action(FakeModel, Action.DELETE) is has_permission


@pytest.mark.parametrize(
    "person,has_permission",
    [
        ("teacher_janek", False),
        ("teacher_franek", False),
        ("teacher_piotrek", False),
        ("adm_maciek", False),
        ("admin", True),
    ],
)
def test_add_permission_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert ps.has_perm_to_action(FakeModel, Action.ADD) is has_permission
