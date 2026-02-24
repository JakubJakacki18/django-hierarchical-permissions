import logging
from collections.abc import Iterable
from typing import Optional, Any, Protocol, TYPE_CHECKING

import rules

if TYPE_CHECKING:
    from .checker import PermissionChecker

logger = logging.getLogger(__name__)


class PermissionCheckerStrategy(Protocol):
    @staticmethod
    def check(
        permissions: Iterable[str], obj: Optional[Any], service: PermissionChecker
    ) -> bool: ...


class RegularPermissionCheckerStrategy:
    @staticmethod
    def check(
        permissions: Iterable[str], obj: Optional[Any], service: PermissionChecker
    ) -> bool:
        """Check regular permissions"""
        return any(
            service.has_permission(permission, obj) for permission in permissions
        )


class ObjectPermissionCheckerStrategy:
    @staticmethod
    def check(
        permissions: Iterable[str], obj: Optional[Any], service: PermissionChecker
    ) -> bool:
        """Check OLP (Object Level Permission)"""
        # print(f"Sprawdzane olp uprawnień: {permissions}")
        if obj is None:
            return False  # could be unnecessary
        for permission in permissions:
            has_perm = service.has_permission(permission, obj)
            logger.debug("permission: %s has_perm: %s", permission, has_perm)
            if has_perm:
                if test_rule := rules.test_rule(permission, service.user, obj):
                    logger.debug("permission: %s test_rule: %s", permission, test_rule)
                    return True
        return False


class HardcodedPermissionCheckerStrategy:
    @staticmethod
    def check(
        permissions: Iterable[str], obj: Optional[Any], service: PermissionChecker
    ) -> bool:
        # TODO Koncept i zasada działania do ponownego przemyślenia
        logger.warning("Checking of hardcoded permissions are not implemented yet.")
        return False

        # return any(self.user.has_perm(permission, obj) for permission in permissions)
