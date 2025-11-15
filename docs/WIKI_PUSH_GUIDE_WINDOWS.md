# Windows에서 GitHub Wiki 푸시하기

> Windows 환경에서 Dawn of Stellar Wiki 문서를 GitHub Wiki에 업로드하는 방법

---

## 📋 준비물

- ✅ Git for Windows 설치 ([다운로드](https://git-scm.com/download/win))
- ✅ GitHub 계정
- ✅ Dos 저장소 접근 권한

---

## 🚀 방법 1: GitHub에서 직접 편집 (가장 쉬움)

Wiki 페이지가 적다면 GitHub 웹 인터페이스에서 직접 편집하는 것이 가장 간단합니다.

### 단계:

1. **Wiki 페이지 이동**
   - https://github.com/APTOL-7176/Dos/wiki 접속

2. **새 페이지 만들기**
   - 우측 상단 "New Page" 버튼 클릭
   - 페이지 제목 입력 (예: "Home", "Beginner-Guide")
   - 내용 붙여넣기 (아래 파일 내용 참고)
   - "Save Page" 클릭

3. **반복**
   - 모든 문서 페이지에 대해 반복

---

## 💻 방법 2: Git 명령어로 푸시 (권장)

대량의 페이지를 한 번에 업로드하거나, 로컬에서 편집하려면 Git을 사용하세요.

### 1️⃣ Wiki 저장소 클론

**Git Bash 또는 명령 프롬프트 실행:**

```bash
# 작업할 폴더로 이동 (예: 내 문서)
cd %USERPROFILE%\Documents

# Wiki 저장소 클론
git clone https://github.com/APTOL-7176/Dos.wiki.git

# Wiki 폴더로 이동
cd Dos.wiki
```

### 2️⃣ Wiki 파일 준비

#### 옵션 A: 파일 직접 다운로드

이 저장소의 `docs/` 폴더에서 다음 파일들을 다운로드:
- `Home.md` → Wiki Home 페이지
- `_Sidebar.md` → 사이드바
- `Beginner-Guide.md` → 초보자 가이드
- `Character-Classes.md` → 캐릭터 직업
- `Game-Overview.md` → 게임 개요
- `Gathering-System.md` → 채집 시스템
- `World-Exploration.md` → 던전 탐험
- `Play-in-Browser.md` → 브라우저 플레이

#### 옵션 B: Git으로 메인 저장소 클론 후 복사

```bash
# 메인 저장소 클론 (다른 폴더에)
cd %USERPROFILE%\Documents
git clone https://github.com/APTOL-7176/Dos.git

# Wiki 파일 복사
copy Dos\docs\*.md Dos.wiki\
```

#### 옵션 C: 아래 명령어로 직접 파일 생성

Wiki 폴더에서 아래 파일들을 직접 생성할 수도 있습니다.

### 3️⃣ Git 설정

```bash
# Wiki 폴더에서 실행
cd %USERPROFILE%\Documents\Dos.wiki

# Git 사용자 설정 (처음 한 번만)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 4️⃣ 변경사항 커밋

```bash
# 모든 파일 추가
git add .

# 커밋
git commit -m "Docs: Complete Wiki documentation setup"
```

### 5️⃣ Wiki 푸시

```bash
# 푸시
git push origin master
```

**인증 방법:**
- GitHub 계정 로그인 창이 나타나면 로그인
- Personal Access Token 사용 (권장)

---

## 🔑 Personal Access Token 생성 및 사용

Git 푸시 시 비밀번호 대신 Personal Access Token(PAT)을 사용해야 합니다.

### Token 생성:

1. **GitHub 설정 이동**
   - https://github.com/settings/tokens 접속
   - 또는: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **새 토큰 생성**
   - "Generate new token" → "Generate new token (classic)" 클릭
   - Note: "Dos Wiki Access" (메모)
   - Expiration: 90 days 또는 원하는 기간
   - Scopes: **`repo`** 체크 (전체 저장소 접근)
   - "Generate token" 클릭

3. **토큰 복사**
   - ⚠️ **중요**: 생성된 토큰을 바로 복사하세요 (다시 볼 수 없음)
   - 안전한 곳에 저장 (예: 비밀번호 관리자)

### Token 사용:

```bash
# 푸시 시 비밀번호 입력란에 토큰 붙여넣기
git push origin master

# Username: [GitHub 사용자명]
# Password: [생성한 Personal Access Token 붙여넣기]
```

### Token 저장 (다음부터 입력 불필요):

```bash
# Credential Helper 설정 (Windows)
git config --global credential.helper manager

# 또는 캐시 사용 (15분 동안 저장)
git config --global credential.helper cache
```

---

## 🐛 문제 해결

### Q: "remote: Permission to Dos.wiki.git denied"
**A:**
- Personal Access Token을 사용하세요
- Token에 `repo` 권한이 있는지 확인
- GitHub 계정이 저장소에 대한 쓰기 권한이 있는지 확인

### Q: "Authentication failed"
**A:**
```bash
# Credential 캐시 삭제
git credential-manager erase

# 또는 Windows Credential Manager에서 삭제
# 제어판 → Credential Manager → Windows 자격 증명 → github.com 삭제

# 다시 푸시
git push origin master
```

### Q: 한글이 깨져요
**A:**
```bash
# UTF-8 인코딩 설정
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

명령 프롬프트 UTF-8 설정:
```cmd
chcp 65001
```

### Q: "Updates were rejected because the tip of your current branch is behind"
**A:**
```bash
# 원격 변경사항 가져오기
git pull origin master

# 충돌 해결 후 다시 푸시
git push origin master
```

### Q: Git Bash에서 한글 파일명이 깨져요
**A:**
```bash
# Git Bash 설정
git config --global core.quotepath false
```

---

## 📝 Wiki 파일 구조

```
Dos.wiki/
├── Home.md              # Wiki 홈 페이지 (필수)
├── _Sidebar.md          # 사이드바 네비게이션
├── Beginner-Guide.md    # 초보자 가이드
├── Character-Classes.md # 캐릭터 직업 가이드
├── Game-Overview.md     # 게임 개요
├── Gathering-System.md  # 채집 & 요리 시스템
├── World-Exploration.md # 던전 탐험
└── Play-in-Browser.md   # 브라우저 플레이 가이드
```

**중요:**
- `Home.md`는 Wiki의 메인 페이지입니다 (필수)
- `_Sidebar.md`는 모든 페이지에 표시되는 사이드바입니다
- 파일명은 대소문자를 구분합니다!

---

## ⚡ 빠른 시작 (한 번에 실행)

### PowerShell에서:

```powershell
# 1. Wiki 클론
cd $env:USERPROFILE\Documents
git clone https://github.com/APTOL-7176/Dos.wiki.git
cd Dos.wiki

# 2. 메인 저장소에서 파일 복사 (메인 저장소가 이미 있다면)
Copy-Item ..\Dos\docs\*.md .

# 3. Git 설정
git config user.name "Your Name"
git config user.email "your@email.com"

# 4. 커밋 및 푸시
git add .
git commit -m "Docs: Wiki documentation setup"
git push origin master
```

### Git Bash에서:

```bash
# 1. Wiki 클론
cd ~/Documents
git clone https://github.com/APTOL-7176/Dos.wiki.git
cd Dos.wiki

# 2. 메인 저장소에서 파일 복사
cp ../Dos/docs/*.md .

# 3. Git 설정
git config user.name "Your Name"
git config user.email "your@email.com"

# 4. 커밋 및 푸시
git add .
git commit -m "Docs: Wiki documentation setup"
git push origin master
```

---

## 🔄 Wiki 업데이트 방법

파일을 수정한 후:

```bash
# Wiki 폴더로 이동
cd %USERPROFILE%\Documents\Dos.wiki

# 변경사항 확인
git status

# 변경된 파일 추가
git add .

# 커밋
git commit -m "Docs: Update wiki content"

# 푸시
git push origin master
```

---

## 📚 추가 자료

- **GitHub Wiki 문서**: https://docs.github.com/en/communities/documenting-your-project-with-wikis
- **Git for Windows**: https://git-scm.com/download/win
- **Personal Access Token**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

## 💡 팁

1. **GitHub Desktop 사용**
   - GUI가 편하다면 [GitHub Desktop](https://desktop.github.com/) 사용
   - Wiki 저장소 URL: `https://github.com/APTOL-7176/Dos.wiki.git`
   - Clone → Edit → Commit → Push

2. **VS Code 사용**
   - VS Code에서 Wiki 폴더 열기
   - 내장 Git 기능으로 커밋 및 푸시
   - Markdown 미리보기로 확인

3. **정기 백업**
   - Wiki 내용을 정기적으로 로컬에 백업
   - `git pull`로 최신 상태 유지

---

**Happy Wiki Building! 📚✨**
