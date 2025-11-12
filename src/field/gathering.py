"""
Gathering System - 채집 시스템

필드에서 자원을 채집하는 시스템
"""

import random
from typing import Dict, Any, Optional, List
from src.core.event_bus import event_bus
from src.core.config import get_config
from src.core.logger import get_logger
from src.character.stats import Stats


class Resource:
    """채집 가능한 자원"""

    def __init__(
        self,
        resource_id: str,
        name: str,
        rarity: float = 1.0,
        required_skill_level: int = 1
    ) -> None:
        self.resource_id = resource_id
        self.name = name
        self.rarity = rarity  # 0.0 ~ 1.0 (낮을수록 희귀)
        self.required_skill_level = required_skill_level


class GatheringSystem:
    """채집 시스템"""

    def __init__(self) -> None:
        self.logger = get_logger("gathering")
        self.config = get_config()

        # 설정 로드
        self.enabled = self.config.get("field_systems.gathering.enabled", True)
        self.stamina_cost = self.config.get("field_systems.gathering.stamina_cost", 10)
        self.base_success_chance = self.config.get("field_systems.gathering.success_base_chance", 0.7)
        self.stat_bonus = self.config.get("field_systems.gathering.stat_bonus", "dexterity")
        self.yield_range = self.config.get("field_systems.gathering.yield_multiplier_range", [1, 3])

        # 자원 데이터베이스
        self.resources: Dict[str, Resource] = {}
        self._load_resources()

    def _load_resources(self) -> None:
        """자원 데이터 로드"""
        # TODO: YAML에서 로드
        default_resources = [
            Resource("herb", "약초", 0.8, 1),
            Resource("mushroom", "버섯", 0.7, 1),
            Resource("flower", "꽃", 0.6, 2),
            Resource("rare_herb", "희귀 약초", 0.3, 3),
            Resource("crystal", "크리스탈", 0.2, 4),
        ]

        for resource in default_resources:
            self.resources[resource.resource_id] = resource

    def can_gather(self, character: Any, resource_id: str) -> bool:
        """
        채집 가능 여부

        Args:
            character: 캐릭터
            resource_id: 자원 ID

        Returns:
            채집 가능 여부
        """
        if not self.enabled:
            return False

        # 스태미나 확인
        stamina = getattr(character, Stats.STAMINA, 0)
        if stamina < self.stamina_cost:
            return False

        # 자원 존재 확인
        resource = self.resources.get(resource_id)
        if not resource:
            return False

        # 스킬 레벨 확인 (임시로 dexterity 사용)
        skill_level = getattr(character, self.stat_bonus, 0)
        if skill_level < resource.required_skill_level:
            return False

        return True

    def gather(self, character: Any, resource_id: str) -> Dict[str, Any]:
        """
        채집 실행

        Args:
            character: 캐릭터
            resource_id: 자원 ID

        Returns:
            채집 결과 {"success": bool, "yield": int, "resource": Resource}
        """
        if not self.can_gather(character, resource_id):
            return {"success": False, "yield": 0, "resource": None}

        resource = self.resources[resource_id]

        # 스태미나 소비
        character.stamina -= self.stamina_cost

        # 성공률 계산
        stat_value = getattr(character, self.stat_bonus, 0)
        success_chance = self.base_success_chance + (stat_value * 0.02)
        success_chance *= resource.rarity  # 희귀도에 따라 감소

        # 채집 시도
        success = random.random() < success_chance

        if success:
            # 획득량 계산
            yield_amount = random.randint(
                self.yield_range[0],
                self.yield_range[0] + stat_value // 5
            )
            yield_amount = min(yield_amount, self.yield_range[1])
        else:
            yield_amount = 0

        result = {
            "success": success,
            "yield": yield_amount,
            "resource": resource
        }

        self.logger.info(
            f"채집: {character.name}",
            {
                "resource": resource.name,
                "success": success,
                "yield": yield_amount
            }
        )

        event_bus.publish("gathering.completed", {
            "character": character,
            "result": result
        })

        return result

    def add_resource(self, resource: Resource) -> None:
        """자원 추가 (동적 확장)"""
        self.resources[resource.resource_id] = resource

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """자원 조회"""
        return self.resources.get(resource_id)


# 전역 인스턴스
gathering_system = GatheringSystem()
