"""Dark Knight Skills - 암흑기사 (어둠 흡수)"""
from src.character.skills.skill import Skill
from src.character.skills.effects.damage_effect import DamageEffect, DamageType
from src.character.skills.effects.gimmick_effect import GimmickEffect, GimmickOperation
from src.character.skills.effects.lifesteal_effect import LifestealEffect
from src.character.skills.effects.buff_effect import BuffEffect, BuffType
from src.character.skills.costs.mp_cost import MPCost
from src.character.skills.costs.stack_cost import StackCost

def create_dark_knight_skills():
    skills = []
    skills.append(Skill("dk_dark_slash", "어둠 베기", "어둠 스택 획득"))
    skills[-1].effects = [DamageEffect(DamageType.BRV, 1.6), GimmickEffect(GimmickOperation.ADD, "darkness", 1, max_value=10)]
    skills[-1].costs = []  # 기본 공격은 MP 소모 없음

    skills.append(Skill("dk_drain", "흡혈 강타", "어둠 소비 HP공격"))
    skills[-1].effects = [DamageEffect(DamageType.HP, 1.0, gimmick_bonus={"field": "darkness", "multiplier": 0.25}), LifestealEffect(0.5), GimmickEffect(GimmickOperation.CONSUME, "darkness", 1)]
    skills[-1].costs = []  # 기본 공격은 MP 소모 없음
    
    skills.append(Skill("dk_dark_aura", "어둠의 오라", "지속 피해"))
    skills[-1].effects = [DamageEffect(DamageType.BRV, 1.0), DamageEffect(DamageType.BRV, 1.0), DamageEffect(DamageType.BRV, 1.0), GimmickEffect(GimmickOperation.ADD, "darkness", 2, max_value=10)]
    skills[-1].costs = [MPCost(30)]
    skills[-1].cooldown = 3
    
    skills.append(Skill("dk_dark_shield", "어둠의 보호막", "어둠으로 보호"))
    skills[-1].effects = [BuffEffect(BuffType.DEFENSE_UP, 0.4, duration=4), GimmickEffect(GimmickOperation.CONSUME, "darkness", 2)]
    skills[-1].costs = [MPCost(28), StackCost("darkness", 2)]
    skills[-1].target_type = "self"
    skills[-1].cooldown = 4
    
    skills.append(Skill("dk_dark_wave", "어둠의 파동", "광역 공격"))
    skills[-1].effects = [DamageEffect(DamageType.BRV_HP, 1.8, gimmick_bonus={"field": "darkness", "multiplier": 0.3}), LifestealEffect(0.4), GimmickEffect(GimmickOperation.CONSUME, "darkness", 3)]
    skills[-1].costs = [MPCost(40), StackCost("darkness", 3)]
    skills[-1].cooldown = 4
    
    for i in range(4):  # 나머지 스킬
        skill = Skill(f"dk_skill_{i+6}", f"암흑 스킬 {i+6}", "")
        skill.effects = [DamageEffect(DamageType.BRV, 1.5 + i*0.3)]
        skill.costs = [MPCost(30 + i*10)]
        skills.append(skill)
    
    ultimate = Skill("dk_ultimate", "어둠의 지배자", "궁극 어둠")
    ultimate.effects = [DamageEffect(DamageType.BRV, 2.5, gimmick_bonus={"field": "darkness", "multiplier": 0.5}), DamageEffect(DamageType.HP, 3.5), LifestealEffect(1.0), GimmickEffect(GimmickOperation.SET, "darkness", 0)]
    ultimate.costs = [MPCost(100)]
    ultimate.is_ultimate = True
    ultimate.cooldown = 10
    skills.append(ultimate)
    
    return skills

def register_dark_knight_skills(sm):
    for s in create_dark_knight_skills():
        sm.register_skill(s)
    return [s.skill_id for s in create_dark_knight_skills()]
