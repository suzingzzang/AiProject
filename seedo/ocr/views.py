from django.shortcuts import render

import openai
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from PIL import Image
from io import BytesIO

client = openai.OpenAI()

# Create your views here.

def index(request):
    return render(request, 'ocr/index.html')


def capture(request):
    if request.method == 'POST':  # 요청이 POST인지 확인합니다.
        image_data = request.POST.get('image_data')  # 이미지 데이터를 폼 데이터에서 가져옵니다.
        if image_data:
            image_data = base64.b64decode(image_data.split(',')[1])  # base64로 인코딩된 이미지 데이터를 디코딩합니다.
            
            image = Image.open(BytesIO(image_data))
            
            # 이미지 형식 및 크기 검증
            if image.format.lower() not in ['jpeg', 'png', 'gif', 'webp']:
                return JsonResponse({'error': 'Unsupported image format'}, status=400)
            
            if len(image_data) > 20 * 1024 * 1024:  # 20MB 제한
                return JsonResponse({'error': 'Image size exceeds 20MB'}, status=400)

            # 이미지 데이터를 base64로 다시 인코딩
            buffered = BytesIO()
            image.save(buffered, format=image.format)
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """당신은 유능한 시각장애인 시각보조장치입니다. 다음 규칙을 지키지 않으면 시각장애인에게 치명적인 문제를 일으킵니다. 다음 규칙을 절대적으로 지키며 이미지의 글자를 읽어주세요.
                                                1. 정확하지 않은거나 사진에 없는 내용은 말하지 마세요.
                                                2. 명확하지 글에 대해서는 무조건 인식하기 어렵고 출력되는 내용이 정확하지 않을 수 있다고 말합니다.
                                                3. 글자가 선명하지 않다면 사진을 다시 찍어달라고 안내합니다.
                                                4. 긴글은 페이지당 50글자 이내로 요약하여 말하세요.
                                                5. 당신의 지식을 이용해서 사진에 없는 내용을 판단하여 지어내는 행위를 절대 하지마세요.
                                                6. 의약품, 주의사항, 위험물, 의료정보, 안전정보 와 같은 내용에서는 5번을 절대적으로 지키세요. 
                                                """},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"}
                    }  
                ]}
            ],
            temperature=0.0,
            top_p=0.95,
            )
            answer = response.choices[0].message.content
            print(answer)
            return JsonResponse({'answer': answer}) 
    return JsonResponse({'error': 'Invalid request'}, status=400) # 유효하지 않은 요청에 대해 오류 응답을 반환합니다.