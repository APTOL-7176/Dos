"""
월드 탐험 시스템

플레이어가 던전을 돌아다니며 적과 조우하고 기믹과 상호작용
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from src.world.dungeon_generator import DungeonMap
from src.world.tile import Tile, TileType
from src.world.fov import FOVSystem
from src.core.logger import get_logger, Loggers


logger = get_logger(Loggers.WORLD)


class ExplorationEvent(Enum):
    """탐험 이벤트"""
    NONE = "none"
    COMBAT = "combat"
    ITEM_FOUND = "item_found"
    TRAP_TRIGGERED = "trap_triggered"
    TELEPORT = "teleport"
    HEAL = "heal"
    STAIRS_UP = "stairs_up"
    STAIRS_DOWN = "stairs_down"
    LOCKED_DOOR = "locked_door"
    KEY_FOUND = "key_found"
    CHEST_FOUND = "chest_found"
    BOSS_ROOM = "boss_room"


@dataclass
class Player:
    """플레이어 정보"""
    x: int
    y: int
    party: List[Any]  # 파티원 리스트
    inventory: List[str] = None  # 아이템
    keys: List[str] = None  # 열쇠
    fov_radius: int = 3  # 시야 반지름

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.keys is None:
            self.keys = []


@dataclass
class ExplorationResult:
    """탐험 결과"""
    success: bool
    event: ExplorationEvent
    message: str = ""
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class ExplorationSystem:
    """탐험 시스템"""

    def __init__(self, dungeon: DungeonMap, party: List[Any]):
        self.dungeon = dungeon
        self.player = Player(
            x=dungeon.stairs_up[0] if dungeon.stairs_up else 5,
            y=dungeon.stairs_up[1] if dungeon.stairs_up else 5,
            party=party
        )
        self.fov_system = FOVSystem(default_radius=3)
        self.floor_number = 1
        self.explored_tiles = set()

        # 초기 FOV 계산
        self.update_fov()

        logger.info(f"탐험 시작: 층 {self.floor_number}, 위치 ({self.player.x}, {self.player.y})")

    def update_fov(self):
        """시야 업데이트"""
        # 이전 visible 초기화
        self.fov_system.clear_visibility(self.dungeon)

        # FOV 계산
        visible = self.fov_system.compute_fov(
            self.dungeon,
            self.player.x,
            self.player.y,
            self.player.fov_radius
        )

        # 탐험한 타일 누적
        self.explored_tiles.update(visible)

    def can_move(self, dx: int, dy: int) -> bool:
        """이동 가능 여부"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        return self.dungeon.is_walkable(new_x, new_y)

    def move_player(self, dx: int, dy: int) -> ExplorationResult:
        """
        플레이어 이동

        Args:
            dx: X 방향 이동량
            dy: Y 방향 이동량

        Returns:
            ExplorationResult
        """
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # 이동 가능 체크
        if not self.dungeon.is_walkable(new_x, new_y):
            tile = self.dungeon.get_tile(new_x, new_y)
            if tile and tile.tile_type == TileType.LOCKED_DOOR:
                return self._handle_locked_door(tile)
            return ExplorationResult(
                success=False,
                event=ExplorationEvent.NONE,
                message="이동할 수 없습니다"
            )

        # 이동
        self.player.x = new_x
        self.player.y = new_y

        # FOV 업데이트
        self.update_fov()

        # 타일 이벤트 체크
        tile = self.dungeon.get_tile(new_x, new_y)
        return self._check_tile_event(tile)

    def _check_tile_event(self, tile: Tile) -> ExplorationResult:
        """타일 이벤트 확인"""
        if tile.tile_type == TileType.TRAP:
            return self._handle_trap(tile)

        elif tile.tile_type == TileType.TELEPORTER:
            return self._handle_teleporter(tile)

        elif tile.tile_type == TileType.LAVA:
            return self._handle_lava(tile)

        elif tile.tile_type == TileType.HEALING_SPRING:
            return self._handle_healing_spring(tile)

        elif tile.tile_type == TileType.STAIRS_UP:
            return ExplorationResult(
                success=True,
                event=ExplorationEvent.STAIRS_UP,
                message="위층으로 올라가는 계단입니다"
            )

        elif tile.tile_type == TileType.STAIRS_DOWN:
            return ExplorationResult(
                success=True,
                event=ExplorationEvent.STAIRS_DOWN,
                message="아래층으로 내려가는 계단입니다"
            )

        elif tile.tile_type == TileType.CHEST:
            return self._handle_chest(tile)

        elif tile.tile_type == TileType.KEY:
            return self._handle_key(tile)

        elif tile.tile_type == TileType.BOSS_ROOM:
            return ExplorationResult(
                success=True,
                event=ExplorationEvent.BOSS_ROOM,
                message="⚠ 보스의 기운이 느껴집니다..."
            )

        # 랜덤 전투 조우 (5% 확률)
        if tile.tile_type == TileType.FLOOR and random.random() < 0.05:
            return self._trigger_combat()

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.NONE,
            message=""
        )

    def _handle_trap(self, tile: Tile) -> ExplorationResult:
        """함정 처리"""
        damage = tile.trap_damage

        # 파티원들에게 데미지
        for member in self.player.party:
            if hasattr(member, 'take_damage'):
                member.take_damage(damage)

        logger.info(f"함정 발동! 파티 전체 {damage} 데미지")

        # 타일 제거 (일회용)
        tile.tile_type = TileType.FLOOR
        tile.trap_damage = 0

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.TRAP_TRIGGERED,
            message=f"💥 함정! 파티 전체 {damage} 데미지!",
            data={"damage": damage}
        )

    def _handle_teleporter(self, tile: Tile) -> ExplorationResult:
        """텔레포터 처리"""
        if tile.teleport_target:
            self.player.x, self.player.y = tile.teleport_target
            self.update_fov()

            logger.info(f"텔레포트: {tile.teleport_target}")

            return ExplorationResult(
                success=True,
                event=ExplorationEvent.TELEPORT,
                message="🌀 텔레포트!",
                data={"target": tile.teleport_target}
            )

        return ExplorationResult(success=True, event=ExplorationEvent.NONE)

    def _handle_lava(self, tile: Tile) -> ExplorationResult:
        """용암 처리"""
        damage = tile.trap_damage

        for member in self.player.party:
            if hasattr(member, 'take_damage'):
                member.take_damage(damage)

        logger.info(f"용암 데미지: {damage}")

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.TRAP_TRIGGERED,
            message=f"🔥 뜨거워! {damage} 화상 데미지!",
            data={"damage": damage}
        )

    def _handle_healing_spring(self, tile: Tile) -> ExplorationResult:
        """치유의 샘 처리"""
        heal_amount = 50

        for member in self.player.party:
            if hasattr(member, 'heal'):
                member.heal(heal_amount)

        logger.info(f"치유의 샘: {heal_amount} HP 회복")

        # 일회용
        tile.tile_type = TileType.FLOOR

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.HEAL,
            message=f"💧 치유의 샘! 파티 전체 {heal_amount} HP 회복!",
            data={"heal": heal_amount}
        )

    def _handle_chest(self, tile: Tile) -> ExplorationResult:
        """보물상자 처리"""
        loot_id = tile.loot_id or "random_item"
        self.player.inventory.append(loot_id)

        logger.info(f"보물상자 획득: {loot_id}")

        # 상자 제거
        tile.tile_type = TileType.FLOOR
        tile.loot_id = None

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.CHEST_FOUND,
            message=f"📦 보물상자 발견! {loot_id} 획득!",
            data={"item": loot_id}
        )

    def _handle_key(self, tile: Tile) -> ExplorationResult:
        """열쇠 처리"""
        key_id = tile.key_id or "key_unknown"
        self.player.keys.append(key_id)

        logger.info(f"열쇠 획득: {key_id}")

        # 열쇠 제거
        tile.tile_type = TileType.FLOOR
        tile.key_id = None

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.KEY_FOUND,
            message=f"🔑 열쇠 발견! {key_id} 획득!",
            data={"key": key_id}
        )

    def _handle_locked_door(self, tile: Tile) -> ExplorationResult:
        """잠긴 문 처리"""
        key_id = tile.key_id

        if key_id in self.player.keys:
            # 열쇠가 있으면 문 열기
            tile.unlock()
            logger.info(f"문 잠금 해제: {key_id}")

            return ExplorationResult(
                success=True,
                event=ExplorationEvent.LOCKED_DOOR,
                message=f"🔓 문을 열었습니다! ({key_id})"
            )
        else:
            return ExplorationResult(
                success=False,
                event=ExplorationEvent.LOCKED_DOOR,
                message=f"🔒 잠겨있습니다. {key_id}가 필요합니다.",
                data={"required_key": key_id}
            )

    def _trigger_combat(self) -> ExplorationResult:
        """전투 조우"""
        # 적 생성 (층수에 따라)
        num_enemies = min(4, 1 + self.floor_number // 3)

        logger.info(f"전투 조우! 적 {num_enemies}명")

        return ExplorationResult(
            success=True,
            event=ExplorationEvent.COMBAT,
            message=f"⚔ 적 출현! {num_enemies}마리!",
            data={"num_enemies": num_enemies, "floor": self.floor_number}
        )

    def descend_floor(self):
        """다음 층으로"""
        self.floor_number += 1
        logger.info(f"층 이동: {self.floor_number}층")

        # 새 던전 생성 필요
        # (이건 외부에서 처리)

    def ascend_floor(self):
        """이전 층으로"""
        if self.floor_number > 1:
            self.floor_number -= 1
            logger.info(f"층 이동: {self.floor_number}층")
