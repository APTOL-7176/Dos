"""Mage Skills - 마법사 스킬 (원소 조합 시스템 - 기초)"""
from src.character.skills.skill import Skill
from src.character.skills.effects.damage_effect import DamageEffect, DamageType
from src.character.skills.effects.gimmick_effect import GimmickEffect, GimmickOperation
from src.character.skills.effects.buff_effect import BuffEffect, BuffType
from src.character.skills.costs.mp_cost import MPCost
from src.character.skills.costs.stack_cost import StackCost

def create_mage_skills():
    """마법사 9개 스킬 생성 (Archmage의 기초 버전)"""

    # 1. 기본 BRV: 불꽃 폭발
    fire_blast = Skill("mage_fire_blast", "불꽃 폭발", "화염 원소 획득")
    fire_blast.effects = [
        DamageEffect(DamageType.BRV, 1.5, stat_type="magical"),
        GimmickEffect(GimmickOperation.ADD, "fire_element", 1, max_value=5)
    ]
    fire_blast.costs = []  # 기본 공격은 MP 소모 없음

    # 2. 기본 HP: 얼음 파편
    ice_shard = Skill("mage_ice_shard", "얼음 파편", "빙결 원소 획득")
    ice_shard.effects = [
        DamageEffect(DamageType.HP, 0.9, stat_type="magical"),
        GimmickEffect(GimmickOperation.ADD, "ice_element", 1, max_value=5)
    ]
    ice_shard.costs = []  # 기본 공격은 MP 소모 없음

    # 3. 천둥 화살
    thunder_bolt = Skill("mage_thunder_bolt", "천둥 화살", "번개 원소 획득")
    thunder_bolt.effects = [
        DamageEffect(DamageType.BRV, 1.7, stat_type="magical"),
        GimmickEffect(GimmickOperation.ADD, "lightning_element", 1, max_value=5)
    ]
    thunder_bolt.costs = [MPCost(6)]
    thunder_bolt.cooldown = 1

    # 4. 마법 미사일
    magic_missile = Skill("mage_magic_missile", "마법 미사일", "기본 마법 공격")
    magic_missile.effects = [
        DamageEffect(DamageType.BRV_HP, 1.3,
                    gimmick_bonus={"field": "fire_element", "multiplier": 0.15}, stat_type="magical")
    ]
    magic_missile.costs = [MPCost(6), StackCost("fire_element", 1)]
    magic_missile.cooldown = 2

    # 5. 마나 보호막
    mana_shield = Skill("mage_mana_shield", "마나 보호막", "방어 마법")
    mana_shield.effects = [
        BuffEffect(BuffType.DEFENSE_UP, 0.4, duration=3),
        GimmickEffect(GimmickOperation.ADD, "ice_element", 1, max_value=5)
    ]
    mana_shield.costs = [MPCost(7)]
    mana_shield.target_type = "self"
    mana_shield.cooldown = 3

    # 6. 원소 융합
    elemental_fusion = Skill("mage_elemental_fusion", "원소 융합", "2원소 소비 융합 공격")
    elemental_fusion.effects = [
        DamageEffect(DamageType.BRV_HP, 1.6,
                    gimmick_bonus={"field": "fire_element", "multiplier": 0.2}, stat_type="magical"),
        DamageEffect(DamageType.BRV, 1.0,
                    gimmick_bonus={"field": "ice_element", "multiplier": 0.2}, stat_type="magical")
    ]
    elemental_fusion.costs = [MPCost(9), StackCost("fire_element", 1), StackCost("ice_element", 1)]
    elemental_fusion.cooldown = 3

    # 7. 비전 폭발
    arcane_explosion = Skill("mage_arcane_explosion", "비전 폭발", "광역 마법 공격")
    arcane_explosion.effects = [
        DamageEffect(DamageType.BRV, 1.8,
                    gimmick_bonus={"field": "lightning_element", "multiplier": 0.25}, stat_type="magical")
    ]
    arcane_explosion.costs = [MPCost(10), StackCost("lightning_element", 1)]
    arcane_explosion.cooldown = 4
    arcane_explosion.is_aoe = True

    # 8. 원소 폭풍
    elemental_storm = Skill("mage_elemental_storm", "원소 폭풍", "3원소 소비 대마법")
    elemental_storm.effects = [
        DamageEffect(DamageType.BRV, 2.0,
                    gimmick_bonus={"field": "fire_element", "multiplier": 0.2}, stat_type="magical"),
        DamageEffect(DamageType.BRV, 1.5,
                    gimmick_bonus={"field": "ice_element", "multiplier": 0.2}, stat_type="magical"),
        DamageEffect(DamageType.HP, 1.5,
                    gimmick_bonus={"field": "lightning_element", "multiplier": 0.25}, stat_type="magical")
    ]
    elemental_storm.costs = [MPCost(14), StackCost("fire_element", 1), StackCost("ice_element", 1), StackCost("lightning_element", 1)]
    elemental_storm.cooldown = 5
    elemental_storm.is_aoe = True

    # 9. 궁극기: 마법 마스터
    ultimate = Skill("mage_ultimate", "마법 마스터", "모든 원소를 결집하여 극한의 마법")
    ultimate.effects = [
        DamageEffect(DamageType.BRV, 2.2,
                    gimmick_bonus={"field": "fire_element", "multiplier": 0.3}, stat_type="magical"),
        DamageEffect(DamageType.BRV, 2.2,
                    gimmick_bonus={"field": "ice_element", "multiplier": 0.3}, stat_type="magical"),
        DamageEffect(DamageType.HP, 2.5,
                    gimmick_bonus={"field": "lightning_element", "multiplier": 0.35}, stat_type="magical"),
        BuffEffect(BuffType.MAGIC_UP, 0.5, duration=4),
        GimmickEffect(GimmickOperation.SET, "fire_element", 0),
        GimmickEffect(GimmickOperation.SET, "ice_element", 0),
        GimmickEffect(GimmickOperation.SET, "lightning_element", 0)
    ]
    ultimate.costs = [MPCost(22)]
    ultimate.is_ultimate = True
    ultimate.is_aoe = True
    ultimate.cooldown = 10

    return [fire_blast, ice_shard, thunder_bolt, magic_missile, mana_shield,
            elemental_fusion, arcane_explosion, elemental_storm, ultimate]

def register_mage_skills(skill_manager):
    """마법사 스킬 등록"""
    skills = create_mage_skills()
    for skill in skills:
        skill_manager.register_skill(skill)
    return [s.skill_id for s in skills]
