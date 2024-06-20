# Seedo

## 🔍 깃 작업 규칙

### 1. 기관 레포지토리 로컬 디렉토리에 클론

```
git clone {git address}
```

## 🚨 로컬의 개인 branch 작업 후, pull-merge-push 필수 규칙!!!

### 0. 로컬 개인 branch 작업 후, git add 와 git commit 으로 커밋로그를 생성한다.

```
git add {file}
git commit -m "{message}"
```

### 1. 로컬 레포지토리의 dev로 checkout 한다.

```
git checkout dev
```

### 2. 원격 레포지토리의 dev 내용을 로컬 레포지토리의 dev 으로 Pull 하여 Sync 맞춘다.

```
git pull origin dev
```

### 3. 로컬 레포지토리의 내가 작업한 branch로 checkout 한다.

```
git checkout {mybranch}
```

### 4. 로컬에서 (최신 Sync가 된) dev 를 작업 branch로 merge하여 conflict 해결한다.

```
git merge dev {mybranch}
```

### 5. commit 로그가 제대로 생성되었는지 확인한다.

```
git log
```

### 5. merge가 되었다면, 원격 레포지토리로 push 한다.

```
git push origin {mybranch}
```

### 6. 원격 branch의 변경 log 확인 후, 원격 branch에서 dev로 pull-request 생성

### 7. 동료들에게 '머지합니다!' 하고 공지한 후, 생성된 pull-request 머지 완료하기!
