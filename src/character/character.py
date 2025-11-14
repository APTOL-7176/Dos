"""
Character - 캐릭터 클래스

StatManager를 통합한 확장 가능한 캐릭터 시스템
YAML 기반 직업 데이터 로딩
"""

from typing import Dict, Any, Optional, List
from src.character.stats import StatManager, Stats, GrowthType
from src.character.character_loader import (
    load_character_data,
    get_base_stats,
    get_gimmick,
    get_traits,
    get_skills,
    get_bonuses
)
from src.core.event_bus import event_bus, Events
from src.core.logger import get_logger


class Character:
    """
    게임 캐릭터 클래스

    StatManager를 사용하여 모든 스탯을 관리합니다.
    """

    def __init__(
        self,
        name: str,
        character_class: str,
        level: int = 1,
        stats_config: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.character_class = character_class
        self.job_id = character_class  # job_id는 character_class의 별칭
        self.level = level

        self.logger = get_logger("character")

        # YAML에서 직업 데이터 로드
        self.class_data = load_character_data(character_class)

        # job_name 설정 (YAML의 class_name)
        self.job_name = self.class_data.get('class_name', character_class)

        # StatManager 초기화
        if stats_config is None:
            stats_config = self._get_stats_from_yaml()

        self.stat_manager = StatManager(stats_config)

        # 현재 HP/MP (StatManager와 별도 관리)
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp

        # 전투 관련 - BRV 시스템 (직업별로 차별화)
        self.max_brv = self._calculate_max_brv()
        self.current_brv = self._calculate_init_brv()
        self.is_alive = True
        self.is_enemy = False  # 적 여부

        # 장비
        self.equipment: Dict[str, Any] = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }

        # 상태 효과 (간단한 구현)
        self.status_effects: List[Any] = []

        # 직업 기믹 초기화
        self.gimmick_data = get_gimmick(character_class)
        self._initialize_gimmick()

        # 특성 (Trait) - YAML에서 로드
        self.available_traits = get_traits(character_class)
        self.active_traits: List[Any] = []

        # 스킬 - YAML에서 로드
        self.skill_ids = get_skills(character_class)
        # TODO: skill_ids를 실제 Skill 객체로 변환
        # 임시로 skill_ids를 skills로 사용 (UI 호환성)
        self.skills = self._load_skills_from_ids(self.skill_ids)

        # 로그
        self.logger.info(f"캐릭터 생성: {self.name} ({self.character_class}), 스킬 {len(self.skills)}개")

        # 이벤트 발행
        event_bus.publish(Events.CHARACTER_CREATED, {
            "character": self,
            "name": self.name,
            "class": self.character_class
        })

    def _get_stats_from_yaml(self) -> Dict[str, Any]:
        """YAML에서 스탯 설정을 가져옵니다."""
        base_stats = get_base_stats(self.character_class)

        # YAML 필드명 → Stats enum 매핑
        stat_mapping = {
            "hp": Stats.HP,
            "mp": Stats.MP,
            "init_brv": Stats.INIT_BRV,
            "physical_attack": Stats.STRENGTH,
            "physical_defense": Stats.DEFENSE,
            "magic_attack": Stats.MAGIC,
            "magic_defense": Stats.SPIRIT,
            "speed": Stats.SPEED,
        }

        stats_config = {}

        for yaml_key, stat_enum in stat_mapping.items():
            base_value = base_stats.get(yaml_key, 50)

            # 성장률 설정 (기본값)
            if yaml_key == "hp":
                growth_rate = 10
                growth_type = "linear"
            elif yaml_key == "mp":
                growth_rate = 5
                growth_type = "linear"
            elif yaml_key == "init_brv":
                growth_rate = 50
                growth_type = "linear"
            elif yaml_key in ["physical_attack", "magic_attack"]:
                growth_rate = 1.1
                growth_type = "exponential"
            elif yaml_key in ["physical_defense", "magic_defense"]:
                growth_rate = 1.08
                growth_type = "exponential"
            elif yaml_key == "speed":
                growth_rate = 1.05
                growth_type = "exponential"
            else:
                growth_rate = 1.0
                growth_type = "linear"

            stats_config[stat_enum] = {
                "base_value": base_value,
                "growth_rate": growth_rate,
                "growth_type": growth_type
            }

        # 추가 스탯 (YAML에 없는 것들)
        stats_config[Stats.LUCK] = {
            "base_value": 5,
            "growth_rate": 0.5,
            "growth_type": "linear"
        }
        stats_config[Stats.ACCURACY] = {
            "base_value": 100,
            "growth_rate": 2,
            "growth_type": "logarithmic"
        }
        stats_config[Stats.EVASION] = {
            "base_value": 10,
            "growth_rate": 1,
            "growth_type": "logarithmic"
        }

        return stats_config

    def _initialize_gimmick(self) -> None:
        """직업별 기믹 시스템을 초기화합니다."""
        if not self.gimmick_data:
            return

        gimmick_type = self.gimmick_data.get("type")

        # 전사 - 6단계 스탠스 시스템
        if gimmick_type == "stance_system":
            self.current_stance = "balanced"
            self.stance_focus = 0
            self.available_stances = [s['id'] for s in self.gimmick_data.get('stances', [])]

        # 아크메이지 / 마법사 - 원소 카운트
        elif gimmick_type == "elemental_counter":
            self.fire_count = 0
            self.ice_count = 0
            self.lightning_count = 0

        # 궁수 - 조준 포인트
        elif gimmick_type == "aim_system":
            self.aim_points = 0
            self.max_aim_points = self.gimmick_data.get("max_aim", 5)

        # 도적 - 베놈 파워
        elif gimmick_type == "venom_system":
            self.venom_power = 0
            self.venom_power_max = self.gimmick_data.get("max_venom", 200)
            self.poison_stacks = 0
            self.max_poison_stacks = self.gimmick_data.get("max_poison", 10)

        # 암살자 - 그림자
        elif gimmick_type == "shadow_system":
            self.shadow_count = 0
            self.max_shadow_count = self.gimmick_data.get("max_shadows", 5)

        # 검성 - 검기
        elif gimmick_type == "sword_aura":
            self.sword_aura = 0
            self.max_sword_aura = self.gimmick_data.get("max_aura", 5)

        # 광전사 - 분노
        elif gimmick_type == "rage_system":
            self.rage_stacks = 0
            self.max_rage_stacks = self.gimmick_data.get("max_rage", 10)

        # 몽크 - 기 에너지
        elif gimmick_type == "ki_system":
            self.ki_energy = 0
            self.max_ki_energy = self.gimmick_data.get("max_ki", 100)
            self.combo_count = 0
            self.strike_marks = 0

        # 바드 - 멜로디
        elif gimmick_type == "melody_system":
            self.melody_stacks = 0
            self.max_melody_stacks = self.gimmick_data.get("max_melody", 7)
            self.melody_notes = []
            self.current_melody = ""

        # 네크로맨서 - 네크로 에너지
        elif gimmick_type == "necro_system":
            self.necro_energy = 0
            self.max_necro_energy = self.gimmick_data.get("max_necro", 50)
            self.soul_power = 0
            self.undead_count = 0

        # 정령술사 - 정령 친화도
        elif gimmick_type == "spirit_bond":
            self.spirit_bond = 0
            self.max_spirit_bond = self.gimmick_data.get("max_bond", 25)

        # 시간술사 - 시간 기록점
        elif gimmick_type == "time_system":
            self.time_marks = 0
            self.max_time_marks = self.gimmick_data.get("max_marks", 7)

        # 용기사 - 용의 표식
        elif gimmick_type == "dragon_marks":
            self.dragon_marks = 0
            self.max_dragon_marks = self.gimmick_data.get("max_marks", 3)

        # 검투사 - 투기장 포인트
        elif gimmick_type == "arena_system":
            self.arena_points = 0
            self.max_arena_points = self.gimmick_data.get("max_points", 20)

        self.logger.debug(f"{self.character_class} 기믹 초기화: {gimmick_type}")

    # ===== 스탯 프로퍼티 =====

    @property
    def max_hp(self) -> int:
        """최대 HP"""
        return int(self.stat_manager.get_value(Stats.HP))

    @property
    def max_mp(self) -> int:
        """최대 MP"""
        return int(self.stat_manager.get_value(Stats.MP))

    @property
    def init_brv(self) -> int:
        """초기 BRV (전투 시작 시)"""
        return int(self.stat_manager.get_value(Stats.INIT_BRV))

    @property
    def strength(self) -> int:
        """물리 공격력"""
        return int(self.stat_manager.get_value(Stats.STRENGTH))

    @property
    def defense(self) -> int:
        """물리 방어력"""
        return int(self.stat_manager.get_value(Stats.DEFENSE))

    @property
    def magic(self) -> int:
        """마법 공격력"""
        return int(self.stat_manager.get_value(Stats.MAGIC))

    @property
    def spirit(self) -> int:
        """마법 방어력"""
        return int(self.stat_manager.get_value(Stats.SPIRIT))

    @property
    def speed(self) -> int:
        """속도"""
        return int(self.stat_manager.get_value(Stats.SPEED))

    @property
    def luck(self) -> int:
        """행운"""
        return int(self.stat_manager.get_value(Stats.LUCK))

    @property
    def accuracy(self) -> int:
        """명중률"""
        return int(self.stat_manager.get_value(Stats.ACCURACY))

    @property
    def evasion(self) -> int:
        """회피율"""
        return int(self.stat_manager.get_value(Stats.EVASION))

    # ===== HP/MP 관리 =====

    def take_damage(self, damage: int) -> int:
        """
        데미지를 받습니다

        Args:
            damage: 데미지 양

        Returns:
            실제로 받은 데미지
        """
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

            event_bus.publish(Events.CHARACTER_DEATH, {
                "character": self,
                "name": self.name
            })

        event_bus.publish(Events.CHARACTER_HP_CHANGE, {
            "character": self,
            "change": -actual_damage,
            "current": self.current_hp,
            "max": self.max_hp
        })

        return actual_damage

    def heal(self, amount: int) -> int:
        """
        HP를 회복합니다

        Args:
            amount: 회복량

        Returns:
            실제로 회복한 양
        """
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        actual_heal = self.current_hp - old_hp

        event_bus.publish(Events.CHARACTER_HP_CHANGE, {
            "character": self,
            "change": actual_heal,
            "current": self.current_hp,
            "max": self.max_hp
        })

        return actual_heal

    def consume_mp(self, amount: int) -> bool:
        """
        MP를 소비합니다

        Args:
            amount: 소비량

        Returns:
            성공 여부
        """
        if self.current_mp < amount:
            return False

        self.current_mp -= amount

        event_bus.publish(Events.CHARACTER_MP_CHANGE, {
            "character": self,
            "change": -amount,
            "current": self.current_mp,
            "max": self.max_mp
        })

        return True

    def restore_mp(self, amount: int) -> int:
        """
        MP를 회복합니다

        Args:
            amount: 회복량

        Returns:
            실제로 회복한 양
        """
        old_mp = self.current_mp
        self.current_mp = min(self.current_mp + amount, self.max_mp)
        actual_restore = self.current_mp - old_mp

        event_bus.publish(Events.CHARACTER_MP_CHANGE, {
            "character": self,
            "change": actual_restore,
            "current": self.current_mp,
            "max": self.max_mp
        })

        return actual_restore

    # ===== 레벨업 =====

    def level_up(self) -> None:
        """레벨업"""
        old_level = self.level
        self.level += 1

        # StatManager를 통해 모든 스탯 성장
        self.stat_manager.apply_level_up(self.level)

        # HP/MP는 회복하지 않음 (전투 중 레벨업 시 밸런스)

        self.logger.info(f"{self.name} 레벨업: {old_level} → {self.level}")

        event_bus.publish(Events.CHARACTER_LEVEL_UP, {
            "character": self,
            "old_level": old_level,
            "new_level": self.level
        })

    # ===== 장비 =====

    def equip_item(self, slot: str, item: Any) -> None:
        """
        장비 장착

        Args:
            slot: 장비 슬롯 (weapon, armor, accessory)
            item: 아이템
        """
        if slot not in self.equipment:
            self.logger.warning(f"잘못된 장비 슬롯: {slot}")
            return

        # 기존 장비 해제
        if self.equipment[slot]:
            self.unequip_item(slot)

        self.equipment[slot] = item

        # 장비 보너스 적용
        if hasattr(item, "stat_bonuses"):
            for stat_name, bonus in item.stat_bonuses.items():
                self.stat_manager.add_bonus(stat_name, f"equipment_{slot}", bonus)

        event_bus.publish(Events.EQUIPMENT_EQUIPPED, {
            "character": self,
            "slot": slot,
            "item": item
        })

    def unequip_item(self, slot: str) -> Optional[Any]:
        """
        장비 해제

        Args:
            slot: 장비 슬롯

        Returns:
            해제된 아이템
        """
        item = self.equipment.get(slot)
        if not item:
            return None

        # 장비 보너스 제거
        if hasattr(item, "stat_bonuses"):
            for stat_name in item.stat_bonuses.keys():
                self.stat_manager.remove_bonus(stat_name, f"equipment_{slot}")

        self.equipment[slot] = None

        event_bus.publish(Events.EQUIPMENT_UNEQUIPPED, {
            "character": self,
            "slot": slot,
            "item": item
        })

        return item

    # ===== 스킬 로딩 =====

    def _load_skills_from_ids(self, skill_ids: List[str]) -> List[Any]:
        """스킬 ID로부터 스킬 객체 생성 (간단한 구현)"""
        skills = []
        for skill_id in skill_ids:
            # 임시 스킬 객체 (딕셔너리 형태)
            # TODO: 실제 Skill 클래스로 변환
            skill = type('SimpleSkill', (), {
                'skill_id': skill_id,
                'name': skill_id.replace('_', ' ').title(),
                'description': f'{skill_id} 스킬',
                'mp_cost': 10,  # 기본 MP 비용
                'brv_multiplier': 1.0,
                'hp_multiplier': 1.0,
            })()
            skills.append(skill)
        return skills

    # ===== BRV 계산 =====

    def _calculate_max_brv(self) -> int:
        """직업별 최대 BRV 계산"""
        # 기본 max BRV: 레벨 * 40
        base_max_brv = self.level * 40

        # 직업 아키타입에 따른 보정
        archetype = self.class_data.get('archetype', 'Balanced')

        if archetype == 'Tank':
            # 탱커: 낮은 BRV (0.8배)
            return int(base_max_brv * 0.8)
        elif archetype == 'Attacker':
            # 어택커: 높은 BRV (1.3배)
            return int(base_max_brv * 1.3)
        elif archetype == 'Mage':
            # 마법사: 중간 BRV (1.0배)
            return int(base_max_brv * 1.0)
        elif archetype == 'Healer':
            # 힐러: 낮은 BRV (0.7배)
            return int(base_max_brv * 0.7)
        elif archetype == 'Specialist':
            # 스페셜리스트: 중상 BRV (1.2배)
            return int(base_max_brv * 1.2)
        else:
            # 균형잡힌 직업 (1.0배)
            return base_max_brv

    def _calculate_init_brv(self) -> int:
        """전투 시작 시 초기 BRV 계산"""
        # 직업 아키타입에 따른 초기 BRV 비율
        archetype = self.class_data.get('archetype', 'Balanced')

        if archetype == 'Tank':
            # 탱커: 20% 시작 (방어에 집중)
            return int(self.max_brv * 0.2)
        elif archetype == 'Attacker':
            # 어택커: 30% 시작 (공격적)
            return int(self.max_brv * 0.3)
        elif archetype == 'Mage':
            # 마법사: 15% 시작 (마나 의존)
            return int(self.max_brv * 0.15)
        elif archetype == 'Healer':
            # 힐러: 10% 시작 (지원 역할)
            return int(self.max_brv * 0.1)
        elif archetype == 'Specialist':
            # 스페셜리스트: 25% 시작
            return int(self.max_brv * 0.25)
        else:
            # 균형잡힌 직업: 20% 시작
            return int(self.max_brv * 0.2)

    # ===== 유틸리티 =====

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (저장용)"""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "stats": self.stat_manager.to_dict(),
            "equipment": {
                slot: item.to_dict() if hasattr(item, "to_dict") else None
                for slot, item in self.equipment.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """딕셔너리에서 복원"""
        character = cls.__new__(cls)
        character.name = data["name"]
        character.character_class = data["character_class"]
        character.level = data["level"]
        character.current_hp = data["current_hp"]
        character.current_mp = data["current_mp"]

        # StatManager 복원
        character.stat_manager = StatManager.from_dict(data["stats"])

        # YAML 데이터 로드
        character.class_data = load_character_data(character.character_class)

        # BRV 시스템
        character.max_brv = character._calculate_max_brv()
        character.current_brv = 0  # 전투 밖에서는 0
        character.is_alive = character.current_hp > 0
        character.is_enemy = False
        character.equipment = {"weapon": None, "armor": None, "accessory": None}
        character.status_effects = []
        character.traits = []

        character.logger = get_logger("character")

        return character

    def __repr__(self) -> str:
        return f"Character({self.name}, {self.character_class}, Lv.{self.level})"
