import json

import requests
from common.decorators import token_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import urllib.parse
import urllib.request
from django.http import HttpResponse
import environ
from .models import Navigation
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# API 가져오기
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_path = BASE_DIR.parent / ".env"
environ.Env.read_env(env_file=env_path)

CLIENT_ID = env("NAVER_TTS_CLIENT_ID")
SECRETE_KEY = env("NAVER_TTS_CLIENT_SECRETE_KEY")

@token_required
def index(request):
    return render(request, "navigation/index.html")


@token_required
def get_walking_directions(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        start_location = data.get("start_location")
        end_location = data.get("end_location")
        # 네이버 API 호출
        endpoint = "https://apis.openapi.sk.com/tmap/routes/pedestrian"
        headers = {"Content-Type": "application/json", "appKey": settings.TMAP_API_KEY}  # settings.py에 등록된 Tmap API 키 사용
        data = {
            "startX": start_location[0],
            "startY": start_location[1],
            "endX": end_location[0],
            "endY": end_location[1],
            "reqCoordType": "WGS84GEO",
            "resCoordType": "WGS84GEO",
            "angle": 0,
            "speed": 0,
            "searchOption": "0",
            "sort": "index",
            # 추후에 geocode를 이용해서 좌표값을 주소값으로 변환한다음 보내야함....
            "startName": "출발지",
            "endName": "도착지",
        }

        try:

            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()  # 에러가 발생하면 예외 처리
            directions_data = response.json()

            # 데이터베이스에 저장
            Navigation.objects.create(user=request.user, start_location=start_location, end_location=end_location)
            print(directions_data)
            # JSON 형식으로 데이터 전송
            return JsonResponse(directions_data)

        except requests.exceptions.HTTPError as err:
            error_message = {"error": str(err)}
            return JsonResponse(error_message, status=response.status_code)

    else:
        return render(request, "navigation/index.html")

@token_required
def naver_tts(request):
    print('success')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            encText = urllib.parse.quote(text)
            data = f"speaker=nara&volume=0&speed=0&pitch=0&format=mp3&text={encText}"
            url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

            request_api = urllib.request.Request(url)
            request_api.add_header("X-NCP-APIGW-API-KEY-ID", CLIENT_ID)
            request_api.add_header("X-NCP-APIGW-API-KEY", SECRETE_KEY)

            response = urllib.request.urlopen(request_api, data=data.encode("utf-8"))
            rescode = response.getcode()

            if rescode == 200:
                response_body = response.read()
                response = HttpResponse(response_body, content_type='audio/mp3')
                response['Content-Disposition'] = 'attachment; filename="tts.mp3"'
                return response
            else:
                return HttpResponse(f"Error Code: {rescode}", status=rescode)
        except urllib.error.HTTPError as e:
            return HttpResponse(f"HTTPError: {e.code} {e.reason}", status=e.code)
        except urllib.error.URLError as e:
            return HttpResponse(f"URLError: {e.reason}", status=500)
        except Exception as e:
            return HttpResponse(str(e), status=500)
    return HttpResponse(status=405)