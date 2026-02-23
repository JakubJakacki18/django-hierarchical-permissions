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
    "person,action,has_permission",
    [
        ("teacher_janek", Action.VIEW, True),
        ("teacher_franek", Action.VIEW, True),
        ("teacher_piotrek", Action.VIEW, True),
        ("adm_maciek", Action.VIEW, True),
        ("admin", Action.VIEW, True),
        ("teacher_janek", Action.CHANGE, True),
        ("teacher_franek", Action.CHANGE, False),
        ("teacher_piotrek", Action.CHANGE, False),
        ("adm_maciek", Action.CHANGE, True),
        ("admin", Action.CHANGE, True),
        ("teacher_janek", Action.DELETE, False),
        ("teacher_franek", Action.DELETE, False),
        ("teacher_piotrek", Action.DELETE, False),
        ("adm_maciek", Action.DELETE, True),
        ("admin", Action.DELETE, True),
        ("teacher_janek", Action.ADD, False),
        ("teacher_franek", Action.ADD, False),
        ("teacher_piotrek", Action.ADD, False),
        ("adm_maciek", Action.ADD, False),
        ("admin", Action.ADD, True),
        ("teacher_janek", Action.EXPORT, False),
        ("teacher_franek", Action.EXPORT, False),
        ("teacher_piotrek", Action.EXPORT, False),
        ("adm_maciek", Action.EXPORT, True),
        ("admin", Action.EXPORT, True),
    ],
)
def test_has_perm_to_action_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, has_permission, action
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert ps.has_perm_to_action(FakeModel, action) is has_permission


@pytest.mark.parametrize(
    "person,permission_codenames,has_permission",
    [
        (
            "teacher_janek",
            ("test_model_app.view_fakemodel",),
            True,
        ),
        ("teacher_franek", ("test_model_app.view_fakemodel",), True),
        ("teacher_piotrek", ("test_model_app.view_fakemodel",), True),
        ("adm_maciek", ("test_model_app.view_fakemodel",), True),
        ("admin", ("test_model_app.view_fakemodel",), True),
        ("teacher_janek", ("test_model_app.change_fakemodel",), True),
        ("teacher_franek", ("test_model_app.change_fakemodel",), False),
        ("teacher_piotrek", ("test_model_app.change_fakemodel",), False),
        ("adm_maciek", ("test_model_app.change_fakemodel",), True),
        ("admin", ("test_model_app.change_fakemodel",), True),
        ("teacher_janek", ("test_model_app.delete_fakemodel",), False),
        ("teacher_franek", ("test_model_app.delete_fakemodel",), False),
        ("teacher_piotrek", ("test_model_app.delete_fakemodel",), False),
        ("adm_maciek", ("test_model_app.delete_fakemodel",), True),
        ("admin", ("test_model_app.delete_fakemodel",), True),
        ("teacher_janek", ("test_model_app.add_fakemodel",), False),
        ("teacher_franek", ("test_model_app.add_fakemodel",), False),
        ("teacher_piotrek", ("test_model_app.add_fakemodel",), False),
        ("adm_maciek", ("test_model_app.add_fakemodel",), False),
        ("admin", ("test_model_app.add_fakemodel",), True),
    ],
)
def test_has_perm_by_permissions_for_fakemodel_when_user_in_group_is_granted(
    users, user_groups, person, permission_codenames, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert (
        ps.has_perm_by_permissions_codenames(None, *permission_codenames)
        is has_permission
    )


# def test_has_perm_checker_for_fakemodel_and_custom_action_when_user_in_group_is_granted(
#     users, user_groups, person, permission_codenames, has_permission
# ):
#     pass
