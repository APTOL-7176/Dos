"""
아이템 시스템

등급, 레벨 제한, 랜덤 부가 능력치
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random


class ItemRarity(Enum):
    """아이템 등급"""
    COMMON = ("common", "일반", (180, 180, 180))
    UNCOMMON = ("uncommon", "고급", (100, 255, 100))
    RARE = ("rare", "희귀", (100, 150, 255))
    EPIC = ("epic", "영웅", (200, 100, 255))
    LEGENDARY = ("legendary", "전설", (255, 165, 0))
    UNIQUE = ("unique", "유니크", (255, 50, 150))

    def __init__(self, id: str, name: str, color: tuple):
        self.id = id
        self.display_name = name
        self.color = color


class ItemType(Enum):
    """아이템 타입"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    KEY_ITEM = "key_item"


class EquipSlot(Enum):
    """장비 슬롯"""
    WEAPON = "weapon"
    HEAD = "head"
    BODY = "body"
    HANDS = "hands"
    FEET = "feet"
    ACCESSORY1 = "accessory1"
    ACCESSORY2 = "accessory2"


@dataclass
class ItemAffix:
    """아이템 접사 (부가 능력치)"""
    id: str
    name: str
    stat: str  # hp, strength, defense, etc.
    value: float  # 고정값 또는 퍼센트
    is_percentage: bool = False

    def get_description(self) -> str:
        """설명 텍스트"""
        if self.is_percentage:
            return f"{self.name}: {self.stat} +{int(self.value * 100)}%"
        else:
            return f"{self.name}: {self.stat} +{int(self.value)}"


@dataclass
class Item:
    """아이템 기본 클래스"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    level_requirement: int = 1
    base_stats: Dict[str, float] = field(default_factory=dict)
    affixes: List[ItemAffix] = field(default_factory=list)
    unique_effect: Optional[str] = None
    stack_size: int = 1
    sell_price: int = 0

    def get_total_stats(self) -> Dict[str, float]:
        """기본 스탯 + 접사 스탯 합계"""
        total = self.base_stats.copy()

        for affix in self.affixes:
            if affix.stat in total:
                if affix.is_percentage:
                    total[affix.stat] *= (1 + affix.value)
                else:
                    total[affix.stat] += affix.value
            else:
                total[affix.stat] = affix.value

        return total

    def get_full_description(self) -> List[str]:
        """전체 설명 (여러 줄)"""
        lines = []
        lines.append(f"[{self.rarity.display_name}] {self.name}")
        lines.append(self.description)
        lines.append(f"레벨 제한: {self.level_requirement}")

        # 기본 스탯
        if self.base_stats:
            lines.append("기본 능력:")
            for stat, value in self.base_stats.items():
                lines.append(f"  {stat}: +{int(value)}")

        # 접사
        if self.affixes:
            lines.append("추가 능력:")
            for affix in self.affixes:
                lines.append(f"  {affix.get_description()}")

        # 유니크 효과
        if self.unique_effect:
            lines.append(f"특수: {self.unique_effect}")

        lines.append(f"판매가: {self.sell_price} 골드")

        return lines


@dataclass
class Equipment(Item):
    """장비 아이템"""
    equip_slot: EquipSlot = EquipSlot.WEAPON

    def __post_init__(self):
        if self.item_type not in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
            self.item_type = ItemType.WEAPON


@dataclass
class Consumable(Item):
    """소비 아이템"""
    effect_type: str = "heal_hp"  # heal_hp, heal_mp, buff, etc.
    effect_value: float = 0

    def __post_init__(self):
        self.item_type = ItemType.CONSUMABLE


# ============= 아이템 생성 템플릿 =============

WEAPON_TEMPLATES = {
    # 검
    "iron_sword": {
        "name": "철검",
        "description": "기본적인 철제 검",
        "rarity": ItemRarity.COMMON,
        "level_requirement": 1,
        "base_stats": {"physical_attack": 15, "accuracy": 5},
        "sell_price": 50
    },
    "steel_sword": {
        "name": "강철검",
        "description": "단단한 강철로 만든 검",
        "rarity": ItemRarity.UNCOMMON,
        "level_requirement": 5,
        "base_stats": {"physical_attack": 30, "accuracy": 8},
        "sell_price": 150
    },
    "mithril_sword": {
        "name": "미스릴 검",
        "description": "가볍고 날카로운 미스릴 검",
        "rarity": ItemRarity.RARE,
        "level_requirement": 10,
        "base_stats": {"physical_attack": 50, "accuracy": 12, "speed": 3},
        "sell_price": 500
    },
    "dragon_slayer": {
        "name": "드래곤 슬레이어",
        "description": "용을 베기 위해 만들어진 거대한 검",
        "rarity": ItemRarity.EPIC,
        "level_requirement": 20,
        "base_stats": {"physical_attack": 85, "strength": 10},
        "sell_price": 2000
    },

    # 지팡이
    "wooden_staff": {
        "name": "나무 지팡이",
        "description": "초보 마법사용 지팡이",
        "rarity": ItemRarity.COMMON,
        "level_requirement": 1,
        "base_stats": {"magic_attack": 18, "mp": 10},
        "sell_price": 60
    },
    "crystal_staff": {
        "name": "수정 지팡이",
        "description": "마력이 깃든 수정 지팡이",
        "rarity": ItemRarity.RARE,
        "level_requirement": 10,
        "base_stats": {"magic_attack": 60, "mp": 30, "spirit": 5},
        "sell_price": 600
    },
    "archmagus_staff": {
        "name": "대마법사의 지팡이",
        "description": "전설적인 대마법사가 사용했던 지팡이",
        "rarity": ItemRarity.LEGENDARY,
        "level_requirement": 25,
        "base_stats": {"magic_attack": 120, "mp": 60, "spirit": 15},
        "sell_price": 5000
    },

    # 활
    "hunting_bow": {
        "name": "사냥용 활",
        "description": "기본적인 사냥용 활",
        "rarity": ItemRarity.COMMON,
        "level_requirement": 1,
        "base_stats": {"physical_attack": 12, "accuracy": 10},
        "sell_price": 45
    },
    "longbow": {
        "name": "장궁",
        "description": "사거리가 긴 장궁",
        "rarity": ItemRarity.UNCOMMON,
        "level_requirement": 7,
        "base_stats": {"physical_attack": 35, "accuracy": 15, "evasion": 3},
        "sell_price": 200
    },
}

ARMOR_TEMPLATES = {
    # 갑옷
    "leather_armor": {
        "name": "가죽 갑옷",
        "description": "기본적인 가죽 갑옷",
        "rarity": ItemRarity.COMMON,
        "level_requirement": 1,
        "base_stats": {"physical_defense": 10, "hp": 20},
        "sell_price": 40
    },
    "chainmail": {
        "name": "사슬 갑옷",
        "description": "사슬로 엮은 갑옷",
        "rarity": ItemRarity.UNCOMMON,
        "level_requirement": 5,
        "base_stats": {"physical_defense": 25, "hp": 40},
        "sell_price": 120
    },
    "plate_armor": {
        "name": "판금 갑옷",
        "description": "무거운 철판 갑옷",
        "rarity": ItemRarity.RARE,
        "level_requirement": 12,
        "base_stats": {"physical_defense": 50, "hp": 80, "physical_attack": -5},
        "sell_price": 600
    },
    "dragon_scale_armor": {
        "name": "용비늘 갑옷",
        "description": "드래곤의 비늘로 만든 갑옷",
        "rarity": ItemRarity.LEGENDARY,
        "level_requirement": 25,
        "base_stats": {"physical_defense": 90, "magic_defense": 70, "hp": 150},
        "sell_price": 8000
    },

    # 로브
    "cloth_robe": {
        "name": "천 로브",
        "description": "마법사용 천 로브",
        "rarity": ItemRarity.COMMON,
        "level_requirement": 1,
        "base_stats": {"magic_defense": 12, "mp": 15},
        "sell_price": 50
    },
    "mage_robe": {
        "name": "마법사 로브",
        "description": "마력이 깃든 로브",
        "rarity": ItemRarity.RARE,
        "level_requirement": 10,
        "base_stats": {"magic_defense": 40, "mp": 50, "magic_attack": 10},
        "sell_price": 500
    },
}

ACCESSORY_TEMPLATES = {
    "ring_of_strength": {
        "name": "힘의 반지",
        "description": "착용자의 힘을 증가시키는 반지",
        "rarity": ItemRarity.UNCOMMON,
        "level_requirement": 3,
        "base_stats": {"strength": 5},
        "sell_price": 100
    },
    "ring_of_wisdom": {
        "name": "지혜의 반지",
        "description": "착용자의 지혜를 증가시키는 반지",
        "rarity": ItemRarity.UNCOMMON,
        "level_requirement": 3,
        "base_stats": {"magic_attack": 8, "mp": 20},
        "sell_price": 100
    },
    "amulet_of_life": {
        "name": "생명의 부적",
        "description": "생명력을 대폭 증가시키는 부적",
        "rarity": ItemRarity.RARE,
        "level_requirement": 8,
        "base_stats": {"hp": 100},
        "sell_price": 400
    },
    "lucky_charm": {
        "name": "행운의 부적",
        "description": "행운을 가져다주는 신비한 부적",
        "rarity": ItemRarity.EPIC,
        "level_requirement": 15,
        "base_stats": {"luck": 10, "accuracy": 10, "evasion": 10},
        "sell_price": 1500
    },
}

# 유니크 아이템
UNIQUE_ITEMS = {
    "excalibur": {
        "name": "엑스칼리버",
        "description": "전설의 성검",
        "rarity": ItemRarity.UNIQUE,
        "level_requirement": 30,
        "base_stats": {"physical_attack": 150, "magic_attack": 50, "hp": 100, "mp": 50},
        "unique_effect": "HP 50% 이상 시 모든 공격력 +30%",
        "sell_price": 99999
    },
    "mjolnir": {
        "name": "묠니르",
        "description": "천둥의 망치",
        "rarity": ItemRarity.UNIQUE,
        "level_requirement": 28,
        "base_stats": {"physical_attack": 140, "strength": 20},
        "unique_effect": "공격 시 30% 확률로 번개 추가 데미지",
        "sell_price": 88888
    },
    "infinity_gauntlet": {
        "name": "무한의 건틀릿",
        "description": "모든 능력을 강화하는 전설의 장갑",
        "rarity": ItemRarity.UNIQUE,
        "level_requirement": 35,
        "base_stats": {
            "physical_attack": 50, "magic_attack": 50,
            "physical_defense": 30, "magic_defense": 30,
            "hp": 200, "mp": 100
        },
        "unique_effect": "모든 스탯 +10%",
        "sell_price": 150000
    },
    "phoenix_feather": {
        "name": "불사조의 깃털",
        "description": "부활의 힘을 가진 깃털",
        "rarity": ItemRarity.UNIQUE,
        "level_requirement": 20,
        "base_stats": {"hp": 150, "magic_defense": 40},
        "unique_effect": "전투 중 1회 사망 시 HP 100%로 부활",
        "sell_price": 50000
    },
}

# 소비 아이템
CONSUMABLE_TEMPLATES = {
    "health_potion": {
        "name": "체력 물약",
        "description": "HP 50 회복",
        "rarity": ItemRarity.COMMON,
        "effect_type": "heal_hp",
        "effect_value": 50,
        "sell_price": 20
    },
    "mega_health_potion": {
        "name": "대형 체력 물약",
        "description": "HP 200 회복",
        "rarity": ItemRarity.UNCOMMON,
        "effect_type": "heal_hp",
        "effect_value": 200,
        "sell_price": 80
    },
    "mana_potion": {
        "name": "마나 물약",
        "description": "MP 30 회복",
        "rarity": ItemRarity.COMMON,
        "effect_type": "heal_mp",
        "effect_value": 30,
        "sell_price": 25
    },
    "elixir": {
        "name": "엘릭서",
        "description": "HP와 MP를 완전히 회복",
        "rarity": ItemRarity.RARE,
        "effect_type": "full_restore",
        "effect_value": 0,
        "sell_price": 500
    },
}

# 접사 풀 (랜덤 생성용)
AFFIX_POOL = {
    # 물리 공격 관련
    "of_power": ItemAffix("of_power", "힘의", "physical_attack", 0.15, True),
    "of_might": ItemAffix("of_might", "완력의", "strength", 5, False),
    "sharp": ItemAffix("sharp", "날카로운", "physical_attack", 10, False),

    # 마법 관련
    "of_magic": ItemAffix("of_magic", "마력의", "magic_attack", 0.15, True),
    "of_wisdom": ItemAffix("of_wisdom", "지혜의", "mp", 20, False),
    "arcane": ItemAffix("arcane", "비전의", "magic_attack", 8, False),

    # 방어 관련
    "of_protection": ItemAffix("of_protection", "보호의", "physical_defense", 0.12, True),
    "sturdy": ItemAffix("sturdy", "견고한", "physical_defense", 8, False),
    "of_resistance": ItemAffix("of_resistance", "저항의", "magic_defense", 0.12, True),

    # 생명력
    "of_vitality": ItemAffix("of_vitality", "생명의", "hp", 0.20, True),
    "healthy": ItemAffix("healthy", "건강한", "hp", 30, False),

    # 속도/회피
    "of_speed": ItemAffix("of_speed", "신속의", "speed", 5, False),
    "of_evasion": ItemAffix("of_evasion", "회피의", "evasion", 8, False),

    # 명중/크리
    "of_accuracy": ItemAffix("of_accuracy", "정확의", "accuracy", 10, False),
    "of_luck": ItemAffix("of_luck", "행운의", "luck", 5, False),
}


class ItemGenerator:
    """아이템 생성기"""

    @staticmethod
    def generate_random_affixes(rarity: ItemRarity) -> List[ItemAffix]:
        """등급에 따라 랜덤 접사 생성"""
        num_affixes = {
            ItemRarity.COMMON: 0,
            ItemRarity.UNCOMMON: 1,
            ItemRarity.RARE: 2,
            ItemRarity.EPIC: 3,
            ItemRarity.LEGENDARY: 4,
            ItemRarity.UNIQUE: 0  # 유니크는 고정 능력
        }

        count = num_affixes.get(rarity, 0)
        if count == 0:
            return []

        # 랜덤 접사 선택
        available_affixes = list(AFFIX_POOL.values())
        selected = random.sample(available_affixes, min(count, len(available_affixes)))

        return selected

    @staticmethod
    def create_weapon(template_id: str, add_random_affixes: bool = True) -> Equipment:
        """무기 생성"""
        template = WEAPON_TEMPLATES.get(template_id)
        if not template:
            raise ValueError(f"Unknown weapon template: {template_id}")

        affixes = []
        if add_random_affixes:
            affixes = ItemGenerator.generate_random_affixes(template["rarity"])

        return Equipment(
            item_id=template_id,
            name=template["name"],
            description=template["description"],
            item_type=ItemType.WEAPON,
            rarity=template["rarity"],
            level_requirement=template["level_requirement"],
            base_stats=template["base_stats"].copy(),
            affixes=affixes,
            equip_slot=EquipSlot.WEAPON,
            sell_price=template["sell_price"]
        )

    @staticmethod
    def create_armor(template_id: str, add_random_affixes: bool = True) -> Equipment:
        """방어구 생성"""
        template = ARMOR_TEMPLATES.get(template_id)
        if not template:
            raise ValueError(f"Unknown armor template: {template_id}")

        affixes = []
        if add_random_affixes:
            affixes = ItemGenerator.generate_random_affixes(template["rarity"])

        return Equipment(
            item_id=template_id,
            name=template["name"],
            description=template["description"],
            item_type=ItemType.ARMOR,
            rarity=template["rarity"],
            level_requirement=template["level_requirement"],
            base_stats=template["base_stats"].copy(),
            affixes=affixes,
            equip_slot=EquipSlot.BODY,
            sell_price=template["sell_price"]
        )

    @staticmethod
    def create_accessory(template_id: str, add_random_affixes: bool = True) -> Equipment:
        """악세서리 생성"""
        template = ACCESSORY_TEMPLATES.get(template_id)
        if not template:
            raise ValueError(f"Unknown accessory template: {template_id}")

        affixes = []
        if add_random_affixes:
            affixes = ItemGenerator.generate_random_affixes(template["rarity"])

        return Equipment(
            item_id=template_id,
            name=template["name"],
            description=template["description"],
            item_type=ItemType.ACCESSORY,
            rarity=template["rarity"],
            level_requirement=template["level_requirement"],
            base_stats=template["base_stats"].copy(),
            affixes=affixes,
            equip_slot=EquipSlot.ACCESSORY1,
            sell_price=template["sell_price"]
        )

    @staticmethod
    def create_unique(template_id: str) -> Equipment:
        """유니크 아이템 생성 (고정 능력)"""
        template = UNIQUE_ITEMS.get(template_id)
        if not template:
            raise ValueError(f"Unknown unique template: {template_id}")

        return Equipment(
            item_id=template_id,
            name=template["name"],
            description=template["description"],
            item_type=ItemType.WEAPON,
            rarity=template["rarity"],
            level_requirement=template["level_requirement"],
            base_stats=template["base_stats"].copy(),
            affixes=[],
            unique_effect=template["unique_effect"],
            equip_slot=EquipSlot.WEAPON,
            sell_price=template["sell_price"]
        )

    @staticmethod
    def create_consumable(template_id: str) -> Consumable:
        """소비 아이템 생성"""
        template = CONSUMABLE_TEMPLATES.get(template_id)
        if not template:
            raise ValueError(f"Unknown consumable template: {template_id}")

        return Consumable(
            item_id=template_id,
            name=template["name"],
            description=template["description"],
            item_type=ItemType.CONSUMABLE,
            rarity=template["rarity"],
            effect_type=template["effect_type"],
            effect_value=template["effect_value"],
            sell_price=template["sell_price"]
        )

    @staticmethod
    def create_random_drop(level: int, boss_drop: bool = False) -> Item:
        """레벨에 맞는 랜덤 드롭 생성"""
        # 등급 확률
        if boss_drop:
            # 보스 드롭: 높은 등급 확률 증가
            rarity_chances = {
                ItemRarity.COMMON: 0.10,
                ItemRarity.UNCOMMON: 0.25,
                ItemRarity.RARE: 0.35,
                ItemRarity.EPIC: 0.20,
                ItemRarity.LEGENDARY: 0.10
            }
        else:
            # 일반 드롭
            rarity_chances = {
                ItemRarity.COMMON: 0.50,
                ItemRarity.UNCOMMON: 0.30,
                ItemRarity.RARE: 0.15,
                ItemRarity.EPIC: 0.04,
                ItemRarity.LEGENDARY: 0.01
            }

        # 등급 결정
        roll = random.random()
        cumulative = 0.0
        chosen_rarity = ItemRarity.COMMON

        for rarity, chance in rarity_chances.items():
            cumulative += chance
            if roll <= cumulative:
                chosen_rarity = rarity
                break

        # 레벨에 맞는 템플릿 선택
        all_templates = {**WEAPON_TEMPLATES, **ARMOR_TEMPLATES, **ACCESSORY_TEMPLATES}
        suitable_templates = [
            (tid, tpl) for tid, tpl in all_templates.items()
            if tpl["rarity"] == chosen_rarity and tpl["level_requirement"] <= level
        ]

        if not suitable_templates:
            # 적합한 템플릿 없으면 소비 아이템
            return ItemGenerator.create_consumable("health_potion")

        template_id, template = random.choice(suitable_templates)

        # 타입에 따라 생성
        if template_id in WEAPON_TEMPLATES:
            return ItemGenerator.create_weapon(template_id)
        elif template_id in ARMOR_TEMPLATES:
            return ItemGenerator.create_armor(template_id)
        else:
            return ItemGenerator.create_accessory(template_id)
