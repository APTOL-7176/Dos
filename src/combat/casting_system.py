"""
캐스팅 시스템

일부 강력한 스킬은 캐스팅 시간이 필요
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

from src.core.logger import get_logger, Loggers


logger = get_logger(Loggers.COMBAT)


class CastingState(Enum):
    """캐스팅 상태"""
    NOT_CASTING = "not_casting"
    CASTING = "casting"
    CAST_COMPLETE = "cast_complete"
    INTERRUPTED = "interrupted"


@dataclass
class CastingInfo:
    """캐스팅 정보"""
    caster: Any  # 시전자
    skill: Any  # 스킬
    target: Optional[Any]  # 대상
    cast_time: float  # 총 시전 시간
    elapsed_time: float = 0.0  # 경과 시간
    state: CastingState = CastingState.CASTING
    interruptible: bool = True  # 중단 가능 여부

    @property
    def progress(self) -> float:
        """진행도 (0.0 ~ 1.0)"""
        if self.cast_time <= 0:
            return 1.0
        return min(1.0, self.elapsed_time / self.cast_time)

    @property
    def is_complete(self) -> bool:
        """완료 여부"""
        return self.elapsed_time >= self.cast_time


class CastingSystem:
    """캐스팅 시스템"""

    def __init__(self):
        self.active_casts: Dict[Any, CastingInfo] = {}  # caster -> CastingInfo
        self.cast_queue: list = []  # 완료 대기 큐

    def start_cast(
        self,
        caster: Any,
        skill: Any,
        target: Optional[Any],
        cast_time: float,
        interruptible: bool = True
    ) -> CastingInfo:
        """
        캐스팅 시작

        Args:
            caster: 시전자
            skill: 스킬
            target: 대상
            cast_time: 시전 시간
            interruptible: 중단 가능 여부

        Returns:
            CastingInfo
        """
        # 이미 캐스팅 중이면 취소
        if caster in self.active_casts:
            self.cancel_cast(caster, "새로운 시전 시작")

        cast_info = CastingInfo(
            caster=caster,
            skill=skill,
            target=target,
            cast_time=cast_time,
            interruptible=interruptible
        )

        self.active_casts[caster] = cast_info

        skill_name = getattr(skill, 'name', str(skill))
        logger.info(f"{caster.name}가 {skill_name} 시전 시작 (시간: {cast_time:.1f}초)")

        return cast_info

    def update(self, delta_time: float):
        """
        캐스팅 업데이트

        Args:
            delta_time: 경과 시간 (초)
        """
        completed_casters = []

        for caster, cast_info in self.active_casts.items():
            if cast_info.state != CastingState.CASTING:
                continue

            # 경과 시간 증가
            cast_info.elapsed_time += delta_time

            # 완료 체크
            if cast_info.is_complete:
                cast_info.state = CastingState.CAST_COMPLETE
                completed_casters.append(caster)
                self.cast_queue.append(cast_info)

                skill_name = getattr(cast_info.skill, 'name', str(cast_info.skill))
                logger.info(f"{caster.name}의 {skill_name} 시전 완료!")

        # 완료된 캐스팅 제거
        for caster in completed_casters:
            del self.active_casts[caster]

    def cancel_cast(self, caster: Any, reason: str = "중단됨"):
        """
        캐스팅 중단

        Args:
            caster: 시전자
            reason: 중단 이유
        """
        if caster not in self.active_casts:
            return

        cast_info = self.active_casts[caster]

        if not cast_info.interruptible:
            logger.debug(f"{caster.name}의 시전은 중단 불가")
            return

        skill_name = getattr(cast_info.skill, 'name', str(cast_info.skill))
        logger.info(f"{caster.name}의 {skill_name} 시전 중단: {reason}")

        cast_info.state = CastingState.INTERRUPTED
        del self.active_casts[caster]

    def interrupt_on_damage(self, caster: Any, damage: int):
        """
        데미지로 인한 중단

        Args:
            caster: 시전자
            damage: 받은 데미지
        """
        if caster not in self.active_casts:
            return

        cast_info = self.active_casts[caster]

        # 중단 확률 (데미지가 클수록 높음)
        interrupt_chance = min(0.9, damage / 100.0)

        import random
        if random.random() < interrupt_chance:
            self.cancel_cast(caster, f"데미지 {damage}로 인한 중단")

    def is_casting(self, caster: Any) -> bool:
        """시전 중인지 확인"""
        return caster in self.active_casts

    def get_cast_info(self, caster: Any) -> Optional[CastingInfo]:
        """캐스팅 정보 가져오기"""
        return self.active_casts.get(caster)

    def get_completed_casts(self) -> list:
        """완료된 캐스팅 가져오기 (큐에서 제거)"""
        completed = self.cast_queue.copy()
        self.cast_queue.clear()
        return completed

    def clear(self):
        """모든 캐스팅 초기화"""
        self.active_casts.clear()
        self.cast_queue.clear()


# 전역 인스턴스
_casting_system: Optional[CastingSystem] = None


def get_casting_system() -> CastingSystem:
    """전역 캐스팅 시스템 인스턴스"""
    global _casting_system
    if _casting_system is None:
        _casting_system = CastingSystem()
    return _casting_system
