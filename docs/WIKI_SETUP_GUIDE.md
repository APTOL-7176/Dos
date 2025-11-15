# GitHub Wiki 설정 가이드

> Dawn of Stellar 위키를 GitHub Wiki로 배포하는 방법

---

## 📖 개요

현재 `/docs` 폴더에 있는 마크다운 문서들을 GitHub Wiki로 배포하는 방법입니다.

---

## 1단계: GitHub에서 Wiki 활성화

### 웹 브라우저에서:

1. **GitHub 저장소 접속**
   - https://github.com/APTOL-7176/Dos

2. **Settings 탭 클릭**
   - 저장소 상단 메뉴에서 "Settings" 클릭

3. **Features 섹션 찾기**
   - 왼쪽 사이드바에서 "General" 선택 (기본값)
   - 아래로 스크롤하여 "Features" 섹션 찾기

4. **Wikis 활성화**
   - "Wikis" 체크박스 체크
   - 자동 저장됨

5. **Wiki 탭 확인**
   - 저장소 상단에 "Wiki" 탭이 생성됨
   - Wiki 탭 클릭

6. **초기 페이지 생성**
   - "Create the first page" 버튼 클릭
   - 제목: "Home"
   - 내용: 임시 텍스트 입력
   - "Save Page" 클릭

---

## 2단계: Wiki Git 저장소 클론

Wiki가 활성화되면, Wiki 전용 Git 저장소가 생성됩니다.

```bash
# 작업 디렉토리로 이동
cd /home/user

# Wiki 저장소 클론
git clone https://github.com/APTOL-7176/Dos.wiki.git

# Wiki 디렉토리로 이동
cd Dos.wiki
```

---

## 3단계: Docs 파일 복사

```bash
# docs 파일들을 wiki 저장소로 복사
cp /home/user/Dos/docs/*.md /home/user/Dos.wiki/

# Home.md 생성 (README.md를 Home.md로)
cp /home/user/Dos/docs/README.md /home/user/Dos.wiki/Home.md
```

---

## 4단계: 사이드바 생성 (선택사항)

Wiki 사이드바를 만들면 탐색이 편리합니다.

```bash
# _Sidebar.md 파일 생성
cat > /home/user/Dos.wiki/_Sidebar.md << 'EOF'
# Dawn of Stellar Wiki

## 시작하기
- [홈](Home)
- [게임 개요](game-overview)
- [초보자 가이드](beginner-guide)

## 핵심 시스템
- [전투 시스템](combat-system)
- [직업 가이드](character-classes)
- [요리 시스템](cooking)
- [채집 시스템](gathering-system)

## 월드
- [던전 탐험](world-exploration)
- [직업 메커니즘](JOB_MECHANISMS)

## 기타
- [아키텍처](architecture)
- [기본 공격 시스템](BASIC_ATTACKS_SYSTEM)
EOF
```

---

## 5단계: Git 커밋 및 푸시

```bash
cd /home/user/Dos.wiki

# 모든 파일 추가
git add .

# 커밋
git commit -m "docs: 초기 Wiki 문서 추가

- 게임 개요
- 직업 가이드 (33개 직업)
- 전투 시스템
- 요리 시스템 (52개 레시피)
- 채집 시스템 (60개 식재료)
- 던전 탐험
- 초보자 가이드"

# 푸시
git push origin master
```

---

## 6단계: Wiki 확인

1. **GitHub Wiki 접속**
   - https://github.com/APTOL-7176/Dos/wiki

2. **페이지 확인**
   - Home 페이지가 README 내용으로 표시됨
   - 사이드바에서 다른 페이지 탐색 가능

3. **링크 작동 확인**
   - 각 문서 간 링크가 정상 작동하는지 확인

---

## Wiki 페이지 목록

현재 `/docs` 폴더에 있는 문서들:

### 주요 가이드
- **Home.md** (README.md) - 메인 위키 페이지
- **game-overview.md** - 게임 전체 개요
- **beginner-guide.md** - 초보자 완벽 가이드

### 시스템 가이드
- **combat-system.md** - ATB + BRV 전투 시스템
- **character-classes.md** - 33개 직업 완전 분석
- **cooking.md** - 52개 요리 레시피
- **gathering-system.md** - 채집 시스템 (60개 식재료)
- **world-exploration.md** - 던전 탐험 가이드

### 기술 문서
- **architecture.md** - 시스템 아키텍처
- **JOB_MECHANISMS.md** - 직업 메커니즘
- **BASIC_ATTACKS_SYSTEM.md** - 기본 공격 시스템
- **CHARACTER_MIGRATION.md** - 캐릭터 마이그레이션
- **status_effects_migration.md** - 상태 효과 마이그레이션

---

## 자동화 스크립트

매번 수동으로 복사하기 번거로우면 스크립트를 사용하세요:

```bash
#!/bin/bash
# sync-wiki.sh - docs를 wiki로 동기화

cd /home/user/Dos.wiki

# docs 파일 복사
cp /home/user/Dos/docs/*.md .

# README를 Home으로
cp /home/user/Dos/docs/README.md Home.md

# Git 커밋 및 푸시
git add .
git commit -m "docs: Wiki 문서 업데이트"
git push origin master

echo "Wiki 동기화 완료!"
```

**사용 방법**:
```bash
chmod +x sync-wiki.sh
./sync-wiki.sh
```

---

## 주의사항

### 1. 링크 형식

GitHub Wiki에서는 링크 형식이 다릅니다:

**docs (일반 마크다운)**:
```markdown
[전투 시스템](combat-system.md)
```

**Wiki**:
```markdown
[전투 시스템](combat-system)
```

`.md` 확장자를 제거해야 합니다.

### 2. 이미지 경로

이미지를 사용하려면:
1. Wiki 저장소의 `images/` 폴더에 이미지 업로드
2. 마크다운에서 상대 경로 사용

```markdown
![이미지 설명](images/screenshot.png)
```

### 3. 한글 페이지명

한글 페이지명은 URL 인코딩되므로, 영문 파일명을 추천합니다.

---

## 트러블슈팅

### Q: Wiki 탭이 안 보여요
**A**: Settings → Features에서 "Wikis" 체크박스를 활성화했는지 확인하세요.

### Q: git push가 실패해요
**A**:
1. GitHub 로그인 확인
2. Wiki 저장소 권한 확인
3. `git pull` 먼저 실행 후 다시 push

### Q: 페이지가 깨져 보여요
**A**:
1. 마크다운 문법 확인
2. 링크에서 `.md` 확장자 제거
3. 이미지 경로 확인

---

## 추가 커스터마이징

### Footer 추가

```bash
# _Footer.md 생성
cat > _Footer.md << 'EOF'
---
**Dawn of Stellar** | Version 5.0.0 | [GitHub](https://github.com/APTOL-7176/Dos)
EOF
```

### 페이지 순서 조정

사이드바(`_Sidebar.md`)에서 원하는 순서로 링크를 배치하세요.

---

## 완료!

이제 GitHub Wiki가 준비되었습니다:
- https://github.com/APTOL-7176/Dos/wiki

**즐거운 문서 작성 되세요! Happy Documenting! 📚**
