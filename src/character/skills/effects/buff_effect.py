"""Buff Effect - 버프 효과"""
from src.character.skills.effects.base import SkillEffect, EffectResult, EffectType

class BuffType:
    """버프 타입"""
    ATTACK_UP = "attack_up"
    DEFENSE_UP = "defense_up"
    MAGIC_UP = "magic_up"
    SPIRIT_UP = "spirit_up"
    SPEED_UP = "speed_up"
    CRITICAL_UP = "critical_up"
    ACCURACY_UP = "accuracy_up"
    EVASION_UP = "evasion_up"

class BuffEffect(SkillEffect):
    """버프 효과"""
    def __init__(self, buff_type: str, value: float, duration: int = 3, is_party_wide: bool = False):
        super().__init__(EffectType.BUFF)
        self.buff_type = buff_type
        self.value = value
        self.duration = duration
        self.is_party_wide = is_party_wide

    def can_execute(self, user, target, context):
        return True, ""

    def execute(self, user, target, context):
        """버프 적용"""
        # 파티 전체 버프
        if self.is_party_wide:
            targets = context.get('party_members', [target]) if context else [target]
        else:
            targets = target if isinstance(target, list) else [target]

        buffed_count = 0
        for t in targets:
            if self._apply_buff(t):
                buffed_count += 1

        buff_name = self.buff_type.replace('_', ' ').title()
        if self.is_party_wide:
            message = f"파티 전체에 {buff_name} 적용! (+{int(self.value*100)}%)"
        else:
            message = f"{buff_name} 적용! (+{int(self.value*100)}%)"

        return EffectResult(
            effect_type=EffectType.BUFF,
            success=buffed_count > 0,
            message=message
        )
    
    def _apply_buff(self, target):
        """개별 버프 적용"""
        if not hasattr(target, 'active_buffs'):
            target.active_buffs = {}
        
        target.active_buffs[self.buff_type] = {
            'value': self.value,
            'duration': self.duration
        }
        return True
