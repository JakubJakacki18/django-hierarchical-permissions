from enum import EnumType
from typing import Optional
import pytest

from hierarchical_permissions.defaults import ORGANIZATIONAL_UNITS_TYPES
from hierarchical_permissions.models import OrganizationalUnit
from hierarchical_permissions.conf import (
    Action,
    PermissionType,
    PERMISSION_DIVIDER_BY_STRATEGY,
    PERMISSION_TYPES_LABELS,
    get_organizational_unit_types,
    PermissionStrategy,
)

PERMISSION_TYPES_LABELS_KEY = object()
from collections import Counter


@pytest.fixture
def total_values_dict(extra_values_dict: dict):
    from hierarchical_permissions.defaults import ACTION
    from hierarchical_permissions.defaults import (
        PERMISSION_DIVIDER_BY_STRATEGY as DEFAULT_PERMISSION_DIVIDER_BY_STRATEGY,
        PERMISSION_TYPES_LABELS as DEFAULT_PERMISSION_TYPES_LABELS,
    )

    defaults = {
        PermissionStrategy: 3,
        Action: len(ACTION),
        OrganizationalUnit: len(ORGANIZATIONAL_UNITS_TYPES),
        PermissionType: sum(
            len(permission_types)
            for permission_types in DEFAULT_PERMISSION_DIVIDER_BY_STRATEGY.values()
        ),
        PERMISSION_TYPES_LABELS_KEY: len(DEFAULT_PERMISSION_TYPES_LABELS),
        PermissionStrategy.OBJECT: len(
            DEFAULT_PERMISSION_DIVIDER_BY_STRATEGY[PermissionStrategy.OBJECT]
        ),
        PermissionStrategy.MODEL: len(
            DEFAULT_PERMISSION_DIVIDER_BY_STRATEGY[PermissionStrategy.MODEL]
        ),
        PermissionStrategy.HARDCODED: len(
            DEFAULT_PERMISSION_DIVIDER_BY_STRATEGY[PermissionStrategy.HARDCODED]
        ),
    }
    return dict(Counter(defaults) + Counter(extra_values_dict))


@pytest.fixture
def extra_values_dict():
    return {
        Action: 1,
        OrganizationalUnit: 2,
        PermissionType: 5,
        PERMISSION_TYPES_LABELS_KEY: 1,
        PermissionStrategy.OBJECT: 3,
        PermissionStrategy.MODEL: 1,
        PermissionStrategy.HARDCODED: 1,
    }


@pytest.mark.parametrize(
    "enum_cls, settings_hint",
    [
        (PermissionStrategy, None),
        (Action, "EXTRA_ACTIONS"),
        (PermissionType, "EXTRA_PERMISSION_SUBTYPES"),
    ],
)
def test_enum_when_extended_by_extra_values_has_expected_size(
    total_values_dict: dict,
    extra_values_dict: dict,
    enum_cls: EnumType,
    settings_hint: Optional[str],
):
    expected = total_values_dict[enum_cls]
    error_msg = (
        f"Total sum of Action enum should be {total_values_dict[enum_cls]}, \n"
        f"{extra_values_dict.get(enum_cls,0)} - extra from settings\n"
        f"Check amount of extra values in extra_values_dict fixture\n"
        f"{enum_cls.__members__.keys()}\n"
    )
    if settings_hint:
        error_msg += f"Check testapp.setting and then {settings_hint}"
    assert len(enum_cls) == expected, error_msg


@pytest.mark.parametrize("strategy", PermissionStrategy)
def test_permission_divider_by_strategy_when_extended_by_extra_values_has_expected_size(
    total_values_dict: dict,
    extra_values_dict: dict,
    strategy: PermissionStrategy,
):
    assert (
        len(PERMISSION_DIVIDER_BY_STRATEGY[strategy]) == total_values_dict[strategy]
    ), (
        f"Total sum of {strategy} in PERMISSION_DIVIDER_BY_STRATEGY should be {total_values_dict[strategy]},\n "
        f"{extra_values_dict[strategy]} - extra from settings\n "
        f"Check amount of extra values in extra_values_dict fixture\n"
        f"Check testapp.settings and then EXTRA_PERMISSION_SUBTYPES"
    )


@pytest.mark.parametrize(
    "source_of_org_unit_type",
    [
        OrganizationalUnit._meta.get_field("type").choices,
        get_organizational_unit_types(),
    ],
)
def test_org_unit_types_from_meta_when_extended_by_extra_values_has_expected_size(
    total_values_dict: dict,
    extra_values_dict: dict,
    source_of_org_unit_type,
):
    assert len(source_of_org_unit_type) == total_values_dict[OrganizationalUnit], (
        f"Total sum of org units should be {total_values_dict[OrganizationalUnit]}, "
        f" {extra_values_dict[OrganizationalUnit]} - extra from settings\n"
        f"Check amount of extra values in extra_values_dict fixture\n"
        f"Check testapp.settings and then EXTRA_ORG_UNIT_TYPES"
    )


def test_permission_types_labels_when_extended_by_extra_values_has_expected_size(
    total_values_dict: dict,
    extra_values_dict: dict,
):
    assert (
        len(PERMISSION_TYPES_LABELS) == total_values_dict[PERMISSION_TYPES_LABELS_KEY]
    ), (
        f"Total sum of PERMISSION_TYPES_LABELS should be {total_values_dict[PERMISSION_TYPES_LABELS_KEY]}, "
        f"{extra_values_dict[PERMISSION_TYPES_LABELS_KEY]} - extra from settings\n "
        f"Check amount of extra values in extra_values_dict fixture\n"
        f"Check testapp.settings and then EXTRA_PERMISSION_SUBTYPES"
    )
