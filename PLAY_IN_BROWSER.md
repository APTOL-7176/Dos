# 🌐 브라우저에서 Dawn of Stellar 플레이하기

> 설치 없이 브라우저에서 바로 게임을 플레이하는 방법

---

## 🎮 플레이 방법

### 1️⃣ GitHub Codespaces (추천!) ⭐

**가장 쉽고 빠른 방법입니다!**

#### 단계별 가이드:

1. **저장소 페이지 방문**
   - https://github.com/APTOL-7176/Dos

2. **Code 버튼 클릭**
   - 오른쪽 상단의 초록색 "Code" 버튼 클릭

3. **Codespaces 탭 선택**
   - "Codespaces" 탭 클릭 (Local, SSH 옆에 있음)

4. **Codespace 생성**
   - "Create codespace on main" 버튼 클릭
   - 잠시 기다리면 브라우저에서 VS Code가 열립니다

5. **게임 실행**
   - 하단 터미널에서 다음 명령어 입력:
   ```bash
   python main.py
   ```

6. **게임 즐기기!** 🎉
   - 방향키로 이동
   - 숫자 키로 스킬 사용
   - ESC로 메뉴 열기

#### Codespaces 장점:
- ✅ 설치 불필요
- ✅ 브라우저에서 바로 실행
- ✅ 무료 (월 60시간)
- ✅ 빠른 속도
- ✅ 자동 환경 설정

---

### 2️⃣ Gitpod

**또 다른 브라우저 기반 개발 환경**

#### 단계별 가이드:

1. **Gitpod 링크 클릭**
   - https://gitpod.io/#https://github.com/APTOL-7176/Dos

2. **자동으로 환경 구성**
   - 잠시 기다리면 VS Code가 열립니다

3. **게임 실행**
   ```bash
   python main.py
   ```

#### Gitpod 장점:
- ✅ 설치 불필요
- ✅ 빠른 시작
- ✅ 무료 플랜 제공

---

### 3️⃣ 원클릭 버튼 (준비 중)

**곧 추가될 예정:**
- [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/APTOL-7176/Dos)
- [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=master&repo=APTOL-7176/Dos)

---

## 🖥️ 시스템 요구사항

### 브라우저:
- Chrome, Edge, Firefox, Safari (최신 버전)
- 인터넷 연결 필요

### GitHub 계정:
- Codespaces 사용 시 GitHub 계정 필요
- 무료 계정도 가능 (월 60시간 무료)

---

## 📋 Codespaces 무료 제한

GitHub 무료 계정:
- **월 60시간** Codespaces 사용 가능
- 2-core 머신 기준
- 초과 시 자동 중지

**팁**: 게임 종료 후 Codespace를 삭제하면 시간 절약!

---

## 🎯 게임 조작법

### 메뉴 탐색:
- **방향키**: 메뉴 이동
- **Enter**: 선택
- **ESC**: 뒤로 가기 / 메뉴 열기

### 던전 탐험:
- **방향키 / WASD**: 이동
- **Shift + 방향키**: 대시

### 전투:
- **1~6**: 스킬 선택
- **Q**: BRV 공격
- **E**: HP 공격
- **R**: 궁극기
- **Space**: 아이템 사용

### 기타:
- **I**: 인벤토리
- **C**: 캐릭터 정보
- **M**: 맵
- **ESC**: 메뉴

---

## 🐛 문제 해결

### Q: Codespace가 시작되지 않아요
**A**:
1. 브라우저 새로고침 (Ctrl + F5)
2. 다른 브라우저 시도
3. GitHub 로그인 상태 확인

### Q: 게임이 실행되지 않아요
**A**:
```bash
# 의존성 재설치
pip install -r requirements.txt

# 게임 실행
python main.py
```

### Q: 화면이 깨져 보여요
**A**:
1. 터미널 크기 조정 (최소 80x50)
2. 폰트 크기 조정
3. 전체 화면 모드 사용

### Q: 한글이 깨져요
**A**:
```bash
# UTF-8 설정 확인
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# 게임 실행
python main.py
```

---

## 💡 플레이 팁

### 1. 첫 플레이 시:
- **난이도**: "평온" 선택
- **직업**: 전사 또는 성직자 추천
- **튜토리얼**: 게임 내 도움말 확인

### 2. 세이브 파일:
- Codespaces는 세이브 파일을 보관합니다
- 같은 Codespace에서 계속 플레이 가능
- Codespace 삭제 시 세이브 파일도 삭제됨

### 3. 성능 최적화:
- 터미널 크기 최적화
- 불필요한 탭 닫기
- 안정적인 인터넷 연결 유지

---

## 🚀 빠른 시작 명령어 모음

```bash
# Codespace 생성 후 바로 실행할 명령어들

# 1. 의존성 확인
pip list | grep tcod

# 2. 기본 모드로 게임 시작
python main.py

# 3. 개발 모드 (모든 직업 해금)
python main.py --dev

# 4. 디버그 모드
python main.py --debug --log=DEBUG

# 5. 테스트 실행
pytest tests/ -v
```

---

## 📚 추가 자료

- **게임 가이드**: [Wiki 홈](https://github.com/APTOL-7176/Dos/wiki)
- **초보자 가이드**: [Beginner Guide](https://github.com/APTOL-7176/Dos/wiki/Beginner-Guide)
- **직업 가이드**: [Character Classes](https://github.com/APTOL-7176/Dos/wiki/Character-Classes)
- **버그 리포트**: [Issues](https://github.com/APTOL-7176/Dos/issues)

---

## 🎊 즐거운 게임 되세요!

**May the stars guide you! ⭐**

---

## 📝 주의사항

1. **Codespaces 시간 관리**
   - 무료 계정: 월 60시간
   - 사용 후 Codespace 중지 또는 삭제 권장

2. **세이브 파일 백업**
   - Codespace 삭제 전 세이브 파일 다운로드
   - `saves/` 폴더 압축 후 로컬에 저장

3. **인터넷 연결**
   - 안정적인 연결 필요
   - 끊김 시 자동 재연결 시도

4. **브라우저 호환성**
   - Chrome/Edge 추천 (최상의 성능)
   - Firefox, Safari도 사용 가능
   - 모바일 브라우저는 지원 제한적

---

**Happy Playing! 🎮✨**
