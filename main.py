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

        # TCOD 디스플레이 초기화
        from src.ui.tcod_display import get_display
        from src.ui.main_menu import run_main_menu, MenuResult

        display = get_display()
        logger.info("TCOD 디스플레이 초기화 완료")

        # 메인 게임 루프
        while True:
            # 메인 메뉴 실행
            menu_result = run_main_menu(display.console, display.context)
            logger.info(f"메인 메뉴 결과: {menu_result.value}")

            if menu_result == MenuResult.QUIT:
                break
            elif menu_result == MenuResult.NEW_GAME:
                logger.info("새 게임 시작 - 파티 구성")

                # 파티 구성
                from src.ui.party_setup import run_party_setup
                party = run_party_setup(display.console, display.context)

                if party:
                    logger.info(f"파티 구성 완료: {len(party)}명")
                    for i, member in enumerate(party):
                        logger.info(
                            f"  {i+1}. {member.character_name} ({member.job_name})"
                        )

                    # 특성 선택
                    from src.ui.trait_selection import run_trait_selection
                    trait_selections = run_trait_selection(
                        display.console,
                        display.context,
                        party
                    )

                    if trait_selections:
                        logger.info(f"특성 선택 완료: {len(trait_selections)}명")
                        for traits in trait_selections:
                            logger.info(
                                f"  {traits.character_name} ({traits.job_name}): "
                                f"{', '.join([t.name for t in traits.selected_traits])}"
                            )

                        # 패시브 선택
                        from src.ui.passive_selection import run_passive_selection
                        passive_selection = run_passive_selection(
                            display.console,
                            display.context
                        )

                        if passive_selection:
                            logger.info(
                                f"패시브 선택 완료: {len(passive_selection.passives)}개, "
                                f"총 코스트 {passive_selection.total_cost}"
                            )
                            for passive in passive_selection.passives:
                                logger.info(
                                    f"  [{passive.cost}] {passive.name}"
                                )

                            # 게임 시작!
                            logger.info("=== 게임 시작! ===")
                            from src.world.dungeon_generator import DungeonGenerator
                            from src.world.exploration import ExplorationSystem
                            from src.ui.world_ui import run_exploration

                            floor_number = 1

                            while True:
                                # 던전 생성
                                dungeon_gen = DungeonGenerator(width=80, height=50)
                                dungeon = dungeon_gen.generate(floor_number)

                                # 탐험 시작
                                exploration = ExplorationSystem(dungeon, party)
                                result = run_exploration(
                                    display.console,
                                    display.context,
                                    exploration
                                )

                                logger.info(f"탐험 결과: {result}")

                                if result == "quit":
                                    logger.info("게임 종료")
                                    break
                                elif result == "combat":
                                    # TODO: 전투 시작
                                    logger.info("전투 시작 (구현 예정)")
                                    break
                                elif result == "floor_down":
                                    floor_number += 1
                                    logger.info(f"다음 층으로: {floor_number}층")
                                    continue
                                elif result == "floor_up":
                                    if floor_number > 1:
                                        floor_number -= 1
                                        logger.info(f"이전 층으로: {floor_number}층")
                                        continue
                                    else:
                                        logger.info("던전 탈출!")
                                        break

                            break
                        else:
                            logger.info("패시브 선택 취소 - 메인 메뉴로")
                            continue
                    else:
                        logger.info("특성 선택 취소 - 메인 메뉴로")
                        continue
                else:
                    logger.info("파티 구성 취소 - 메인 메뉴로")
                    continue
            elif menu_result == MenuResult.CONTINUE:
                logger.info("게임 계속하기 (구현 예정)")
                # TODO: 세이브 로드
                break
            elif menu_result == MenuResult.SHOP:
                logger.info("상점 열기 (구현 예정)")
                # TODO: 상점 UI
                break
            elif menu_result == MenuResult.SETTINGS:
                logger.info("설정 열기 (구현 예정)")
                # TODO: 설정 UI
                break

        # 정리
        display.close()

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
