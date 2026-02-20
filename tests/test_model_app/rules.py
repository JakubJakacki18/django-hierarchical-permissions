import rules
from datetime import date


@rules.predicate
def is_owner(user, obj):
    return obj.owner == user


@rules.predicate
def is_staff(user):
    return user.is_staff


is_staff_and_owner = is_staff & is_owner

# @rules.predicate
# def is_weekend():
#     return date.today().weekday() in (5, 6)
#
#
# rules.add_perm("test_model_app.isWeekend", is_weekend)
