from django import template
from django.db.models import Q
from matching.models import UserRequest
from record.models import Accident

register = template.Library()


@register.inclusion_tag("alarm_list.html", takes_context=True)
def get_user_notifications(context):
    request = context["request"]
    user = request.user
    user_requests = UserRequest.objects.filter((Q(requester=user) | Q(recipient=user)) & Q(is_accepted=True))

    partner_list = []
    for user_request in user_requests:
        partner_info = user_request.recipient if user_request.requester == user else user_request.requester
        partner_list.append(partner_info)

    accident_records = Accident.objects.filter(user__in=partner_list).order_by("-accident_date", "-accident_time")[:10]

    return {"accident_records": accident_records}
