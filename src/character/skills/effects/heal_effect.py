"""Heal Effect - 회복 효과"""
from enum import Enum
from src.character.skills.effects.base import SkillEffect, EffectResult, EffectType

class HealType(Enum):
    HP = "hp"
    MP = "mp"

class HealEffect(SkillEffect):
    """회복 효과"""
    def __init__(self, heal_type=HealType.HP, base_amount=0, percentage=0.0, stat_scaling=None, multiplier=1.0):
        super().__init__(EffectType.HEAL)
        self.heal_type = heal_type
        self.base_amount = base_amount
        self.percentage = percentage
        self.stat_scaling = stat_scaling
        self.multiplier = multiplier
    
    def execute(self, user, target, context):
        """회복 실행"""
        amount = self.base_amount
        
        # 스탯 스케일링
        if self.stat_scaling and hasattr(user, self.stat_scaling):
            stat_value = getattr(user, self.stat_scaling, 0)
            amount += int(stat_value * self.multiplier)
        
        # 비율 회복
        if self.percentage > 0:
            if self.heal_type == HealType.HP:
                amount += int(target.max_hp * self.percentage)
            elif self.heal_type == HealType.MP:
                amount += int(target.max_mp * self.percentage)
        
        # 회복 적용
        if self.heal_type == HealType.HP:
            actual_heal = target.heal(amount)
        else:
            actual_heal = target.restore_mp(amount)
        
        return EffectResult(
            effect_type=EffectType.HEAL,
            success=True,
            heal_amount=actual_heal,
            message=f"{self.heal_type.value.upper()} 회복 {actual_heal}"
        )
