pass


# def test_immutability_of_constants():
#     from hierarchical_permissions.models import OrganizationalUnit
#     from hierarchical_permissions.conf import (
#         Action,
#         PermissionType,
#         PERMISSION_DIVIDER_BY_STRATEGY,
#         PERMISSION_TYPES_LABELS,
#         get_organizational_unit_types,
#     )
#
#     org_unit_types = OrganizationalUnit._meta.get_field("type").choices
#     assert len(org_unit_types) == len(
#         get_organizational_unit_types()
#     ), f"OrganizationalUnit.type len is not equal fun get_organizational_unit_types() len"
#     assert org_unit_types == get_organizational_unit_types()
