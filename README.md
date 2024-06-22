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
export PATH=/Users/{username}/anaconda3/envs/seedo/bin:$PATH
windowOS:
변수 이름: SEEDO_PYTHON
변수 값: C:\Users\jinho\anaconda3\envs\seedo\python.exe

```

### 3-1. 경로 수정한 경우 pre-commit 환경 초기화

```
pre-commit uninstall
pre-commit install
```

### 4. 작업 후, git add, git commit

> 처음 commit 할 때, pre-commit 세팅 다운로드 - cache 되는 과정이 있어 오래 걸린다.<br><br> > [INFO] This may take a few minutes...<br><br>
> 차후 반복되는 commit은 빠르게 가능하다.

```
git add {file}
git commit -m "{message}"
```
