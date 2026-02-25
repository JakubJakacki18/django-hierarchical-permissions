from enum import Enum


class PermissionStrategy(str, Enum):
    OBJECT = "olp"
    MODEL = "regular"
    HARDCODED = "hardcoded"


PERMISSION_TYPE = {
    "FIELD": "field",
}

PERMISSION_TYPES_LABELS = {
    "FIELD": lambda action_value, model_name, field: f"Can {action_value} {field} field from {model_name} model",
}

PERMISSION_DIVIDER_BY_STRATEGY = {
    PermissionStrategy.OBJECT: [],
    PermissionStrategy.MODEL: [
        "FIELD",
    ],
    PermissionStrategy.HARDCODED: [],
}

ACTION = {
    "ADD": "add",
    "CHANGE": "change",
    "VIEW": "view",
    "DELETE": "delete",
}

ORGANIZATIONAL_UNITS_TYPES = (
    ("ROOT", "Root"),
    ("GROUP", "Group"),
)
