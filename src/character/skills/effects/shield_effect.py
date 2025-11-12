"""Shield Effect - 보호막 효과"""
from src.character.skills.effects.base import SkillEffect, EffectResult, EffectType

class ShieldEffect(SkillEffect):
    """보호막 효과"""
    def __init__(self, base_amount=0, hp_consumed_multiplier=0.0):
        super().__init__(EffectType.GIMMICK)
        self.base_amount = base_amount
        self.hp_consumed_multiplier = hp_consumed_multiplier
    
    def execute(self, user, target, context):
        """보호막 생성"""
        amount = self.base_amount
        
        # HP 소비 기반 보호막
        if self.hp_consumed_multiplier > 0 and 'hp_consumed' in context:
            hp_consumed = context['hp_consumed']
            amount += int(hp_consumed * self.hp_consumed_multiplier)
        
        # 보호막 추가
        if not hasattr(target, 'shield_amount'):
            target.shield_amount = 0
        
        old_shield = target.shield_amount
        target.shield_amount += amount
        
        return EffectResult(
            effect_type=EffectType.GIMMICK,
            success=True,
            gimmick_changes={'shield_amount': amount},
            message=f"보호막 +{amount} (총 {target.shield_amount})"
        )
