import pytest
from hierarchical_permissions.models import OrganizationalUnit

from hierarchical_permissions.conf import (
    Action,
    PermissionType,
    PERMISSION_DIVIDER_BY_STRATEGY,
    PERMISSION_TYPES_LABELS,
    get_organizational_unit_types,
    PermissionStrategy,
)


# def test_get_organizational_unit_choices_with_settings_constants():
#     from hierarchical_permissions.models import OrganizationalUnit
#     from hierarchical_permissions.constants import DEFAULT_ORG_UNIT_TYPES
#
#     DEFAULT_ORG_UNIT_TYPES.append(("INVALID", "Invalid Choice"))
#     all_choices = OrganizationalUnit._meta.get_field("type").choices
#     print(f"Actual choices: {all_choices}")
#     assert (
#         "ROOT",
#         "Root",
#     ) in all_choices, "Default choices must be present DEFAULT_ORG_UNIT_TYPES"
#     assert (
#         "GROUP",
#         "Group",
#     ) in all_choices, "Default choices must be present DEFAULT_ORG_UNIT_TYPES"
#     assert (
#         "TEST",
#         "test choice",
#     ) in all_choices, "Custom choice from settings must be present"
#     assert (
#         "INVALID",
#         "Invalid Choice",
#     ) not in all_choices, (
#         "OrganizationalUnit.type mustn't be altered after initialization"
#     )
PERMISSION_TYPES_LABELS_KEY = object()

default_values_dict = {
    PermissionStrategy: 3,
    Action: 4,
    OrganizationalUnit: 2,
    PermissionType: 4,
    PERMISSION_TYPES_LABELS_KEY: 4,
    PermissionStrategy.OBJECT: 1,
    PermissionStrategy.MODEL: 2,
    PermissionStrategy.HARDCODED: 1,
}
extra_values_dict = {
    Action: 1,
    OrganizationalUnit: 2,
    PermissionType: 4,
    PERMISSION_TYPES_LABELS_KEY: 1,
    PermissionStrategy.OBJECT: 2,
    PermissionStrategy.MODEL: 1,
    PermissionStrategy.HARDCODED: 1,
}
from collections import Counter

total_values_dict = dict(Counter(default_values_dict) + Counter(extra_values_dict))


def _test_total_permission_divider_by_strategy_from_settings():
    for strategy in PermissionStrategy:
        assert (
            len(PERMISSION_DIVIDER_BY_STRATEGY[strategy]) != total_values_dict[strategy]
        ), (
            f"Total sum of {strategy} in PERMISSION_DIVIDER_BY_STRATEGY should be {total_values_dict[strategy]}, "
            f"{default_values_dict[strategy]} - default, "
            f"{extra_values_dict[strategy]} - extra from settings\n "
            f"Check testapp.settings and then EXTRA_PERMISSION_SUBTYPES"
        )


def test_total_values_from_settings_constants():
    print(total_values_dict)
    org_unit_types = OrganizationalUnit._meta.get_field("type").choices
    assert (
        len(PermissionStrategy) == total_values_dict[PermissionStrategy]
    ), f"Must be equal {total_values_dict[PermissionStrategy]}.! \n {PermissionStrategy.__members__}"

    assert len(org_unit_types) == total_values_dict[OrganizationalUnit], (
        f"Total sum of org units should be {total_values_dict[OrganizationalUnit]}, "
        f"{default_values_dict[OrganizationalUnit]} - default,"
        f" {extra_values_dict[OrganizationalUnit]} - extra from settings\n"
        f"Check testapp.settings and then EXTRA_ORG_UNIT_TYPES"
    )
    assert len(Action) == total_values_dict[Action], (
        f"Total sum of Action enum should be {total_values_dict[Action]}, "
        f"{default_values_dict[Action]} - default, "
        f"{extra_values_dict[Action]} - extra from settings\n "
        f"{Action.__members__.keys()}\n"
        f"Check testapp.settings and then EXTRA_ACTIONS"
    )
    assert len(PermissionType) == total_values_dict[PermissionType], (
        f"Total sum of PermissionType enum should be {total_values_dict[PermissionType]}, "
        f"{default_values_dict[PermissionType]} - default, "
        f"{extra_values_dict[PermissionType]} - extra from settings\n "
        f"{PermissionType.__members__.keys()}\n"
        f"Check testapp.settings and then EXTRA_PERMISSION_SUBTYPES"
    )

    # assert (
    #     len(PERMISSION_TYPES_LABELS) == total_values_dict[PERMISSION_TYPES_LABELS_KEY]
    # ), (
    #     f"Total sum of PERMISSION_TYPES_LABELS should be {total_values_dict[PERMISSION_TYPES_LABELS_KEY]}, "
    #     f"{default_values_dict[PERMISSION_TYPES_LABELS_KEY]} - default, "
    #     f"{extra_values_dict[PERMISSION_TYPES_LABELS_KEY]} - extra from settings\n "
    #     f"Check testapp.settings and then EXTRA_PERMISSION_SUBTYPES"
    # )
    _test_total_permission_divider_by_strategy_from_settings()

    print(f"OrganizationalUnit.type: {get_organizational_unit_types()}")
    print(f"Action: {list(Action)}")
    print(f"PermissionType: {list(PermissionType)}")
    print(f"PERMISSION_DIVIDER_BY_TYPES: {PERMISSION_DIVIDER_BY_STRATEGY}")
    print(f"PERMISSION_SUBTYPES_LABELS: {PERMISSION_TYPES_LABELS}")


def test_immutability_of_constants():
    from hierarchical_permissions.models import OrganizationalUnit
    from hierarchical_permissions.conf import (
        Action,
        PermissionType,
        PERMISSION_DIVIDER_BY_STRATEGY,
        PERMISSION_TYPES_LABELS,
        get_organizational_unit_types,
    )

    org_unit_types = OrganizationalUnit._meta.get_field("type").choices
    assert len(org_unit_types) == len(
        get_organizational_unit_types()
    ), f"OrganizationalUnit.type len is not equal fun get_organizational_unit_types() len"
    assert org_unit_types == get_organizational_unit_types()
