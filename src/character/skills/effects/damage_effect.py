"""Damage Effect"""
from enum import Enum
from src.character.skills.effects.base import SkillEffect, EffectResult, EffectType
from src.combat.brave_system import get_brave_system
from src.combat.damage_calculator import get_damage_calculator

class DamageType(Enum):
    BRV = "brv"
    HP = "hp"
    BRV_HP = "brv_hp"

class DamageEffect(SkillEffect):
    """데미지 효과"""
    def __init__(self, damage_type=DamageType.BRV, multiplier=1.0, gimmick_bonus=None):
        super().__init__(EffectType.DAMAGE)
        self.damage_type = damage_type
        self.multiplier = multiplier
        self.gimmick_bonus = gimmick_bonus or {}
        self.brave_system = get_brave_system()
        self.damage_calculator = get_damage_calculator()
    
    def can_execute(self, user, target, context) -> bool:
        if self.damage_type == DamageType.HP:
            return user.current_brv > 0
        return True
    
    def execute(self, user, target, context) -> EffectResult:
        result = EffectResult(effect_type=EffectType.DAMAGE, success=True)
        
        # 최종 배율 계산 (기믹 보너스)
        final_mult = self.multiplier
        if self.gimmick_bonus:
            field = self.gimmick_bonus.get('field')
            bonus_mult = self.gimmick_bonus.get('multiplier', 0)
            if field and hasattr(user, field):
                stacks = getattr(user, field, 0)
                final_mult += stacks * bonus_mult
        
        if self.damage_type == DamageType.BRV:
            dmg_result = self.damage_calculator.calculate_brv_damage(user, target, final_mult)
            brv_result = self.brave_system.brv_attack(user, target, dmg_result.final_damage)
            result.brv_damage = brv_result['brv_stolen']
            result.brv_gained = brv_result['actual_gain']
            result.brv_broken = brv_result['is_break']
            result.critical = dmg_result.is_critical
            result.message = f"BRV 공격! {result.brv_damage}"
        
        elif self.damage_type == DamageType.HP:
            hp_result = self.brave_system.hp_attack(user, target, final_mult)
            result.hp_damage = hp_result['hp_damage']
            result.damage_dealt = hp_result['hp_damage']
            result.message = f"HP 공격! {result.hp_damage}"
        
        elif self.damage_type == DamageType.BRV_HP:
            # BRV 먼저
            dmg_result = self.damage_calculator.calculate_brv_damage(user, target, final_mult)
            brv_result = self.brave_system.brv_attack(user, target, dmg_result.final_damage)
            result.brv_damage = brv_result['brv_stolen']
            result.brv_gained = brv_result['actual_gain']
            result.brv_broken = brv_result['is_break']
            # HP 이어서
            hp_result = self.brave_system.hp_attack(user, target, 1.0)
            result.hp_damage = hp_result['hp_damage']
            result.damage_dealt = hp_result['hp_damage']
            result.message = f"BRV+HP 공격! BRV:{result.brv_damage} HP:{result.hp_damage}"
        
        return result
