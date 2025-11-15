"""
재료 시스템

채집 가능한 재료 아이템
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from src.equipment.item_system import Item, ItemType, ItemRarity


class IngredientCategory(Enum):
    """재료 카테고리"""
    MEAT = "meat"           # 고기
    VEGETABLE = "vegetable" # 채소
    FRUIT = "fruit"         # 과일
    MUSHROOM = "mushroom"   # 버섯
    FISH = "fish"           # 생선
    EGG = "egg"             # 달걀
    DAIRY = "dairy"         # 유제품 (우유, 치즈 등)
    GRAIN = "grain"         # 곡물 (밀, 쌀 등)
    SPICE = "spice"         # 향신료
    SWEETENER = "sweetener" # 감미료 (꿀, 설탕 등)
    FILLER = "filler"       # 필러 (나뭇가지, 얼음 등)

    @property
    def display_name(self) -> str:
        """표시 이름"""
        names = {
            IngredientCategory.MEAT: "고기",
            IngredientCategory.VEGETABLE: "채소",
            IngredientCategory.FRUIT: "과일",
            IngredientCategory.MUSHROOM: "버섯",
            IngredientCategory.FISH: "생선",
            IngredientCategory.EGG: "달걀",
            IngredientCategory.DAIRY: "유제품",
            IngredientCategory.GRAIN: "곡물",
            IngredientCategory.SPICE: "향신료",
            IngredientCategory.SWEETENER: "감미료",
            IngredientCategory.FILLER: "필러"
        }
        return names.get(self, "???")


@dataclass
class Ingredient(Item):
    """
    재료 아이템

    돈스타브 스타일:
    - 카테고리: 고기, 채소 등
    - 가치(value): 레시피 계산에 사용
    - 신선도: 시간에 따라 감소 (선택적)
    """
    category: IngredientCategory = IngredientCategory.FILLER
    food_value: float = 1.0  # 요리 가치 (레시피 계산용)

    # 신선도 (0.0 ~ 1.0)
    freshness: float = 1.0
    spoil_time: int = 0  # 부패 시간 (턴 단위, 0 = 부패하지 않음)

    # 생으로 먹을 수 있는지
    edible_raw: bool = False
    raw_hp_restore: int = 0
    raw_mp_restore: int = 0

    def spoil(self, turns: int = 1):
        """
        부패 진행

        Args:
            turns: 경과 턴 수
        """
        if self.spoil_time > 0:
            self.freshness = max(0.0, self.freshness - (turns / self.spoil_time))

    def is_spoiled(self) -> bool:
        """부패 여부"""
        return self.freshness <= 0.0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "weight": self.weight,
            "sell_price": self.sell_price,
            "category": self.category.value,
            "food_value": self.food_value,
            "freshness": self.freshness,
            "spoil_time": self.spoil_time,
            "edible_raw": self.edible_raw,
            "raw_hp_restore": self.raw_hp_restore,
            "raw_mp_restore": self.raw_mp_restore
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ingredient":
        """딕셔너리에서 복원"""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            item_type=ItemType(data.get("item_type", "material")),
            rarity=ItemRarity(data.get("rarity", "common")),
            weight=data.get("weight", 0.5),
            sell_price=data.get("sell_price", 10),
            category=IngredientCategory(data["category"]),
            food_value=data.get("food_value", 1.0),
            freshness=data.get("freshness", 1.0),
            spoil_time=data.get("spoil_time", 0),
            edible_raw=data.get("edible_raw", False),
            raw_hp_restore=data.get("raw_hp_restore", 0),
            raw_mp_restore=data.get("raw_mp_restore", 0)
        )


class IngredientDatabase:
    """재료 데이터베이스"""

    # 재료 정의
    INGREDIENTS = {
        # === 고기 ===
        "monster_meat": Ingredient(
            item_id="monster_meat",
            name="몬스터 고기",
            description="몬스터에게서 얻은 고기. 날것으로 먹으면 위험하다.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=5,
            category=IngredientCategory.MEAT,
            food_value=1.0,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=0
        ),

        "beast_meat": Ingredient(
            item_id="beast_meat",
            name="야수 고기",
            description="야수에게서 얻은 질 좋은 고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.8,
            sell_price=15,
            category=IngredientCategory.MEAT,
            food_value=2.0,
            spoil_time=80,
            edible_raw=True,
            raw_hp_restore=10,
            raw_mp_restore=0
        ),

        "dragon_meat": Ingredient(
            item_id="dragon_meat",
            name="드래곤 고기",
            description="드래곤의 고기. 마력이 깃들어 있다.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.RARE,
            weight=1.2,
            sell_price=50,
            category=IngredientCategory.MEAT,
            food_value=3.0,
            spoil_time=120,
            edible_raw=True,
            raw_hp_restore=20,
            raw_mp_restore=10
        ),

        # === 채소 ===
        "carrot": Ingredient(
            item_id="carrot",
            name="당근",
            description="신선한 당근.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=3,
            category=IngredientCategory.VEGETABLE,
            food_value=1.0,
            spoil_time=150,
            edible_raw=True,
            raw_hp_restore=3,
            raw_mp_restore=0
        ),

        "potato": Ingredient(
            item_id="potato",
            name="감자",
            description="평범한 감자.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=3,
            category=IngredientCategory.VEGETABLE,
            food_value=1.0,
            spoil_time=200,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=0
        ),

        "magic_herb": Ingredient(
            item_id="magic_herb",
            name="마법 허브",
            description="마력이 담긴 허브. 요리에 넣으면 MP 회복 효과가 있다.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.1,
            sell_price=20,
            category=IngredientCategory.VEGETABLE,
            food_value=1.5,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=0,
            raw_mp_restore=10
        ),

        # === 과일 ===
        "berry": Ingredient(
            item_id="berry",
            name="베리",
            description="달콤한 베리.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=5,
            category=IngredientCategory.FRUIT,
            food_value=0.5,
            spoil_time=80,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=0
        ),

        "apple": Ingredient(
            item_id="apple",
            name="사과",
            description="빨갛고 아삭한 사과.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=5,
            category=IngredientCategory.FRUIT,
            food_value=1.0,
            spoil_time=120,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        # === 버섯 ===
        "red_mushroom": Ingredient(
            item_id="red_mushroom",
            name="붉은 버섯",
            description="독이 있어 보이는 붉은 버섯.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=10,
            category=IngredientCategory.MUSHROOM,
            food_value=0.5,
            spoil_time=200,
            edible_raw=False,  # 날것 먹으면 위험
            raw_hp_restore=-10,
            raw_mp_restore=0
        ),

        "blue_mushroom": Ingredient(
            item_id="blue_mushroom",
            name="푸른 버섯",
            description="마력이 담긴 푸른 버섯.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.1,
            sell_price=15,
            category=IngredientCategory.MUSHROOM,
            food_value=1.0,
            spoil_time=200,
            edible_raw=True,
            raw_hp_restore=0,
            raw_mp_restore=15
        ),

        # === 생선 ===
        "fish": Ingredient(
            item_id="fish",
            name="물고기",
            description="신선한 물고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=10,
            category=IngredientCategory.FISH,
            food_value=1.0,
            spoil_time=60,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        # === 향신료 ===
        "spice": Ingredient(
            item_id="spice",
            name="향신료",
            description="요리의 풍미를 높여주는 향신료.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.05,
            sell_price=20,
            category=IngredientCategory.SPICE,
            food_value=0.5,
            spoil_time=0,  # 부패하지 않음
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 감미료 ===
        "honey": Ingredient(
            item_id="honey",
            name="꿀",
            description="달콤한 꿀.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.3,
            sell_price=15,
            category=IngredientCategory.SWEETENER,
            food_value=1.0,
            spoil_time=0,  # 부패하지 않음
            edible_raw=True,
            raw_hp_restore=10,
            raw_mp_restore=0
        ),

        # === 필러 (요리 실패 방지용) ===
        "ice": Ingredient(
            item_id="ice",
            name="얼음",
            description="차가운 얼음. 요리 재료로 쓸 수 있다.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=2,
            category=IngredientCategory.FILLER,
            food_value=0.5,
            spoil_time=50,
            edible_raw=True,
            raw_hp_restore=0,
            raw_mp_restore=5
        ),

        "stick": Ingredient(
            item_id="stick",
            name="나뭇가지",
            description="마른 나뭇가지. 연료나 요리 재료로 쓸 수 있다.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=1,
            category=IngredientCategory.FILLER,
            food_value=0.0,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 추가 고기류 ===
        "pork": Ingredient(
            item_id="pork",
            name="돼지고기",
            description="부드러운 돼지고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.6,
            sell_price=12,
            category=IngredientCategory.MEAT,
            food_value=1.5,
            spoil_time=90,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "chicken": Ingredient(
            item_id="chicken",
            name="닭고기",
            description="신선한 닭고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=10,
            category=IngredientCategory.MEAT,
            food_value=1.3,
            spoil_time=70,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "beef": Ingredient(
            item_id="beef",
            name="소고기",
            description="질 좋은 소고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.8,
            sell_price=18,
            category=IngredientCategory.MEAT,
            food_value=2.0,
            spoil_time=85,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "rabbit_meat": Ingredient(
            item_id="rabbit_meat",
            name="토끼고기",
            description="부드러운 토끼고기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.4,
            sell_price=8,
            category=IngredientCategory.MEAT,
            food_value=1.2,
            spoil_time=75,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 추가 채소류 ===
        "tomato": Ingredient(
            item_id="tomato",
            name="토마토",
            description="빨갛게 익은 토마토.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=4,
            category=IngredientCategory.VEGETABLE,
            food_value=0.8,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=4,
            raw_mp_restore=0
        ),

        "onion": Ingredient(
            item_id="onion",
            name="양파",
            description="향이 강한 양파.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=3,
            category=IngredientCategory.VEGETABLE,
            food_value=0.8,
            spoil_time=180,
            edible_raw=True,
            raw_hp_restore=2,
            raw_mp_restore=0
        ),

        "cabbage": Ingredient(
            item_id="cabbage",
            name="양배추",
            description="신선한 양배추.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=5,
            category=IngredientCategory.VEGETABLE,
            food_value=1.0,
            spoil_time=140,
            edible_raw=True,
            raw_hp_restore=3,
            raw_mp_restore=0
        ),

        "lettuce": Ingredient(
            item_id="lettuce",
            name="상추",
            description="아삭한 상추.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=3,
            category=IngredientCategory.VEGETABLE,
            food_value=0.7,
            spoil_time=60,
            edible_raw=True,
            raw_hp_restore=2,
            raw_mp_restore=0
        ),

        "pumpkin": Ingredient(
            item_id="pumpkin",
            name="호박",
            description="커다란 호박.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=1.0,
            sell_price=8,
            category=IngredientCategory.VEGETABLE,
            food_value=1.5,
            spoil_time=200,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "garlic": Ingredient(
            item_id="garlic",
            name="마늘",
            description="향이 강한 마늘.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.05,
            sell_price=4,
            category=IngredientCategory.VEGETABLE,
            food_value=0.5,
            spoil_time=250,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "radish": Ingredient(
            item_id="radish",
            name="무",
            description="아삭한 무.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.4,
            sell_price=4,
            category=IngredientCategory.VEGETABLE,
            food_value=0.9,
            spoil_time=160,
            edible_raw=True,
            raw_hp_restore=3,
            raw_mp_restore=0
        ),

        "spinach": Ingredient(
            item_id="spinach",
            name="시금치",
            description="영양이 풍부한 시금치.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=5,
            category=IngredientCategory.VEGETABLE,
            food_value=1.0,
            spoil_time=50,
            edible_raw=True,
            raw_hp_restore=4,
            raw_mp_restore=2
        ),

        # === 추가 과일류 ===
        "orange": Ingredient(
            item_id="orange",
            name="오렌지",
            description="새콤달콤한 오렌지.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=6,
            category=IngredientCategory.FRUIT,
            food_value=1.0,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=7,
            raw_mp_restore=0
        ),

        "banana": Ingredient(
            item_id="banana",
            name="바나나",
            description="달콤한 바나나.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=5,
            category=IngredientCategory.FRUIT,
            food_value=1.1,
            spoil_time=60,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        "grape": Ingredient(
            item_id="grape",
            name="포도",
            description="달콤한 포도.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=7,
            category=IngredientCategory.FRUIT,
            food_value=0.8,
            spoil_time=70,
            edible_raw=True,
            raw_hp_restore=6,
            raw_mp_restore=0
        ),

        "peach": Ingredient(
            item_id="peach",
            name="복숭아",
            description="향긋한 복숭아.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=7,
            category=IngredientCategory.FRUIT,
            food_value=1.0,
            spoil_time=80,
            edible_raw=True,
            raw_hp_restore=7,
            raw_mp_restore=0
        ),

        "strawberry": Ingredient(
            item_id="strawberry",
            name="딸기",
            description="빨간 딸기.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=8,
            category=IngredientCategory.FRUIT,
            food_value=0.7,
            spoil_time=50,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=0
        ),

        "watermelon": Ingredient(
            item_id="watermelon",
            name="수박",
            description="시원한 수박.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=2.0,
            sell_price=12,
            category=IngredientCategory.FRUIT,
            food_value=1.5,
            spoil_time=90,
            edible_raw=True,
            raw_hp_restore=12,
            raw_mp_restore=0
        ),

        # === 추가 버섯류 ===
        "white_mushroom": Ingredient(
            item_id="white_mushroom",
            name="흰버섯",
            description="일반적인 흰버섯.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=8,
            category=IngredientCategory.MUSHROOM,
            food_value=0.8,
            spoil_time=180,
            edible_raw=True,
            raw_hp_restore=4,
            raw_mp_restore=0
        ),

        "black_mushroom": Ingredient(
            item_id="black_mushroom",
            name="검은버섯",
            description="희귀한 검은버섯.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.RARE,
            weight=0.1,
            sell_price=30,
            category=IngredientCategory.MUSHROOM,
            food_value=2.0,
            spoil_time=220,
            edible_raw=True,
            raw_hp_restore=15,
            raw_mp_restore=20
        ),

        "golden_mushroom": Ingredient(
            item_id="golden_mushroom",
            name="황금버섯",
            description="전설의 황금버섯.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.EPIC,
            weight=0.1,
            sell_price=100,
            category=IngredientCategory.MUSHROOM,
            food_value=5.0,
            spoil_time=300,
            edible_raw=True,
            raw_hp_restore=50,
            raw_mp_restore=50
        ),

        # === 추가 생선류 ===
        "salmon": Ingredient(
            item_id="salmon",
            name="연어",
            description="신선한 연어.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.8,
            sell_price=18,
            category=IngredientCategory.FISH,
            food_value=1.8,
            spoil_time=65,
            edible_raw=True,
            raw_hp_restore=12,
            raw_mp_restore=0
        ),

        "tuna": Ingredient(
            item_id="tuna",
            name="참치",
            description="고급 참치.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=1.0,
            sell_price=22,
            category=IngredientCategory.FISH,
            food_value=2.0,
            spoil_time=70,
            edible_raw=True,
            raw_hp_restore=15,
            raw_mp_restore=0
        ),

        "shrimp": Ingredient(
            item_id="shrimp",
            name="새우",
            description="싱싱한 새우.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=10,
            category=IngredientCategory.FISH,
            food_value=1.0,
            spoil_time=40,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "crab": Ingredient(
            item_id="crab",
            name="게",
            description="큰 게.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.6,
            sell_price=15,
            category=IngredientCategory.FISH,
            food_value=1.5,
            spoil_time=45,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "eel": Ingredient(
            item_id="eel",
            name="장어",
            description="영양가 높은 장어.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.7,
            sell_price=25,
            category=IngredientCategory.FISH,
            food_value=2.5,
            spoil_time=50,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 달걀류 ===
        "egg": Ingredient(
            item_id="egg",
            name="달걀",
            description="신선한 달걀.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=5,
            category=IngredientCategory.EGG,
            food_value=1.0,
            spoil_time=150,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "duck_egg": Ingredient(
            item_id="duck_egg",
            name="오리알",
            description="큼직한 오리알.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.15,
            sell_price=7,
            category=IngredientCategory.EGG,
            food_value=1.2,
            spoil_time=140,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "quail_egg": Ingredient(
            item_id="quail_egg",
            name="메추리알",
            description="작은 메추리알.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.05,
            sell_price=4,
            category=IngredientCategory.EGG,
            food_value=0.7,
            spoil_time=120,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 유제품 ===
        "milk": Ingredient(
            item_id="milk",
            name="우유",
            description="신선한 우유.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=8,
            category=IngredientCategory.DAIRY,
            food_value=1.0,
            spoil_time=80,
            edible_raw=True,
            raw_hp_restore=10,
            raw_mp_restore=5
        ),

        "cheese": Ingredient(
            item_id="cheese",
            name="치즈",
            description="숙성된 치즈.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.3,
            sell_price=15,
            category=IngredientCategory.DAIRY,
            food_value=1.5,
            spoil_time=200,
            edible_raw=True,
            raw_hp_restore=12,
            raw_mp_restore=0
        ),

        "butter": Ingredient(
            item_id="butter",
            name="버터",
            description="고소한 버터.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.2,
            sell_price=10,
            category=IngredientCategory.DAIRY,
            food_value=1.0,
            spoil_time=150,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        "cream": Ingredient(
            item_id="cream",
            name="크림",
            description="부드러운 크림.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.2,
            sell_price=12,
            category=IngredientCategory.DAIRY,
            food_value=1.2,
            spoil_time=60,
            edible_raw=True,
            raw_hp_restore=10,
            raw_mp_restore=5
        ),

        # === 곡물류 ===
        "rice": Ingredient(
            item_id="rice",
            name="쌀",
            description="하얀 쌀.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=8,
            category=IngredientCategory.GRAIN,
            food_value=1.5,
            spoil_time=0,  # 부패하지 않음
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "wheat": Ingredient(
            item_id="wheat",
            name="밀",
            description="황금색 밀.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=7,
            category=IngredientCategory.GRAIN,
            food_value=1.4,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "flour": Ingredient(
            item_id="flour",
            name="밀가루",
            description="곱게 빻은 밀가루.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=10,
            category=IngredientCategory.GRAIN,
            food_value=1.5,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "corn": Ingredient(
            item_id="corn",
            name="옥수수",
            description="달콤한 옥수수.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=6,
            category=IngredientCategory.GRAIN,
            food_value=1.2,
            spoil_time=120,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        "oat": Ingredient(
            item_id="oat",
            name="귀리",
            description="영양가 높은 귀리.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.4,
            sell_price=7,
            category=IngredientCategory.GRAIN,
            food_value=1.3,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        # === 추가 향신료 ===
        "pepper": Ingredient(
            item_id="pepper",
            name="후추",
            description="알싸한 후추.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.05,
            sell_price=15,
            category=IngredientCategory.SPICE,
            food_value=0.3,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "salt": Ingredient(
            item_id="salt",
            name="소금",
            description="요리의 기본, 소금.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=5,
            category=IngredientCategory.SPICE,
            food_value=0.2,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "cinnamon": Ingredient(
            item_id="cinnamon",
            name="계피",
            description="향긋한 계피.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.05,
            sell_price=20,
            category=IngredientCategory.SPICE,
            food_value=0.5,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "ginger": Ingredient(
            item_id="ginger",
            name="생강",
            description="매운 생강.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=8,
            category=IngredientCategory.SPICE,
            food_value=0.5,
            spoil_time=180,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "chili": Ingredient(
            item_id="chili",
            name="고추",
            description="매운 고추.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.05,
            sell_price=6,
            category=IngredientCategory.SPICE,
            food_value=0.4,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=1,
            raw_mp_restore=0
        ),

        # === 추가 감미료 ===
        "sugar": Ingredient(
            item_id="sugar",
            name="설탕",
            description="달콤한 설탕.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=10,
            category=IngredientCategory.SWEETENER,
            food_value=0.8,
            spoil_time=0,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=0
        ),

        "maple_syrup": Ingredient(
            item_id="maple_syrup",
            name="메이플 시럽",
            description="달콤한 메이플 시럽.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.UNCOMMON,
            weight=0.4,
            sell_price=20,
            category=IngredientCategory.SWEETENER,
            food_value=1.5,
            spoil_time=0,
            edible_raw=True,
            raw_hp_restore=15,
            raw_mp_restore=0
        ),

        "molasses": Ingredient(
            item_id="molasses",
            name="당밀",
            description="진한 당밀.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=12,
            category=IngredientCategory.SWEETENER,
            food_value=1.0,
            spoil_time=0,
            edible_raw=True,
            raw_hp_restore=10,
            raw_mp_restore=0
        ),

        # === 추가 필러 ===
        "water": Ingredient(
            item_id="water",
            name="물",
            description="깨끗한 물.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.5,
            sell_price=1,
            category=IngredientCategory.FILLER,
            food_value=0.1,
            spoil_time=0,
            edible_raw=True,
            raw_hp_restore=5,
            raw_mp_restore=5
        ),

        "oil": Ingredient(
            item_id="oil",
            name="식용유",
            description="요리용 기름.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=8,
            category=IngredientCategory.FILLER,
            food_value=0.5,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),

        "seaweed": Ingredient(
            item_id="seaweed",
            name="해초",
            description="바다의 해초.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.1,
            sell_price=5,
            category=IngredientCategory.FILLER,
            food_value=0.6,
            spoil_time=100,
            edible_raw=True,
            raw_hp_restore=3,
            raw_mp_restore=5
        ),

        "tofu": Ingredient(
            item_id="tofu",
            name="두부",
            description="부드러운 두부.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=6,
            category=IngredientCategory.FILLER,
            food_value=1.0,
            spoil_time=70,
            edible_raw=True,
            raw_hp_restore=8,
            raw_mp_restore=0
        ),

        "soy_sauce": Ingredient(
            item_id="soy_sauce",
            name="간장",
            description="짜고 고소한 간장.",
            item_type=ItemType.MATERIAL,
            rarity=ItemRarity.COMMON,
            weight=0.3,
            sell_price=8,
            category=IngredientCategory.FILLER,
            food_value=0.5,
            spoil_time=0,
            edible_raw=False,
            raw_hp_restore=0,
            raw_mp_restore=0
        ),
    }

    @classmethod
    def get_ingredient(cls, ingredient_id: str) -> Optional[Ingredient]:
        """재료 가져오기"""
        template = cls.INGREDIENTS.get(ingredient_id)
        if template:
            # 복사본 반환 (신선도 등이 개별적으로 관리되도록)
            return Ingredient(
                item_id=template.item_id,
                name=template.name,
                description=template.description,
                item_type=ItemType.MATERIAL,
                rarity=template.rarity,
                weight=template.weight,
                sell_price=template.sell_price,
                category=template.category,
                food_value=template.food_value,
                freshness=template.freshness,
                spoil_time=template.spoil_time,
                edible_raw=template.edible_raw,
                raw_hp_restore=template.raw_hp_restore,
                raw_mp_restore=template.raw_mp_restore
            )
        return None

    @classmethod
    def get_all_ingredient_ids(cls) -> list:
        """모든 재료 ID 목록"""
        return list(cls.INGREDIENTS.keys())
