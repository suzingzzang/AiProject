# Seedo

## 🔍 깃 작업 규칙

### 1. 기관 레포지토리 로컬 디렉토리에 클론

```
git clone {git address}
```

## 🚨 로컬의 개인 branch 작업 후, pull-merge-push 필수 규칙!!!

### 1. 로컬의 레포지토리에서 dev로 checkout 한다.

```
git checkout dev
```

### 2. 로컬에서 원격 레포지토리의 내용을 Pull 하여 Sync 맞춘다.

```
git pull origin dev
```

### 3. 내가 작업한 branch로 checkout (Sync 맞추는 작업)

```
git checkout {mybranch}
```

### 4. 로컬에서 (최신 Sync가 된) dev 브랜치를 작업 브랜치로 merge하여 conflict 해결

```
git merge dev {mybranch}
```

### 5. merge가 되었다면, 원격 레포지토리로 push

```
git push origin {mybranch}
```

### 6. push된 branch 확인 후, 원격 {branch}에서 dev로 pull-request 생성

### 7. 동료들에게 '머지합니다!' 하고 공지한 후, 생성된 pull-request 머지 완료하기!
