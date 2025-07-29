import pytest


def test_settings_constants():
    from hierarchical_permissions.models import OrganizationalUnit

    all_choices = OrganizationalUnit._meta.get_field("type").choices
    print(f"Actual choices: {all_choices}")
    assert ("ROOT", "Root") in all_choices
    assert ("TEST", "test choice") in all_choices
    assert ("GROUP", "Group") in all_choices
