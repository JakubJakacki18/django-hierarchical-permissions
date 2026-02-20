import pytest
import rules
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from hierarchical_permissions.conf import PermissionType
from hierarchical_permissions.models import OrganizationalUnit, UserGroup
from hierarchical_permissions.services import PermissionCreationService
from test_model_app.models import FakeModel

from tests.test_model_app.rules import is_owner, is_staff, is_staff_and_owner


@pytest.fixture
def users(db):
    teacher_janek = User.objects.create_user(
        username="t_janek", email="janek@example.com", password="admin", is_staff=True
    )
    teacher_franek = User.objects.create_user(
        username="t_franek", email="franek@example.com", password="admin"
    )
    teacher_piotrek = User.objects.create_user(
        username="t_piotrek",
        email="piotrek@example.com",
        password="admin",
        is_staff=True,
    )
    adm_maciek = User.objects.create_user(
        username="adm_maciek",
        email="maciek@example.com",
        password="admin",
        is_staff=True,
    )
    admin = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="admin",
        is_staff=True,
        is_superuser=True,
    )

    return {
        "teacher_janek": teacher_janek,
        "teacher_franek": teacher_franek,
        "teacher_piotrek": teacher_piotrek,
        "adm_maciek": adm_maciek,
        "admin": admin,
    }


@pytest.fixture
def user_groups(db, users, organizational_units, permission_groups):
    ug1 = UserGroup.objects.create()
    ug1.users.set((users["teacher_janek"],))
    ug1.organizational_units.set(
        (organizational_units["csharp"], organizational_units["java"])
    )
    ug1.permission_groups.set((permission_groups["leading_teacher"],))

    ug2 = UserGroup.objects.create()
    ug2.users.set((users["teacher_franek"], users["teacher_janek"]))
    ug2.organizational_units.set((organizational_units["it_cathedral"],))
    ug2.permission_groups.set((permission_groups["teacher"],))

    ug3 = UserGroup.objects.create()
    ug3.users.set((users["adm_maciek"],))
    ug3.organizational_units.set((organizational_units["it_faculty"],))
    ug3.permission_groups.set((permission_groups["mesh_admin"],))

    ug4 = UserGroup.objects.create()
    ug4.users.set((users["teacher_piotrek"], users["teacher_janek"]))
    ug4.organizational_units.set((organizational_units["physics"],))
    ug4.permission_groups.set((permission_groups["teacher"],))

    return [ug1, ug2, ug3, ug4]


@pytest.fixture
def organizational_units(db):
    root = OrganizationalUnit.objects.create(name="Root Unit", type="ROOT")

    pb = OrganizationalUnit.objects.create(
        name="Bialystok University of Technology",
        parent=root,
        type="UNIVERSITY",
    )

    it_faculty = OrganizationalUnit.objects.create(
        name="IT Faculty", parent=pb, type="FACULTY"
    )
    mech_faculty = OrganizationalUnit.objects.create(
        name="Mechanical Faculty", parent=pb, type="FACULTY"
    )

    it_cathedral = OrganizationalUnit.objects.create(
        name="IT Cathedral", parent=it_faculty, type="CATHEDRAL"
    )
    math_cathedral = OrganizationalUnit.objects.create(
        name="Math Cathedral", parent=it_faculty, type="CATHEDRAL"
    )
    mech_cathedral = OrganizationalUnit.objects.create(
        name="Mechanical Cathedral", parent=mech_faculty, type="CATHEDRAL"
    )
    physics_cathedral = OrganizationalUnit.objects.create(
        name="Physics Cathedral", parent=mech_faculty, type="CATHEDRAL"
    )

    csharp = OrganizationalUnit.objects.create(
        name="C#", parent=it_cathedral, type="GROUP"
    )
    java = OrganizationalUnit.objects.create(
        name="Java", parent=it_cathedral, type="GROUP"
    )
    adm_and_man_it = OrganizationalUnit.objects.create(
        name="Administration and Management of IT Systems",
        parent=it_cathedral,
        type="GROUP",
    )
    linux = OrganizationalUnit.objects.create(
        name="Linux Administration I",
        parent=adm_and_man_it,
        type="GROUP",
    )
    linux_adv = OrganizationalUnit.objects.create(
        name="Linux Administration II",
        parent=adm_and_man_it,
        type="GROUP",
    )

    math_analysis = OrganizationalUnit.objects.create(
        name="Mathematical Analysis",
        parent=math_cathedral,
        type="GROUP",
    )
    math_algebra = OrganizationalUnit.objects.create(
        name="Linear Algebra",
        parent=math_cathedral,
        type="GROUP",
    )

    mechanics = OrganizationalUnit.objects.create(
        name="Mechanics",
        parent=mech_cathedral,
        type="GROUP",
    )
    physics = OrganizationalUnit.objects.create(
        name="Physics",
        parent=physics_cathedral,
        type="GROUP",
    )

    return locals()


@pytest.fixture
def permissions_codenames(db):
    content_type = ContentType.objects.get_for_model(FakeModel)
    # FakeModel._meta.permissions += *PermissionCreationService.create_fields_permissions(FakeModel),
    permissions = (
        *PermissionCreationService.add_rules_to_permissions(
            content_type.app_label,
            PermissionCreationService.create_crud_permissions_by_type(
                FakeModel._meta.model_name, PermissionType.OWNER
            ),
            [is_owner],
        ),
        *PermissionCreationService.add_rules_to_permissions(
            content_type.app_label,
            PermissionCreationService.create_crud_permissions_by_type(
                FakeModel._meta.model_name, PermissionType.STAFF
            ),
            [is_staff],
        ),
        *PermissionCreationService.add_rules_to_permissions(
            content_type.app_label,
            PermissionCreationService.create_crud_permissions_by_type(
                FakeModel._meta.model_name,
                PermissionType.SUPER_STAFF,
                "when is owner and staff member",
            ),
            [is_staff_and_owner],
        ),
    )
    for codename, name in permissions:
        Permission.objects.get_or_create(
            codename=codename, content_type=content_type, defaults={"name": name}
        )

    yield
    for codename, _ in permissions:
        rule_name = f"{content_type.app_label}.{codename}"
        rules.remove_rule(rule_name)


@pytest.fixture
def fake_model_objects(db, users, organizational_units):
    return {
        "physics": FakeModel.objects.create(
            parent=organizational_units["physics"],
            name="Physics",
            owner=users["teacher_janek"],
        ),
        "java": FakeModel.objects.create(
            parent=organizational_units["java"],
            name="Java",
            owner=users["teacher_janek"],
        ),
        "csharp": FakeModel.objects.create(
            parent=organizational_units["csharp"],
            name="C#",
            owner=users["teacher_janek"],
        ),
        "linux": FakeModel.objects.create(
            parent=organizational_units["linux"],
            name="Linux",
            owner=users["teacher_franek"],
        ),
        "algebra": FakeModel.objects.create(
            parent=organizational_units["math_algebra"],
            name="Algebra",
            owner=users["teacher_franek"],
        ),
    }
