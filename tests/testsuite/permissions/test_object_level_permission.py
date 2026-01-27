import pytest

from hierarchical_permissions.conf import Action
from hierarchical_permissions.services import PermissionService
from test_model_app.models import FakeModel


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
        ("teacher_franek", "csharp", False),
        ("teacher_piotrek", "csharp", False),
        ("teacher_janek", "linux", False),
        ("teacher_franek", "linux", False),
        ("teacher_piotrek", "linux", False),
        ("teacher_janek", "algebra", False),
        ("teacher_franek", "algebra", False),
        ("teacher_piotrek", "algebra", False),
    ],
)
def test_permission_for_fakemodel_when_rule_is_fulfilled_and_user_in_group_is_granted(
    users, user_groups, fake_model_objects, person, object_name, has_permission
):
    ps = PermissionService(users[person])
    assert (
        ps.has_perm_to_action(FakeModel, Action.DELETE, fake_model_objects[object_name])
        is has_permission
    )
