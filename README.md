# Seedo

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
