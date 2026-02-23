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
            {
                "model": FakeModel,
                "codenames": [
                    "staff_view_fakemodel",
                    "superStaff_view_fakemodel",
                    "owner_change_fakemodel",
                ],
            },
        ],
        "Leading teacher": [
            {
                "model": FakeModel,
                "codenames": [
                    "staff_view_fakemodel",
                    "owner_view_fakemodel",
                    "superStaff_view_fakemodel",
                    "staff_change_fakemodel",
                    "owner_delete_fakemodel",
                ],
            },
        ],
        "Mesh administrator": [
            {
                "model": FakeModel,
                "codenames": [
                    "staff_view_fakemodel",
                    "owner_view_fakemodel",
                    "superStaff_view_fakemodel",
                    "superStaff_change_fakemodel",
                    "staff_delete_fakemodel",
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
    "person,object_name,has_permission",
    [
        ("teacher_janek", "physics", False),
        ("teacher_franek", "physics", False),
        ("teacher_piotrek", "physics", False),
        ("adm_maciek", "physics", False),
        (
            "teacher_janek",
            "java",
            True,
        ),  # He is Leading teacher in ug1, and he is owner of java
        ("teacher_franek", "java", False),
        ("teacher_piotrek", "java", False),
        (
            "teacher_janek",
            "csharp",
            True,
        ),  # He is Leading teacher in ug1, and he is owner of csharp
        (
            "adm_maciek",
            "java",
            True,
        ),  # He is Mesh administrator in ug3, and he is member of staff
        ("teacher_franek", "csharp", False),
        ("teacher_piotrek", "csharp", False),
        (
            "adm_maciek",
            "linux",
            True,
        ),  # He is Mesh administrator in ug3, and he is member of staff
        ("teacher_janek", "linux", False),
        ("teacher_franek", "linux", False),
        ("teacher_piotrek", "linux", False),
        (
            "adm_maciek",
            "algebra",
            True,
        ),  # He is Mesh administrator in ug3, and he is member of staff
        ("teacher_janek", "algebra", False),
        ("teacher_franek", "algebra", False),
        ("teacher_piotrek", "algebra", False),
    ],
)
def test_delete_permission_for_fakemodel_when_rule_is_fulfilled_and_user_in_group_is_granted(
    users, user_groups, fake_model_objects, person, object_name, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert (
        ps.has_perm_to_action(FakeModel, Action.DELETE, fake_model_objects[object_name])
        is has_permission
    )


@pytest.mark.parametrize(
    "person,object_name,has_permission",
    [
        ("teacher_janek", "physics", True),  # He is teacher in ug4 and member of staff
        ("teacher_franek", "physics", False),
        (
            "teacher_piotrek",
            "physics",
            True,
        ),  # He is teacher in ug4 and member of staff
        ("adm_maciek", "physics", False),
        (
            "teacher_janek",
            "java",
            True,
        ),  # He is Leading teacher in ug1, and he is owner of java
        (
            "teacher_franek",
            "java",
            False,
        ),  # He is Teacher in ug2, but he isn't member of staff
        ("teacher_piotrek", "java", False),
        (
            "teacher_janek",
            "csharp",
            True,
        ),  # He is Leading teacher in ug1, and he is owner of csharp
        ("adm_maciek", "java", True),
        ("teacher_franek", "csharp", False),
        ("teacher_piotrek", "csharp", False),
        ("adm_maciek", "linux", True),
        ("teacher_janek", "linux", True),
        ("teacher_franek", "linux", False),
        ("teacher_piotrek", "linux", False),
        ("adm_maciek", "algebra", True),
        ("teacher_janek", "algebra", False),
        ("teacher_franek", "algebra", False),
        ("teacher_piotrek", "algebra", False),
    ],
)
def test_view_permission_for_fakemodel_when_rule_is_fulfilled_and_user_in_group_is_granted(
    users, user_groups, fake_model_objects, person, object_name, has_permission
):
    ps = PermissionService(users[person], DjangoPermissionRepository())
    assert (
        ps.has_perm_to_action(FakeModel, Action.VIEW, fake_model_objects[object_name])
        is has_permission
    )
