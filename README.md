
# Seedo
![image](https://github.com/user-attachments/assets/be5dbf37-eb45-4d78-96c3-38c3ec0b02ac)

## 기대효과
보행 보조 기능을 통해 시각장애인의 활동 지원과 관련된 복지 지출과 행정 비용을 효율적으로 관리하여 감소시킬 수 있으며, 보건 복지부 장애인 정책국과 함께 시각장애인들에 생활 인프라를 향상시키고, 관련 정책목표의 효율적 달성에 기여한다.
## 3.주요 서비스 내용
1. 보행 보조 모드[AI Modeling] - 노면 상태 확인 및 특이 사항 발생 경우
노면 상태 구분 사항 [Object Detection, Segmentation]
1-1. 보도인지 차도인지 구분
1-2. 점자블록 구분: 정상인 경우, 깨진 경우, 점자블록이 더이상 이어지지 않은 경우, 점자블록이 가려진 경우(전동킥보드 등)
1-3. 장애물: 볼라드(자동차 진입 억제용 말뚝), 맨홀, 웅덩이 등 (기타: 은행, 분변)
특이 사항 발생 경우 [TTS + Database]
1-1. 보도를 벗어난 경우: '보도를 벗어났습니다. 주의하세요'
1-2. 점자블록이 깨진 경우, 더이상 이어지지 않은 경우 > '파손 점자블록이 발견되었습니다. 조심하세요. 이미지를 저장합니다.'> 민원 신청을 위해 자동으로 캡처 및 위치 정보 저장
1-3. 장애물 발생: '전방에 ㅇㅇㅇ가 있습니다. 주의하세요' (※ 오감지를 방지하기 위한 범위 조정 필요)

2. 보행 보조 모드[AI Modeling] - 보행 중, 낙상 사고 발생 경우
사고 발생 시, 감지 후 기록 저장 및 응급 상황 연결 [ML + Database + Device]
1-1. 핸드폰 GPS, 자이로센서, 가속도센서 값 활용 행동분석: 사고 판단 후, 사고 시각, 지점(위치) 기준으로 전후구간 영상기록
1-2. 응급 상황 연결: 보호자 번호의 디바이스로 응급상황 알람 전송
3. 목적지 네비게이션 [API]
1-1. 출발지, 목적지 입력 받아 경로 설정.
1-2. 실시간 현 위치 기준으로 길안내 및 도착 확인 음성 제공
1-3. 경로를 벗어난 경우, 현 위치 기준으로 목적지 경로 재설정

4. 글 읽기 [OCR]
1-1. 카메라로 인식하고 싶은 물건 등을 촬영하고, 사진 속의 텍스트와 물건 등을 인식하여 상황에 맞게 음성 및 텍스트 출력 
1-2. 화폐 등 정확한 정보확인이 필요한 경우, 재확인이 필요함을 음성 및 텍스트로 알람

5. 회원가입 후, 회원별 관리데이터 활용방안: 회원가입이 필요한 이유 [Database]
1-1. 맹인 로그인: 앱 기능이 제공되고, 기록이 저장된다.
1-2. 보호자 로그인:
맹인과 보호자를 인증을 통해 매칭한다. 보호자는 자신이 보호하는 맹인으로 매칭된 분들의 영상을 열람할 수 있다. (삭제는 중앙 관리자(정부 측)에게 요청 필요, 보호자가 악의적인 목적으로 삭제하는 것 방지)보호자가 타지역에서 사고 알람을 전달받고 사고 영상을 확인하여, 보호조치를 할 수 있게 한다.

## 역할 : 백엔드 총괄
데이터베이스 설계 및 서버 연결 / 회원가입 및 로그인
네비게이션 길찾기 기능 및 TTS / 문의 게시판 구현









## 🔍 백엔드 초기 환경세팅

### • 라이브러리 설치

### 1. 가상환경 생성(anaconda) 및 확인

- 환경이름: seedo

```
conda create -n seedo python=3.11
conda env list
```

### 2. 가상환경 이동

```
conda activate seedo
```

### 3. pip install upgrade

```
pip install --upgrade pip
```

### 4. requirements.txt 설치

```
pip install -r requirements.txt
```

<br>

---

### 🖍️ 배포서버 nginx 설정 (OS: ubuntu)

### 1. nginx 설치

```
sudo apt update
sudo apt install nginx
```

### 2. nginx.conf 설정

- nginx.conf user 설정 변경

```
sudo vi /etc/nginx/nginx.conf

>>
user ubuntu;
#user {username}
```

### | (배포 설정: HTTPS - SSL인증서 발급)

- openssl 설치

```
sudo apt update
sudo apt install openssl
openssl version
```

- SSL인증서 발급

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/ssl/private/localhost-selfsigned.key \
-out /etc/ssl/certs/localhost-selfsigned.crt
```

- sites-available/ecotour 에 server 구성 설정

```
sudo vi /etc/nginx/sites-available/seedo-pjt
```

아래 내용 작성

- 80(http)->443(https)->8000(unix socket)

```

# Server block for uwsgi application and static/media files
server {
    listen 8000;
    server_name localhost;

    set $base_path /home/ubuntu/SeedoPJT/seedo;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:$base_path/uwsgi.sock;
    }

    location /static/ {
        alias $base_path/staticfiles/;
    }

    location /media/ {
        alias $base_path/media/;
    }

    #error_log $base_path/logs/nginx_error.log;
    access_log $base_path/logs/nginx_access.log;
}


# HTTPS server block for uwsgi application and static/media files
server {
    listen 443 ssl;
    server_name localhost;  # or your_domain_or_ip for production

    ssl_certificate /etc/ssl/certs/localhost-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/localhost-selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    set $base_path /home/ubuntu/SeedoPJT/seedo;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Internal communication
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias $base_path/staticfiles/;
    }

    location /media/ {
        alias $base_path/media/;
    }

    # error_log $base_path/logs/nginx_error.log;
    access_log $base_path/logs/nginx_access.log;
}

# HTTP server block to redirect all traffic to HTTPS
server {
    listen 80;
    server_name localhost;  # or your_domain_or_ip for production

    location / {
        return 301 https://$host$request_uri;
    }

    # error_log $base_path/logs/nginx_http_error.log;
    access_log $base_path/logs/nginx_http_access.log;
}
```

- 심볼릭 링크 연결

```
sudo ln -s /etc/nginx/sites-available/seedo-pjt /etc/nginx/sites-enabled/
```

- default 구성 포트 변경(80 -> 8080)

```
sudo vi /etc/nginx/sites-available/default
>>
listen 8080 default_server;
listen [::]:8080 default_server;
```

<br>

---

<br>

## 🔍 배포 서버 실행 방법

### 0. /SeedoPJT/seedo 하위에 디렉토리 생성 (존재하지 않을 경우)

```
/seedo/logs
/seedo/media
```

### 1. app static 모아 정적파일 생성

- app에 새로운 static 추가가 있었을 경우 필요

```
python manage.py collectstatic
```

### 2. nginx 실행

```
sudo nginx
```

### 3. uwsgi 실행

```
uwsgi --ini uwsgi.ini
```

### 4. 사이트 접속

```
https://{domain_ip | domain_url}
```

<br>

---

## 🖍️ pre-commit config 세팅:

> pre-commit 훅이 git add, git commit 할 때,<br>
> 자동으로 코드 스타일과 형식을 유지

### 0. 가상환경 이동

```
conda activate seedo
```

### 1. 라이브러리 설치

```
pip install pre-commit
```

### 2. pre-commit 훅 설치

```
pre-commit install
```

### 3. 훅 설정 확인하기

```
vi .git/hooks/pre-commit

>>> 아래 파이썬 경로가 가상환경 경로로 되어 있는지 확인!
macOS:
INSTALL_PYTHON=/Users/{username}/anaconda3/envs/seedo/bin/python
windowOS:
INSTALL_PYTHON=C:\Users\{username}\anaconda3\envs\seedo\python.exe


>>> 경로가 다르다면, 환경변수에 자신의 conda 환경 python 경로 추가하기
macOS:
export PATH="/Users/{username}/anaconda3/envs/seedo/bin:$PATH"
windowOS:
변수 이름: SEEDO_PYTHON
변수 값: C:\Users\{username}\anaconda3\envs\seedo\python.exe

```

### 3-1. 경로 수정한 경우 pre-commit 환경 초기화

```
pre-commit uninstall
pre-commit install
```

### 4. 작업 후 커밋 사전작업, pre-commit 자동 포멧팅 실행

- 모든 포멧팅이 passed가 나오도록 반복 실행한다.

```
pre-commit run --all-files
```

### 4. pre-commit 자동 포멧팅 후, git add, git commit

```
git add {file}
git commit -m "{message}"
```
