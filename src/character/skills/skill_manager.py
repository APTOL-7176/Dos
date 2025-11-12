"""Skill Manager - 스킬 관리자"""
from typing import Any, Dict, List, Optional
from src.character.skills.skill import Skill, SkillResult
from src.core.event_bus import event_bus, Events
from src.core.logger import get_logger

class SkillManager:
    """스킬 관리자"""
    def __init__(self):
        self.logger = get_logger("skill_manager")
        self._skills = {}
        self._cooldowns = {}

    def register_skill(self, skill: Skill):
        """스킬 등록"""
        self._skills[skill.skill_id] = skill
        self.logger.debug(f"스킬 등록: {skill.name}")

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """스킬 가져오기"""
        return self._skills.get(skill_id)

    def execute_skill(self, skill_id: str, user: Any, target: Any, context: Optional[Dict[str, Any]] = None) -> SkillResult:
        """스킬 실행"""
        skill = self.get_skill(skill_id)
        if not skill:
            return SkillResult(success=False, message=f"스킬 없음: {skill_id}")
        
        if self.is_on_cooldown(user, skill_id):
            return SkillResult(success=False, message="쿨다운 중")
        
        event_bus.publish(Events.SKILL_CAST_START, {"skill": skill, "user": user, "target": target})
        result = skill.execute(user, target, context)
        
        if result.success and skill.cooldown > 0:
            self.set_cooldown(user, skill_id, skill.cooldown)
        
        event_bus.publish(Events.SKILL_EXECUTE, {"skill": skill, "user": user, "target": target, "result": result})
        return result

    def is_on_cooldown(self, character: Any, skill_id: str) -> bool:
        """쿨다운 확인"""
        char_id = id(character)
        return char_id in self._cooldowns and self._cooldowns[char_id].get(skill_id, 0) > 0

    def get_cooldown(self, character: Any, skill_id: str) -> int:
        """남은 쿨다운"""
        char_id = id(character)
        return self._cooldowns.get(char_id, {}).get(skill_id, 0)

    def set_cooldown(self, character: Any, skill_id: str, turns: int):
        """쿨다운 설정"""
        char_id = id(character)
        if char_id not in self._cooldowns:
            self._cooldowns[char_id] = {}
        self._cooldowns[char_id][skill_id] = turns

    def reduce_cooldowns(self, character: Any, amount: int = 1):
        """쿨다운 감소"""
        char_id = id(character)
        if char_id not in self._cooldowns:
            return
        for skill_id in list(self._cooldowns[char_id].keys()):
            self._cooldowns[char_id][skill_id] -= amount
            if self._cooldowns[char_id][skill_id] <= 0:
                del self._cooldowns[char_id][skill_id]

_skill_manager = None

def get_skill_manager() -> SkillManager:
    """전역 스킬 관리자"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager
