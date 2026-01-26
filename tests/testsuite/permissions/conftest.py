import pytest
from django.contrib.auth.models import User, Group
from hierarchical_permissions.models import OrganizationalUnit, UserGroup
from hierarchical_permissions.services import PermissionCreationService
from test_model_app.models import FakeModel


@pytest.fixture
def users(db):
    teacher_janek = User.objects.create_user(
        username="t_janek", email="janek@example.com", password="admin", is_staff=True
    )
    teacher_franek = User.objects.create_user(
        username="t_franek", email="franek@example.com", password="admin", is_staff=True
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
def permission_groups(db):
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
