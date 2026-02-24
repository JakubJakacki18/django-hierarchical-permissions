import logging

from .utils import args_extractor, permission_extractor
from .checker import PermissionChecker
from typing import Union, Callable

logger = logging.getLogger(__name__)


def has_perm_checker_decorator(*permissions_in_fun_or_args: Union[str, Callable]):
    def inner(func):
        def wrapper(*args, **kwargs):
            self, request, obj = args_extractor(*args)
            permissions = permission_extractor(self, *permissions_in_fun_or_args)
            print("Dekorator dostał argumenty:", permissions)
            print("Wywołuję funkcję:", func.__name__)
            return (
                True
                if PermissionChecker(request.user).has_perm_by_permissions_codenames(
                    obj, *permissions
                )
                else func(*args, **kwargs)
            )

        return wrapper

    return inner
