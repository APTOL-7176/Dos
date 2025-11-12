# Dawn of Stellar - 별빛의 여명

Python 기반 로그라이크 RPG with Final Fantasy-style Brave Combat

![Version](https://img.shields.io/badge/version-5.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 소개

**Dawn of Stellar**는 Final Fantasy 시리즈의 ATB + Brave 전투 시스템을 결합한 로그라이크 RPG입니다.
28개의 독특한 캐릭터 클래스, 절차적으로 생성되는 던전, AI 동료 시스템, 그리고 멀티플레이어를 지원합니다.

### 주요 특징

- 🎮 **Final Fantasy 스타일 전투**: ATB(Active Time Battle) + Brave 시스템
- ⚔️ **28개 캐릭터 클래스**: 각각 고유한 스킬과 플레이 스타일
- 🧠 **전술적 AI 동료**: 지능적인 의사결정 트리 기반 AI
- 🎲 **절차적 던전 생성**: 매번 다른 던전 경험
- 🌐 **멀티플레이어**: 협동 및 대전 모드
- 🇰🇷 **완전한 한국어 지원**: UI 및 게임 콘텐츠
- 📱 **모바일 지원**: Flutter 기반 크로스플랫폼

## 빠른 시작

### 요구사항

- Python 3.10 이상
- pip (Python 패키지 관리자)

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/dawn-of-stellar.git
cd dawn-of-stellar

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 게임 실행
python main.py
```

### 개발 모드

```bash
# 개발 모드 (모든 클래스 잠금 해제)
python main.py --dev

# 디버그 모드 (상세 로그)
python main.py --debug --log=DEBUG
```

## 게임 시스템

### Brave Combat System

**BRV (Brave) 공격**으로 Brave 포인트를 축적하고, **HP 공격**으로 실제 데미지를 가합니다.

```
[전투 흐름]
1. BRV 공격 → 적의 BRV를 0으로 만듦 (BREAK!)
2. BREAK 상태에서 HP 공격 → 보너스 데미지
3. 적 HP를 0으로 만들면 승리!
```

**BREAK 시스템**:
- 적의 BRV를 0으로 만들면 BREAK 발동
- BREAK 중 HP 공격 시 보너스 데미지 (1.5x)
- 적은 BREAK 중 행동 불가 (스턴)

### ATB (Active Time Battle) System

- 속도 스탯에 따라 ATB 게이지가 실시간으로 증가
- 게이지가 1000에 도달하면 행동 가능
- 전략적인 타이밍과 스킬 선택이 중요

### 캐릭터 클래스

28개의 다양한 클래스:

| 물리 계열 | 마법 계열 | 지원 계열 | 특수 계열 |
|----------|----------|----------|----------|
| 전사 | 흑마법사 | 백마법사 | 용기사 |
| 기사 | 적마법사 | 음유시인 | 소환사 |
| 궁수 | 청마법사 | 춤꾼 | 시공마법사 |
| 닌자 | 환술사 | 학자 | 마검사 |
| 암살자 | 원소술사 | 점성술사 | 붉은마법사 |
| 몽크 | 파괴술사 | 음양사 | 루프스 |
| 창술사 | | 현자 | 기공사 |

각 클래스는 고유한:
- 기본 스탯 분포
- 6개의 전용 스킬
- 2개의 패시브 능력
- 독특한 플레이 스타일

### 스킬 시스템

스킬 타입:
- **BRV 공격**: Brave 포인트 축적
- **HP 공격**: 축적된 Brave로 HP 데미지
- **복합 공격**: BRV + HP 동시 공격
- **지원**: 아군 버프
- **디버프**: 적 약화
- **궁극기**: 강력한 특수 기술

### AI 동료 시스템

전술적 AI가 상황에 맞는 최적의 행동을 선택:

```
우선순위:
1. 긴급 힐 (HP < 30%)
2. 지원 힐 (HP < 60%)
3. 궁극기 사용 (게이지 100%)
4. 전술 스킬 (상황 판단)
5. HP 공격 (BRV 충분)
6. BRV 공격 (기본)
```

AI 성격:
- **공격적**: HP 공격 우선
- **방어적**: BRV 축적 우선
- **균형**: 상황 판단
- **지원**: 아군 버프 우선

## 프로젝트 구조

```
NewProject/
├── src/              # 소스 코드
│   ├── core/        # 핵심 시스템
│   ├── combat/      # 전투 시스템
│   ├── character/   # 캐릭터 시스템
│   ├── world/       # 월드 시스템
│   ├── ai/          # AI 시스템
│   └── ...
├── data/            # 게임 데이터 (YAML)
├── assets/          # 에셋 (오디오, 폰트)
├── tests/           # 테스트
└── docs/            # 문서
```

상세 구조는 [`PROJECT_DESIGN.md`](PROJECT_DESIGN.md) 참조

## 개발

### 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 유닛 테스트만
pytest tests/unit/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=html
```

### 코드 품질 검사

```bash
# Type checking
mypy src/

# Linting
pylint src/

# Code formatting
black src/
```

### 빌드

```bash
# 전체 빌드 프로세스
python scripts/build.py

# 또는 Claude Code 명령어
/build
```

### 커스텀 명령어 (Claude Code)

Claude Code를 사용하는 경우:

- `/test` - 테스트 실행
- `/run [mode]` - 게임 실행
- `/build` - 프로젝트 빌드
- `/add-character <name>` - 새 캐릭터 클래스 추가
- `/add-skill <name>` - 새 스킬 추가
- `/debug-combat` - 전투 디버깅

## 기여하기

기여는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

자세한 내용은 [`CONTRIBUTING.md`](CONTRIBUTING.md) 참조

## 문서

- **프로젝트 설계**: [`PROJECT_DESIGN.md`](PROJECT_DESIGN.md)
- **Claude Code 가이드**: [`.claude/CLAUDE.md`](.claude/CLAUDE.md)
- **API 문서**: [`docs/api/`](docs/api/)
- **사용자 가이드**: [`docs/guides/`](docs/guides/)

## 라이선스

MIT License - 자세한 내용은 [`LICENSE`](LICENSE) 참조

## 크레딧

### 영감을 받은 게임
- **Final Fantasy** 시리즈 (ATB, Brave 시스템)
- **Dissidia Final Fantasy** (Brave Combat)
- **Slay the Spire** (로그라이크 구조)
- **Darkest Dungeon** (턴제 전투)

### 개발 도구
- Python 3.10+
- pygame (UI/Audio)
- pytest (Testing)
- mypy (Type Checking)
- Claude Code (AI-assisted Development)

## 연락처

- 이슈 트래킹: [GitHub Issues](https://github.com/yourusername/dawn-of-stellar/issues)
- 프로젝트 링크: [https://github.com/yourusername/dawn-of-stellar](https://github.com/yourusername/dawn-of-stellar)

---

**Made with ❤️ and ☕ by the Dawn of Stellar Team**
