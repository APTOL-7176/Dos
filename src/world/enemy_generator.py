"""
적 생성 시스템

층수에 따라 적절한 난이도의 적 생성
"""

from typing import List, Dict, Any
import random


class EnemyTemplate:
    """적 템플릿"""

    def __init__(
        self,
        enemy_id: str,
        name: str,
        level: int,
        hp: int,
        mp: int,
        physical_attack: int,
        physical_defense: int,
        magic_attack: int,
        magic_defense: int,
        speed: int,
        luck: int = 5,
        accuracy: int = 50,
        evasion: int = 10
    ):
        self.enemy_id = enemy_id
        self.name = name
        self.level = level
        self.hp = hp
        self.mp = mp
        self.physical_attack = physical_attack
        self.physical_defense = physical_defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.speed = speed
        self.luck = luck
        self.accuracy = accuracy
        self.evasion = evasion


# 적 템플릿 데이터베이스
ENEMY_TEMPLATES = {
    # Lv 1-5
    "slime": EnemyTemplate(
        "slime", "슬라임", 1,
        hp=30, mp=5,
        physical_attack=8, physical_defense=5,
        magic_attack=5, magic_defense=8,
        speed=5, luck=3, accuracy=45, evasion=5
    ),
    "goblin": EnemyTemplate(
        "goblin", "고블린", 2,
        hp=45, mp=10,
        physical_attack=12, physical_defense=8,
        magic_attack=6, magic_defense=7,
        speed=8, luck=5, accuracy=50, evasion=8
    ),
    "wolf": EnemyTemplate(
        "wolf", "늑대", 3,
        hp=55, mp=5,
        physical_attack=15, physical_defense=10,
        magic_attack=5, magic_defense=8,
        speed=12, luck=7, accuracy=55, evasion=12
    ),

    # Lv 6-10
    "orc": EnemyTemplate(
        "orc", "오크", 6,
        hp=90, mp=15,
        physical_attack=25, physical_defense=18,
        magic_attack=10, magic_defense=12,
        speed=10, luck=5, accuracy=52, evasion=8
    ),
    "skeleton": EnemyTemplate(
        "skeleton", "해골 전사", 7,
        hp=80, mp=20,
        physical_attack=28, physical_defense=15,
        magic_attack=12, magic_defense=15,
        speed=13, luck=8, accuracy=55, evasion=10
    ),
    "dark_mage": EnemyTemplate(
        "dark_mage", "다크 메이지", 8,
        hp=70, mp=60,
        physical_attack=15, physical_defense=12,
        magic_attack=35, magic_defense=25,
        speed=11, luck=10, accuracy=58, evasion=12
    ),

    # Lv 11-15
    "ogre": EnemyTemplate(
        "ogre", "오우거", 11,
        hp=150, mp=20,
        physical_attack=40, physical_defense=30,
        magic_attack=15, magic_defense=20,
        speed=8, luck=5, accuracy=50, evasion=5
    ),
    "wraith": EnemyTemplate(
        "wraith", "망령", 12,
        hp=110, mp=80,
        physical_attack=30, physical_defense=20,
        magic_attack=50, magic_defense=40,
        speed=15, luck=12, accuracy=60, evasion=18
    ),
    "golem": EnemyTemplate(
        "golem", "골렘", 13,
        hp=200, mp=10,
        physical_attack=35, physical_defense=50,
        magic_attack=10, magic_defense=30,
        speed=5, luck=3, accuracy=48, evasion=3
    ),

    # Lv 16-20
    "troll": EnemyTemplate(
        "troll", "트롤", 16,
        hp=250, mp=30,
        physical_attack=55, physical_defense=40,
        magic_attack=20, magic_defense=25,
        speed=10, luck=8, accuracy=52, evasion=8
    ),
    "vampire": EnemyTemplate(
        "vampire", "뱀파이어", 18,
        hp=180, mp=100,
        physical_attack=50, physical_defense=35,
        magic_attack=60, magic_defense=45,
        speed=20, luck=15, accuracy=65, evasion=20
    ),
    "wyvern": EnemyTemplate(
        "wyvern", "와이번", 19,
        hp=220, mp=50,
        physical_attack=60, physical_defense=45,
        magic_attack=40, magic_defense=35,
        speed=18, luck=12, accuracy=58, evasion=15
    ),

    # Lv 21-25
    "demon": EnemyTemplate(
        "demon", "악마", 22,
        hp=300, mp=150,
        physical_attack=70, physical_defense=50,
        magic_attack=80, magic_defense=60,
        speed=16, luck=15, accuracy=62, evasion=18
    ),
    "dragon": EnemyTemplate(
        "dragon", "드래곤", 25,
        hp=500, mp=200,
        physical_attack=90, physical_defense=70,
        magic_attack=100, magic_defense=80,
        speed=15, luck=20, accuracy=65, evasion=12
    ),

    # 보스
    "boss_chimera": EnemyTemplate(
        "boss_chimera", "키메라 (보스)", 10,
        hp=400, mp=100,
        physical_attack=50, physical_defense=35,
        magic_attack=50, magic_defense=35,
        speed=14, luck=15, accuracy=60, evasion=15
    ),
    "boss_lich": EnemyTemplate(
        "boss_lich", "리치 (보스)", 20,
        hp=800, mp=500,
        physical_attack=60, physical_defense=50,
        magic_attack=120, magic_defense=90,
        speed=12, luck=20, accuracy=70, evasion=20
    ),
    "boss_dragon_king": EnemyTemplate(
        "boss_dragon_king", "드래곤 킹 (보스)", 30,
        hp=1500, mp=1000,
        physical_attack=120, physical_defense=100,
        magic_attack=150, magic_defense=120,
        speed=18, luck=25, accuracy=75, evasion=15
    ),

    # 최종 보스 - 세피로스 (15층)
    # 압도적인 스탯의 최종 보스 - 플레이어보다 훨씬 빠르게 행동
    "sephiroth": EnemyTemplate(
        "sephiroth", "세피로스", 15,
        hp=50000, mp=9999,
        physical_attack=300, physical_defense=250,
        magic_attack=400, magic_defense=300,
        speed=300, luck=50, accuracy=95, evasion=40
    ),
}


class SimpleEnemy:
    """간단한 적 클래스 (전투용)"""

    def __init__(self, template: EnemyTemplate, level_modifier: float = 1.0):
        self.name = template.name
        self.level = max(1, int(template.level * level_modifier))

        # 스탯 (레벨 보정)
        self.max_hp = int(template.hp * level_modifier)
        self.current_hp = self.max_hp
        self.max_mp = int(template.mp * level_modifier)
        self.current_mp = self.max_mp

        self.physical_attack = int(template.physical_attack * level_modifier)
        self.physical_defense = int(template.physical_defense * level_modifier)
        self.magic_attack = int(template.magic_attack * level_modifier)
        self.magic_defense = int(template.magic_defense * level_modifier)
        self.speed = template.speed
        self.luck = template.luck
        self.accuracy = template.accuracy
        self.evasion = template.evasion

        # BRV (적 타입과 레벨에 따라 차별화)
        self.max_brv = self._calculate_max_brv(template, level_modifier)
        self.current_brv = self._calculate_init_brv(template, level_modifier)

        # 상태
        self.is_alive = True
        self.status_effects = {}
        self.wound_damage = 0

        # 스킬 (간단하게)
        self.skills = []

    def _calculate_max_brv(self, template: EnemyTemplate, level_modifier: float) -> int:
        """적의 최대 BRV 계산 (레벨과 타입에 따라 다름)"""
        # 기본 최대 BRV: 레벨 * 30 (이전의 1/10 수준)
        base_max_brv = int(template.level * 30 * level_modifier)

        # 적 타입별 보정
        enemy_type = template.enemy_id
        if "boss" in enemy_type or enemy_type == "sephiroth":
            # 보스: 3배
            return int(base_max_brv * 3)
        elif enemy_type in ["dragon", "demon", "vampire"]:
            # 강력한 적: 2배
            return int(base_max_brv * 2)
        elif enemy_type in ["wraith", "dark_mage"]:
            # 마법사 계열: 1.5배
            return int(base_max_brv * 1.5)
        elif enemy_type in ["slime", "goblin"]:
            # 약한 적: 0.7배
            return int(base_max_brv * 0.7)
        else:
            # 기본
            return base_max_brv

    def _calculate_init_brv(self, template: EnemyTemplate, level_modifier: float) -> int:
        """적의 초기 BRV 계산 (최대 BRV의 일부)"""
        max_brv = self.max_brv if hasattr(self, 'max_brv') else self._calculate_max_brv(template, level_modifier)

        # 적 타입별 초기 BRV 비율
        enemy_type = template.enemy_id
        if "boss" in enemy_type or enemy_type == "sephiroth":
            # 보스: 50% 시작
            return int(max_brv * 0.5)
        elif enemy_type in ["wraith", "dark_mage", "vampire"]:
            # 마법사/언데드: 30% 시작
            return int(max_brv * 0.3)
        elif enemy_type in ["dragon", "demon", "troll"]:
            # 강력한 물리 적: 40% 시작
            return int(max_brv * 0.4)
        elif enemy_type in ["slime", "goblin", "wolf"]:
            # 약한 적: 10% 시작
            return int(max_brv * 0.1)
        else:
            # 기본: 20% 시작
            return int(max_brv * 0.2)

    def take_damage(self, damage: int) -> int:
        """데미지 받기"""
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

        return actual_damage

    def heal(self, amount: int) -> int:
        """회복"""
        actual_heal = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_heal
        return actual_heal


class EnemyGenerator:
    """적 생성기"""

    @staticmethod
    def generate_enemies(floor_number: int, num_enemies: int = None) -> List[SimpleEnemy]:
        """
        층수에 맞는 적 생성

        Args:
            floor_number: 층 번호
            num_enemies: 적 수 (None이면 자동)

        Returns:
            적 리스트
        """
        if num_enemies is None:
            # 층수에 따라 적 수 결정 (1~4)
            num_enemies = min(4, 1 + floor_number // 5)

        # 층수에 맞는 템플릿 선택
        suitable_templates = []
        for template in ENEMY_TEMPLATES.values():
            if "boss" in template.enemy_id:
                continue  # 보스는 제외

            # 층수 ±3 범위
            if abs(template.level - floor_number) <= 3:
                suitable_templates.append(template)

        if not suitable_templates:
            # 적합한 템플릿 없으면 가장 가까운 것
            suitable_templates = sorted(
                [t for t in ENEMY_TEMPLATES.values() if "boss" not in t.enemy_id],
                key=lambda t: abs(t.level - floor_number)
            )[:3]

        # 랜덤 선택
        enemies = []
        for _ in range(num_enemies):
            template = random.choice(suitable_templates)

            # 레벨 보정 (층수에 맞게)
            level_modifier = floor_number / max(1, template.level)
            level_modifier = max(0.5, min(2.0, level_modifier))  # 0.5배 ~ 2배

            enemy = SimpleEnemy(template, level_modifier)

            # 적 타입에 맞는 스킬 추가
            try:
                from src.combat.enemy_skills import EnemySkillDatabase
                enemy.skills = EnemySkillDatabase.get_skills_for_enemy_type(template.enemy_id)
            except ImportError:
                pass

            enemies.append(enemy)

        return enemies

    @staticmethod
    def generate_boss(floor_number: int) -> SimpleEnemy:
        """보스 생성"""
        # 층수에 맞는 보스 선택
        if floor_number == 15:
            # 15층: 세피로스 (최종 보스)
            template = ENEMY_TEMPLATES["sephiroth"]
        elif floor_number < 15:
            template = ENEMY_TEMPLATES["boss_chimera"]
        elif floor_number < 25:
            template = ENEMY_TEMPLATES["boss_lich"]
        else:
            template = ENEMY_TEMPLATES["boss_dragon_king"]

        level_modifier = floor_number / template.level
        level_modifier = max(1.0, level_modifier)  # 최소 1배

        boss = SimpleEnemy(template, level_modifier)

        # 세피로스일 경우 스킬 추가
        if floor_number == 15:
            try:
                from src.combat.enemy_skills import EnemySkillDatabase
                boss.skills = EnemySkillDatabase.get_skills_for_enemy_type("sephiroth")
            except ImportError:
                pass

        return boss
