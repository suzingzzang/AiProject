from django import template

register = template.Library()


@register.filter(name="email_username")
def email_username(value):
    try:
        return value.split("@")[0]
    except (AttributeError, IndexError):
        return ""
