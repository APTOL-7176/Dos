"""
Combat Manager - 전투 관리자

ATB, Brave, Damage 시스템을 통합하여 전투 흐름 제어
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from src.core.config import get_config
from src.core.logger import get_logger
from src.core.event_bus import event_bus, Events
from src.combat.atb_system import get_atb_system, ATBSystem
from src.combat.brave_system import get_brave_system, BraveSystem
from src.combat.damage_calculator import get_damage_calculator, DamageCalculator


class CombatState(Enum):
    """전투 상태"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"


class ActionType(Enum):
    """행동 타입"""
    BRV_ATTACK = "brv_attack"
    HP_ATTACK = "hp_attack"
    BRV_HP_ATTACK = "brv_hp_attack"
    SKILL = "skill"
    ITEM = "item"
    DEFEND = "defend"
    FLEE = "flee"


class CombatManager:
    """
    전투 관리자

    전투 흐름 제어 및 시스템 통합
    """

    def __init__(self) -> None:
        self.logger = get_logger("combat")
        self.config = get_config()

        # 서브시스템
        self.atb: ATBSystem = get_atb_system()
        self.brave: BraveSystem = get_brave_system()
        self.damage_calc: DamageCalculator = get_damage_calculator()

        # 전투 상태
        self.state: CombatState = CombatState.NOT_STARTED
        self.turn_count = 0
        self.current_actor: Optional[Any] = None

        # 전투원
        self.allies: List[Any] = []
        self.enemies: List[Any] = []

        # 콜백
        self.on_combat_end: Optional[Callable[[CombatState], None]] = None
        self.on_turn_start: Optional[Callable[[Any], None]] = None
        self.on_action_complete: Optional[Callable[[Any, Dict], None]] = None

    def start_combat(self, allies: List[Any], enemies: List[Any]) -> None:
        """
        전투 시작

        Args:
            allies: 아군 리스트
            enemies: 적군 리스트
        """
        self.logger.info("전투 시작!")

        # 전투원 설정
        self.allies = allies
        self.enemies = enemies
        self.turn_count = 0
        self.state = CombatState.IN_PROGRESS

        # ATB 시스템에 전투원 등록
        for ally in allies:
            self.atb.register_combatant(ally)
            self.brave.initialize_brv(ally)

        for enemy in enemies:
            self.atb.register_combatant(enemy)
            self.brave.initialize_brv(enemy)

        # 이벤트 발행
        event_bus.publish(Events.COMBAT_START, {
            "allies": allies,
            "enemies": enemies
        })

        self.logger.debug(
            f"전투 참여자: 아군 {len(allies)}명, 적군 {len(enemies)}명"
        )

    def update(self, delta_time: float = 1.0) -> None:
        """
        전투 업데이트 (매 프레임 호출)

        Args:
            delta_time: 경과 시간
        """
        if self.state not in [CombatState.IN_PROGRESS, CombatState.PLAYER_TURN, CombatState.ENEMY_TURN]:
            return

        # ATB 시스템 업데이트
        is_player_turn = self.state == CombatState.PLAYER_TURN
        self.atb.update(delta_time, is_player_turn)

        # 승리/패배 판정
        self._check_battle_end()

    def execute_action(
        self,
        actor: Any,
        action_type: ActionType,
        target: Optional[Any] = None,
        skill: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        행동 실행

        Args:
            actor: 행동자
            action_type: 행동 타입
            target: 대상
            skill: 스킬 (있는 경우)
            **kwargs: 추가 옵션

        Returns:
            행동 결과
        """
        self.current_actor = actor
        result = {}

        self.logger.debug(
            f"행동 실행: {actor.name} → {action_type.value}",
            {"target": getattr(target, "name", None) if target else None}
        )

        # 행동 타입별 처리
        if action_type == ActionType.BRV_ATTACK:
            result = self._execute_brv_attack(actor, target, skill, **kwargs)
        elif action_type == ActionType.HP_ATTACK:
            result = self._execute_hp_attack(actor, target, skill, **kwargs)
        elif action_type == ActionType.BRV_HP_ATTACK:
            result = self._execute_brv_hp_attack(actor, target, skill, **kwargs)
        elif action_type == ActionType.SKILL:
            result = self._execute_skill(actor, target, skill, **kwargs)
        elif action_type == ActionType.ITEM:
            result = self._execute_item(actor, target, **kwargs)
        elif action_type == ActionType.DEFEND:
            result = self._execute_defend(actor, **kwargs)
        elif action_type == ActionType.FLEE:
            result = self._execute_flee(actor, **kwargs)

        # ATB 소비
        self.atb.consume_atb(actor)

        # 턴 종료 처리
        self._on_turn_end(actor)

        # 콜백 호출
        if self.on_action_complete:
            self.on_action_complete(actor, result)

        # 이벤트 발행
        event_bus.publish(Events.COMBAT_ACTION, {
            "actor": actor,
            "action_type": action_type.value,
            "target": target,
            "result": result
        })

        self.current_actor = None
        return result

    def _execute_brv_attack(
        self,
        attacker: Any,
        defender: Any,
        skill: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """BRV 공격 실행"""
        # 스킬 배율
        skill_multiplier = getattr(skill, "brv_multiplier", 1.0) if skill else 1.0

        # 데미지 계산
        damage_result = self.damage_calc.calculate_brv_damage(
            attacker, defender, skill_multiplier, **kwargs
        )

        # BRV 공격 적용
        brv_result = self.brave.brv_attack(attacker, defender, damage_result.final_damage)

        return {
            "action": "brv_attack",
            "damage": damage_result.final_damage,
            "is_critical": damage_result.is_critical,
            "brv_stolen": brv_result["brv_stolen"],
            "actual_gain": brv_result["actual_gain"],
            "is_break": brv_result["is_break"]
        }

    def _execute_hp_attack(
        self,
        attacker: Any,
        defender: Any,
        skill: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """HP 공격 실행"""
        if attacker.current_brv <= 0:
            self.logger.warning(f"{attacker.name}: BRV가 0이라 HP 공격 불가")
            return {"action": "hp_attack", "error": "no_brv"}

        # 스킬 배율
        hp_multiplier = getattr(skill, "hp_multiplier", 1.0) if skill else 1.0

        # BREAK 상태 확인
        is_break = self.brave.is_broken(defender)

        # 데미지 계산
        damage_result, wound_damage = self.damage_calc.calculate_hp_damage(
            attacker, defender, attacker.current_brv, hp_multiplier, is_break, **kwargs
        )

        # 실제 HP 감소 (HP 공격 전에 적용)
        if hasattr(defender, "take_damage"):
            actual_damage = defender.take_damage(damage_result.final_damage)
        else:
            actual_damage = damage_result.final_damage

        # HP 공격 적용 (BRV 소비)
        hp_result = self.brave.hp_attack(attacker, defender, hp_multiplier)

        return {
            "action": "hp_attack",
            "hp_damage": actual_damage,
            "wound_damage": wound_damage,
            "brv_consumed": hp_result["brv_consumed"],
            "is_break_bonus": is_break
        }

    def _execute_brv_hp_attack(
        self,
        attacker: Any,
        defender: Any,
        skill: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """BRV + HP 복합 공격 실행"""
        # 1. BRV 공격
        brv_attack_result = self._execute_brv_attack(attacker, defender, skill, **kwargs)

        # 2. HP 공격 (BRV가 있으면)
        if attacker.current_brv > 0:
            hp_attack_result = self._execute_hp_attack(attacker, defender, skill, **kwargs)
        else:
            hp_attack_result = {"hp_damage": 0, "wound_damage": 0, "brv_consumed": 0}

        # 결과 병합
        combined_result = {
            "action": "brv_hp_attack",
            "is_combo": True
        }

        # BRV 결과 추가
        for key in ["damage", "is_critical", "brv_stolen", "actual_gain", "is_break"]:
            if key in brv_attack_result:
                combined_result[f"brv_{key}"] = brv_attack_result[key]

        # HP 결과 추가
        for key in ["hp_damage", "wound_damage", "brv_consumed", "is_break_bonus"]:
            if key in hp_attack_result:
                combined_result[key] = hp_attack_result[key]

        return combined_result

    def _execute_skill(
        self,
        actor: Any,
        target: Optional[Any] = None,
        skill: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """스킬 실행"""
        # TODO: 스킬 시스템 연동
        return {
            "action": "skill",
            "skill_name": getattr(skill, "name", "Unknown") if skill else "Unknown"
        }

    def _execute_item(self, actor: Any, target: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        """아이템 사용"""
        # TODO: 아이템 시스템 연동
        return {
            "action": "item"
        }

    def _execute_defend(self, actor: Any, **kwargs) -> Dict[str, Any]:
        """방어 태세"""
        # 방어 버프 적용 (TODO: 버프 시스템 연동)
        return {
            "action": "defend"
        }

    def _execute_flee(self, actor: Any, **kwargs) -> Dict[str, Any]:
        """도망"""
        # 도망 확률 계산
        flee_chance = 0.5  # 기본 50%
        import random
        if random.random() < flee_chance:
            self.state = CombatState.FLED
            return {
                "action": "flee",
                "success": True
            }
        else:
            return {
                "action": "flee",
                "success": False
            }

    def _on_turn_end(self, actor: Any) -> None:
        """
        턴 종료 처리

        Args:
            actor: 행동한 캐릭터
        """
        # 턴 시작 시 INT BRV 회복
        self.brave.recover_int_brv(actor)

        # 이벤트 발행
        event_bus.publish(Events.COMBAT_TURN_END, {
            "actor": actor,
            "turn": self.turn_count
        })

        self.turn_count += 1

    def _check_battle_end(self) -> None:
        """승리/패배 판정"""
        # 모든 적이 죽었는가?
        if all(self._is_defeated(enemy) for enemy in self.enemies):
            self._end_combat(CombatState.VICTORY)
            return

        # 모든 아군이 죽었는가?
        if all(self._is_defeated(ally) for ally in self.allies):
            self._end_combat(CombatState.DEFEAT)
            return

    def _is_defeated(self, character: Any) -> bool:
        """캐릭터가 전투 불능 상태인지 확인"""
        if hasattr(character, "is_alive"):
            return not character.is_alive()
        if hasattr(character, "current_hp"):
            return character.current_hp <= 0
        return False

    def _end_combat(self, state: CombatState) -> None:
        """
        전투 종료

        Args:
            state: 종료 상태
        """
        self.state = state

        self.logger.info(f"전투 종료: {state.value}")

        # 이벤트 발행
        event_bus.publish(Events.COMBAT_END, {
            "state": state.value,
            "turn_count": self.turn_count
        })

        # 콜백 호출
        if self.on_combat_end:
            self.on_combat_end(state)

        # 시스템 정리
        self.atb.clear()

    def get_action_order(self) -> List[Any]:
        """
        현재 행동 순서 가져오기

        Returns:
            행동 가능한 전투원 리스트
        """
        return self.atb.get_action_order()

    def is_player_turn(self, character: Any) -> bool:
        """플레이어 턴 여부"""
        return character in self.allies

    def get_valid_targets(self, actor: Any, action_type: ActionType) -> List[Any]:
        """
        유효한 대상 리스트

        Args:
            actor: 행동자
            action_type: 행동 타입

        Returns:
            대상 리스트
        """
        if action_type in [ActionType.BRV_ATTACK, ActionType.HP_ATTACK, ActionType.BRV_HP_ATTACK]:
            # 공격: 상대편 대상
            if actor in self.allies:
                return [e for e in self.enemies if not self._is_defeated(e)]
            else:
                return [a for a in self.allies if not self._is_defeated(a)]
        else:
            # 아이템, 스킬 등: 아군 대상
            if actor in self.allies:
                return self.allies
            else:
                return self.enemies


# 전역 인스턴스
_combat_manager: Optional[CombatManager] = None


def get_combat_manager() -> CombatManager:
    """전역 전투 관리자 인스턴스"""
    global _combat_manager
    if _combat_manager is None:
        _combat_manager = CombatManager()
    return _combat_manager
