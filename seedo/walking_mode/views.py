import os
import urllib.parse
import urllib.request
from pathlib import Path

import cv2
import environ
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.views import View
from PIL import Image
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent

# pt 파일가져오기
yolo_od_pt = os.path.join(BASE_DIR, "walking_mode/pt_files/yolov8n_epoch20.pt")
yolo_seg_pt = os.path.join(BASE_DIR, "walking_mode/pt_files/yolov8s_epoch50.pt")

# API 가져오기
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_path = BASE_DIR.parent / ".env"
environ.Env.read_env(env_file=env_path)

CLIENT_ID = env("NAVER_TTS_CLIENT_ID")
SECRETE_KEY = env("NAVER_TTS_CLIENT_SECRETE_KEY")


# tts api
def naver_tts(text):
    try:
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
            return response_body
        else:
            raise Exception(f"Error Code: {rescode}")
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTPError: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URLError: {e.reason}")
    except Exception as e:
        raise Exception(str(e))


# ##프레임수 줄여주는 코드
# def reduce_fps(input_video_path, fps_video_path, target_fps=2):
#     # 비디오 파일 열기
#     cap = cv2.VideoCapture(input_video_path)
#     if not cap.isOpened():
#         print("Error opening video file")
#         return

#     # 원본 비디오의 FPS 및 프레임 크기 가져오기
#     original_fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#     # 출력 비디오 설정
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     #오리지널 패스에 같은 크기로 사진 저장
#     out = cv2.VideoWriter(fps_video_path, fourcc, target_fps, (frame_width, frame_height))

#     # FPS 감소 비율 계산
#     fps_ratio = original_fps / target_fps

#     frame_count = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # 지정된 비율에 따라 프레임 쓰기
#         if frame_count % int(fps_ratio) == 0:
#             out.write(frame)

#         frame_count += 1

#     # 비디오 파일 닫기
#     cap.release()
#     out.release()
#     print(f"Finished reducing FPS from {original_fps} to {target_fps}. Output saved to {fps_video_path}")


class ImageUploadView(View):
    template_name = "test.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        od_classes = []
        seg_classes = []
        tts_audio_url = None  # 초기화

        # if request.FILES.get('image'):
        if request.FILES.get("file"):
            # 모델 로드

            model_od = YOLO(yolo_od_pt)
            model_seg = YOLO(yolo_seg_pt)
            names_od = model_od.names
            names_seg = model_seg.names

            # image = request.FILES['image'] 영상을 기본으로
            file = request.FILES["file"]
            file_path = os.path.join(settings.MEDIA_ROOT, "video.mp4")
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # 만약 파일이 이미지라면!
            if file.content_type.startswith("image"):
                img = Image.open(file_path)
                img = np.array(img)

                # 객체 탐지
                results_od = model_od(img)
                results_seg = model_seg(img)

                # 객체 클래스 추출
                if results_od and results_od[0].boxes:
                    od_classes = [names_od[int(cls)] for cls in results_od[0].boxes.cls]
                else:
                    od_classes = []

                if results_seg and results_seg[0].boxes:
                    seg_classes = [names_seg[int(cls)] for cls in results_seg[0].boxes.cls]
                else:
                    seg_classes = []

                # 디버깅 로그 추가
                print("Detected Object Classes:", od_classes)
                print("Segmented Object Classes:", seg_classes)

            # 비디오 파일이라면!
            elif file.content_type.startswith("video"):
                cap = cv2.VideoCapture(file_path)

                od_classes = []
                seg_classes = []

                # 초당 프레임조작용(reduce fps 이용- 크기조정 아직 미이용)
                target_fps = 2

                original_fps = cap.get(cv2.CAP_PROP_FPS)
                frame_interval = original_fps / target_fps

                frame_count = 0
                while cap.isOpened():
                    ret, frame = cap.read()  # ret: 프레임 존재 boolean , frame: ret = true일때 나오는값
                    if not ret:
                        print("Video frame is empty or video processing has been successfully completed.")
                        break
                    if frame_count % frame_interval == 0:

                        # 객체 탐지
                        results_od = model_od.track(frame, conf=0.3, iou=0.5, persist=True)
                        results_seg = model_seg.track(frame, conf=0.3, iou=0.5, persist=True)

                        # 객체 클래스 추출
                        if results_od and results_od[0].boxes:
                            od_classes = [names_od[int(cls)] for cls in results_od[0].boxes.cls]
                        else:
                            od_classes = []

                        if results_seg and results_seg[0].boxes:
                            seg_classes = [names_seg[int(cls)] for cls in results_seg[0].boxes.cls]
                        else:
                            seg_classes = []
                    frame_count += 1

                cap.release()

            # 디버깅 로그 추가
            print("Detected Object Classes:", od_classes)
            print("Segmented Object Classes:", seg_classes)

            # tts 문자생성
            tts_audio_url = None  # 초기화
            tts_text = []
            if len(od_classes) != 0:
                distance = ["0미터" for _ in range(len(od_classes))]
                for od_class, distance in zip(od_classes, distance):
                    tts_text.append(f"{od_class}, {distance}")
                tts_text = " , ".join(tts_text)
            else:
                distance = ["0미터" for _ in range(len(seg_classes))]
                for seg_class, distance in zip(seg_classes, distance):
                    tts_text.append(f"{seg_class}, {distance}")
                tts_text = " , ".join(tts_text)

            # TTS 합성
            # tts_text = "Object detection classes: " + ", ".join(od_classes) + ". Segmentation classes: " + ", ".join(seg_classes)
            try:
                tts_audio = naver_tts(tts_text)
                if tts_audio:
                    tts_audio_dir = os.path.join(settings.MEDIA_ROOT, "tts_audio")
                    if not os.path.exists(tts_audio_dir):
                        os.makedirs(tts_audio_dir)
                    tts_audio_path = os.path.join(tts_audio_dir, "tts_audio.mp3")
                    with open(tts_audio_path, "wb") as f:
                        f.write(tts_audio)
                    tts_audio_url = "media/tts_audio/tts_audio.mp3"
                    print("TTS Audio Path:", tts_audio_path)  # 로그 추가
                    print("TTS Audio URL:", tts_audio_url)  # 로그 추가
            except Exception as e:
                print(f"TTS Error: {str(e)}")

        context = {"od_classes": od_classes, "seg_classes": seg_classes, "tts_audio_url": tts_audio_url}

        return render(request, self.template_name, context)
