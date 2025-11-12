"""Warlock Skills - 흑마법사 스킬 (부패/저주 시스템)"""
from src.character.skills.skill import Skill
from src.character.skills.effects.damage_effect import DamageEffect, DamageType
from src.character.skills.effects.gimmick_effect import GimmickEffect, GimmickOperation
from src.character.skills.effects.heal_effect import HealEffect, HealType
from src.character.skills.effects.buff_effect import BuffEffect, BuffType
from src.character.skills.costs.mp_cost import MPCost
from src.character.skills.costs.stack_cost import StackCost

def create_warlock_skills():
    """흑마법사 9개 스킬 생성"""
    
    # 1. 기본 BRV: 암흑 화살
    shadow_bolt = Skill("warlock_shadow_bolt", "암흑 화살", "어둠의 마법, 부패 축적")
    shadow_bolt.effects = [
        DamageEffect(DamageType.BRV, 1.6),
        GimmickEffect(GimmickOperation.ADD, "corruption_stacks", 1, max_value=10)
    ]
    shadow_bolt.costs = [MPCost(15)]
    
    # 2. 기본 HP: 영혼 흡수
    drain_soul = Skill("warlock_drain_soul", "영혼 흡수", "부패 소비, 영혼 흡수")
    drain_soul.effects = [
        DamageEffect(DamageType.HP, 1.0, gimmick_bonus={"field": "corruption_stacks", "multiplier": 0.2}),
        HealEffect(HealType.HP, percentage=0.15),
        GimmickEffect(GimmickOperation.CONSUME, "corruption_stacks", 1)
    ]
    drain_soul.costs = [MPCost(20), StackCost("corruption_stacks", 1)]
    
    # 3. 고통의 저주
    curse_of_agony = Skill("warlock_curse", "고통의 저주", "지속 피해 저주")
    curse_of_agony.effects = [
        DamageEffect(DamageType.BRV, 1.0),
        DamageEffect(DamageType.BRV, 1.0),
        DamageEffect(DamageType.BRV, 1.0),
        GimmickEffect(GimmickOperation.ADD, "corruption_stacks", 2, max_value=10)
    ]
    curse_of_agony.costs = [MPCost(30)]
    curse_of_agony.cooldown = 3
    
    # 4. 부패
    corruption = Skill("warlock_corruption", "부패", "부패 확산")
    corruption.effects = [
        DamageEffect(DamageType.BRV, 1.3, gimmick_bonus={"field": "corruption_stacks", "multiplier": 0.15}),
        GimmickEffect(GimmickOperation.ADD, "corruption_stacks", 2, max_value=10)
    ]
    corruption.costs = [MPCost(25)]
    corruption.cooldown = 2
    
    # 5. 생명 전환
    life_tap = Skill("warlock_life_tap", "생명 전환", "HP → MP + 부패")
    life_tap.effects = [
        HealEffect(HealType.MP, base_amount=50),
        GimmickEffect(GimmickOperation.ADD, "corruption_stacks", 1, max_value=10)
    ]
    life_tap.costs = [MPCost(0)]
    life_tap.target_type = "self"
    life_tap.cooldown = 3
    
    # 6. 악마 소환
    summon_demon = Skill("warlock_summon_demon", "악마 소환", "부패 5 소비, 악마 소환")
    summon_demon.effects = [
        GimmickEffect(GimmickOperation.SET, "demon_summoned", 1),
        BuffEffect(BuffType.MAGIC_UP, 0.3, duration=5),
        BuffEffect(BuffType.ATTACK_UP, 0.2, duration=5),
        GimmickEffect(GimmickOperation.CONSUME, "corruption_stacks", 5)
    ]
    summon_demon.costs = [MPCost(40), StackCost("corruption_stacks", 5)]
    summon_demon.target_type = "self"
    summon_demon.cooldown = 5
    
    # 7. 어둠의 계약
    dark_pact = Skill("warlock_dark_pact", "어둠의 계약", "부패로 힘 강화")
    dark_pact.effects = [
        BuffEffect(BuffType.MAGIC_UP, 0.4, duration=4),
        BuffEffect(BuffType.CRITICAL_UP, 0.25, duration=4),
        GimmickEffect(GimmickOperation.CONSUME, "corruption_stacks", 3)
    ]
    dark_pact.costs = [MPCost(35), StackCost("corruption_stacks", 3)]
    dark_pact.target_type = "self"
    dark_pact.cooldown = 4
    
    # 8. 지옥불
    fel_flame = Skill("warlock_fel_flame", "지옥불", "부패 폭발")
    fel_flame.effects = [
        DamageEffect(DamageType.BRV_HP, 2.0, gimmick_bonus={"field": "corruption_stacks", "multiplier": 0.35}),
        GimmickEffect(GimmickOperation.CONSUME, "corruption_stacks", 2)
    ]
    fel_flame.costs = [MPCost(45), StackCost("corruption_stacks", 2)]
    fel_flame.cooldown = 4
    
    # 9. 궁극기: 카오스 볼트
    ultimate = Skill("warlock_ultimate", "카오스 볼트", "혼돈의 마법 극의")
    ultimate.effects = [
        DamageEffect(DamageType.BRV, 2.5, gimmick_bonus={"field": "corruption_stacks", "multiplier": 0.5}),
        DamageEffect(DamageType.BRV, 2.0, gimmick_bonus={"field": "demon_summoned", "multiplier": 1.0}),
        DamageEffect(DamageType.HP, 3.5),
        BuffEffect(BuffType.MAGIC_UP, 0.5, duration=5),
        GimmickEffect(GimmickOperation.SET, "corruption_stacks", 0)
    ]
    ultimate.costs = [MPCost(100)]
    ultimate.is_ultimate = True
    ultimate.cooldown = 10
    
    return [shadow_bolt, drain_soul, curse_of_agony, corruption, life_tap,
            summon_demon, dark_pact, fel_flame, ultimate]

def register_warlock_skills(skill_manager):
    """흑마법사 스킬 등록"""
    skills = create_warlock_skills()
    for skill in skills:
        skill_manager.register_skill(skill)
    return [s.skill_id for s in skills]
