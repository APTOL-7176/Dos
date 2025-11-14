#!/usr/bin/env python3
"""
버그 수정 검증 스크립트
"""

import sys
sys.path.insert(0, '/home/user/Dos')

from src.world.enemy_generator import ENEMY_TEMPLATES
from src.combat.atb_system import ATBSystem
from src.combat.combat_manager import CombatManager, CombatState
from src.core.config import initialize_config

# 설정 초기화
initialize_config()


def test_enemy_balance():
    """1레벨 적 밸런싱 확인"""
    print("\n=== 1레벨 적 밸런싱 테스트 ===")

    # 슬라임 스탯 확인
    slime = ENEMY_TEMPLATES["slime"]
    print(f"\n슬라임 (Lv {slime.level}):")
    print(f"  HP: {slime.hp} (이전: 30)")
    print(f"  물리 공격력: {slime.physical_attack} (이전: 8)")
    print(f"  물리 방어력: {slime.physical_defense} (이전: 5)")
    print(f"  속도: {slime.speed} (이전: 5)")

    # 고블린 스탯 확인
    goblin = ENEMY_TEMPLATES["goblin"]
    print(f"\n고블린 (Lv {goblin.level}):")
    print(f"  HP: {goblin.hp} (이전: 45)")
    print(f"  물리 공격력: {goblin.physical_attack} (이전: 12)")
    print(f"  물리 방어력: {goblin.physical_defense} (이전: 8)")
    print(f"  속도: {goblin.speed} (이전: 8)")

    # 늑대 스탯 확인
    wolf = ENEMY_TEMPLATES["wolf"]
    print(f"\n늑대 (Lv {wolf.level}):")
    print(f"  HP: {wolf.hp} (이전: 55)")
    print(f"  물리 공격력: {wolf.physical_attack} (이전: 15)")
    print(f"  물리 방어력: {wolf.physical_defense} (이전: 10)")
    print(f"  속도: {wolf.speed} (이전: 12)")

    # 검증
    assert slime.hp >= 60, "슬라임 HP가 너무 낮습니다"
    assert slime.physical_attack >= 15, "슬라임 공격력이 너무 낮습니다"
    assert goblin.hp >= 80, "고블린 HP가 너무 낮습니다"
    assert wolf.hp >= 90, "늑대 HP가 너무 낮습니다"

    print("\n✓ 적 밸런싱 테스트 통과!")


def test_atb_system():
    """ATB 시스템 동작 확인"""
    print("\n=== ATB 시스템 테스트 ===")

    # 간단한 캐릭터 클래스
    class DummyCharacter:
        def __init__(self, name, speed):
            self.name = name
            self.speed = speed

    atb = ATBSystem()

    # 전투원 등록
    player = DummyCharacter("플레이어", 10)
    enemy = DummyCharacter("슬라임", 8)

    atb.register_combatant(player)
    atb.register_combatant(enemy)

    print(f"\n초기 ATB 게이지:")
    print(f"  플레이어: {atb.get_gauge(player).current}")
    print(f"  슬라임: {atb.get_gauge(enemy).current}")

    # 일반 업데이트 (시간 흐름)
    print(f"\n일반 업데이트 (is_player_turn=False):")
    for i in range(5):
        atb.update(delta_time=1.0, is_player_turn=False)
        print(f"  프레임 {i+1} - 플레이어: {atb.get_gauge(player).current:.1f}, 슬라임: {atb.get_gauge(enemy).current:.1f}")

    player_gauge_before = atb.get_gauge(player).current

    # 플레이어 턴 중 업데이트 (시간 정지)
    print(f"\n플레이어 턴 중 업데이트 (is_player_turn=True):")
    for i in range(5):
        atb.update(delta_time=1.0, is_player_turn=True)
        print(f"  프레임 {i+1} - 플레이어: {atb.get_gauge(player).current:.1f}, 슬라임: {atb.get_gauge(enemy).current:.1f}")

    player_gauge_after = atb.get_gauge(player).current

    # 검증: 플레이어 턴 중에는 ATB가 증가하지 않아야 함
    assert player_gauge_before == player_gauge_after, "플레이어 턴 중 ATB가 증가했습니다!"

    print("\n✓ ATB 시스템 테스트 통과!")
    print("  → 플레이어 턴 중 ATB가 정지하는 것을 확인했습니다.")


def test_combat_state():
    """전투 상태 전환 테스트"""
    print("\n=== 전투 상태 전환 테스트 ===")

    combat = CombatManager()

    print(f"초기 상태: {combat.state}")
    assert combat.state == CombatState.NOT_STARTED

    # 전투 시작
    class DummyCharacter:
        def __init__(self, name):
            self.name = name
            self.speed = 10
            self.current_brv = 0
            self.max_brv = 1000
            self.is_alive = True

    allies = [DummyCharacter("플레이어")]
    enemies = [DummyCharacter("슬라임")]

    combat.start_combat(allies, enemies)
    print(f"전투 시작 후: {combat.state}")
    assert combat.state == CombatState.IN_PROGRESS

    # 상태 변경 테스트
    combat.state = CombatState.PLAYER_TURN
    print(f"플레이어 턴으로 변경: {combat.state}")
    assert combat.state == CombatState.PLAYER_TURN

    combat.state = CombatState.IN_PROGRESS
    print(f"진행 중으로 변경: {combat.state}")
    assert combat.state == CombatState.IN_PROGRESS

    print("\n✓ 전투 상태 전환 테스트 통과!")


if __name__ == "__main__":
    try:
        test_enemy_balance()
        test_atb_system()
        test_combat_state()

        print("\n" + "="*50)
        print("모든 테스트 통과! ✓")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
