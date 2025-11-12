#!/usr/bin/env python3
"""
Dawn of Stellar - 별빛의 여명

메인 엔트리 포인트
"""

import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import initialize_config, get_config
from src.core.logger import get_logger, Loggers
from src.core.event_bus import event_bus


def parse_arguments() -> argparse.Namespace:
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Dawn of Stellar - 별빛의 여명"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="개발 모드로 실행 (모든 클래스 잠금 해제)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드로 실행"
    )

    parser.add_argument(
        "--log",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="로그 레벨 설정"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="설정 파일 경로"
    )

    parser.add_argument(
        "--mobile-server",
        action="store_true",
        help="모바일 서버 모드로 실행"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="서버 포트 (모바일 서버 모드)"
    )

    return parser.parse_args()


def main() -> int:
    """
    메인 함수

    Returns:
        종료 코드 (0: 정상, 1: 에러)
    """
    # 명령줄 인자 파싱
    args = parse_arguments()

    try:
        # 설정 초기화
        config = initialize_config(args.config)

        # 명령줄 옵션으로 설정 오버라이드
        if args.dev:
            config.set("development.enabled", True)
            config.set("development.unlock_all_classes", True)

        if args.debug:
            config.set("development.debug_mode", True)

        # 로거 초기화
        logger = get_logger(Loggers.SYSTEM)
        logger.info("=" * 60)
        logger.info("Dawn of Stellar - 별빛의 여명 시작")
        logger.info(f"버전: {config.get('game.version', '5.0.0')}")
        logger.info(f"언어: {config.language}")
        logger.info(f"개발 모드: {config.development_mode}")
        logger.info(f"디버그 모드: {config.debug_mode}")
        logger.info("=" * 60)

        # TODO: 게임 엔진 초기화
        # from src.core.game_engine import GameEngine
        # engine = GameEngine(config)
        # engine.run()

        print("\n" + "=" * 60)
        print("  Dawn of Stellar - 별빛의 여명")
        print("  Version 5.0.0 (재구조화)")
        print("=" * 60)
        print()
        print("[*] 게임 시스템 초기화 중...")
        print()
        print("[OK] 설정 로드 완료")
        print("[OK] 로거 초기화 완료")
        print("[OK] 이벤트 버스 초기화 완료")
        print()
        print("[!] 게임 엔진이 아직 구현되지 않았습니다.")
        print("    구조와 설정만 준비된 상태입니다.")
        print()
        print("다음 단계:")
        print("  1. src/core/game_engine.py 구현")
        print("  2. 전투 시스템 구현 (src/combat/)")
        print("  3. 캐릭터 시스템 구현 (src/character/)")
        print("  4. 월드 시스템 구현 (src/world/)")
        print()
        print("Claude Code 명령어를 사용하여 개발을 진행하세요:")
        print("  /add-character <이름>  - 새 캐릭터 클래스 추가")
        print("  /add-skill <이름>      - 새 스킬 추가")
        print("  /test                  - 테스트 실행")
        print("  /build                 - 프로젝트 빌드")
        print()

        logger.info("게임 종료")
        return 0

    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
