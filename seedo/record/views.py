from common.decorators import token_required
from django.db.models import Q
from django.shortcuts import render
from matching.models import UserRequest

from .models import Condition

# Create your views here.


@token_required
def broken_view(request, request_id):
    user = request.user
    # request_id가 보낸 요청과 받은 요청 중 파트너 허가된 목록반환
    user_requests = UserRequest.objects.filter((Q(requester=user) | Q(recipient=user)) & Q(is_accepted=True))

    partner_list = [{"user": user}]
    for user_request in user_requests:
        partner_info = {"user": user_request.recipient if user_request.requester == user else user_request.requester}
        partner_list.append(partner_info)

    # 조회하는 사용자의 파손 기록 조회
    broken_records = Condition.objects.filter(user=request_id)
    broken_list = []
    for broken_record in broken_records:
        broken_info = {
            "broken_date": broken_record.condition_date,
            "broken_img": broken_record.condition_image_path,
            "broken_location": broken_record.condition_location,
        }
        broken_list.append(broken_info)

    context = {"partner_list": partner_list, "broken_list": broken_list}
    return render(request, "record/break.html", context)
