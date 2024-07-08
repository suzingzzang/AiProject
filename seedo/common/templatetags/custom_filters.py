from django import template

register = template.Library()


@register.filter(name="email_username")
def email_username(value):
    try:
        return value.split("@")[0]
    except (AttributeError, IndexError):
        return ""


@register.filter(name="file_name")
def file_name(value):
    try:
        return value.split("/")[-1]
    except (AttributeError, IndexError):
        return ""


@register.filter(name="extension_name")
def extension_name(value):
    try:
        return value.split(".")[-1]
    except (AttributeError, IndexError):
        return ""


@register.filter(name="in_list")
def in_list(value, arg):
    return value in arg.split(",")


@register.filter(name="is_q_list_option")
def is_q_list_option(value, arg):
    arg2value = "answered" if arg == 2 else "unanswered" if arg == 3 else ""
    return value == arg2value
