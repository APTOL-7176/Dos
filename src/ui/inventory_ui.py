"""
인벤토리 UI

아이템 확인, 사용, 장비 착용
"""

import tcod.console
import tcod.event
from typing import List, Optional, Any
from enum import Enum

from src.equipment.inventory import Inventory
from src.equipment.item_system import Item, Equipment, Consumable, ItemType
from src.ui.tcod_display import Colors
from src.ui.input_handler import GameAction, InputHandler
from src.ui.cursor_menu import CursorMenu, MenuItem
from src.core.logger import get_logger


logger = get_logger("inventory_ui")


class InventoryMode(Enum):
    """인벤토리 모드"""
    BROWSE = "browse"  # 둘러보기
    USE_ITEM = "use_item"  # 아이템 사용
    EQUIP = "equip"  # 장비 착용
    SELECT_TARGET = "select_target"  # 대상 선택


class InventoryUI:
    """인벤토리 UI"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        inventory: Inventory,
        party: List[Any]
    ):
        """
        Args:
            screen_width: 화면 너비
            screen_height: 화면 높이
            inventory: 인벤토리
            party: 파티 멤버 리스트
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.inventory = inventory
        self.party = party

        self.mode = InventoryMode.BROWSE
        self.cursor = 0  # 아이템 커서
        self.scroll_offset = 0
        self.max_visible = 15  # 한 번에 표시할 아이템 수

        # 필터
        self.filter_type: Optional[ItemType] = None

        # 선택된 아이템/대상
        self.selected_item_index: Optional[int] = None
        self.target_cursor = 0

        # 정렬 메뉴
        self.sort_menu: Optional[CursorMenu] = None

        self.closed = False

    def handle_input(self, action: GameAction) -> bool:
        """
        입력 처리

        Args:
            action: 게임 액션

        Returns:
            닫기 여부
        """
        if self.mode == InventoryMode.BROWSE:
            return self._handle_browse(action)
        elif self.mode == InventoryMode.USE_ITEM or self.mode == InventoryMode.EQUIP:
            return self._handle_use_or_equip(action)
        elif self.mode == InventoryMode.SELECT_TARGET:
            return self._handle_target_select(action)

        return False

    def _handle_browse(self, action: GameAction) -> bool:
        """둘러보기 모드 입력"""
        if action == GameAction.MOVE_UP:
            self.cursor = max(0, self.cursor - 1)
            self._update_scroll()
        elif action == GameAction.MOVE_DOWN:
            self.cursor = min(len(self.inventory) - 1, self.cursor + 1)
            self._update_scroll()
        elif action == GameAction.CONFIRM:
            # 아이템 사용/장착
            if len(self.inventory) > 0:
                item = self.inventory.get_item(self.cursor)
                if item:
                    self.selected_item_index = self.cursor

                    if isinstance(item, Equipment):
                        self.mode = InventoryMode.EQUIP
                    elif isinstance(item, Consumable):
                        self.mode = InventoryMode.USE_ITEM
        elif action == GameAction.CANCEL or action == GameAction.ESCAPE:
            self.closed = True
            return True
        elif action == GameAction.MOVE_LEFT:
            # 필터 변경
            self._change_filter(-1)
        elif action == GameAction.MOVE_RIGHT:
            # 필터 변경
            self._change_filter(1)
        elif action == GameAction.MENU:
            # 정렬 메뉴
            self._open_sort_menu()

        return False

    def _handle_use_or_equip(self, action: GameAction) -> bool:
        """아이템 사용/장착 모드 입력"""
        if action == GameAction.MOVE_UP:
            self.target_cursor = max(0, self.target_cursor - 1)
        elif action == GameAction.MOVE_DOWN:
            self.target_cursor = min(len(self.party) - 1, self.target_cursor + 1)
        elif action == GameAction.CONFIRM:
            # 대상에게 사용/장착
            target = self.party[self.target_cursor]
            item = self.inventory.get_item(self.selected_item_index)

            if isinstance(item, Consumable):
                # 소비 아이템 사용
                success = self.inventory.use_consumable(self.selected_item_index, target)
                if success:
                    logger.info(f"{item.name} 사용 완료")
                    # 인덱스 조정
                    if self.cursor >= len(self.inventory):
                        self.cursor = max(0, len(self.inventory) - 1)
            elif isinstance(item, Equipment):
                # 장비 착용
                self._equip_item(target, item)

            # 모드 복귀
            self.mode = InventoryMode.BROWSE
            self.selected_item_index = None

        elif action == GameAction.CANCEL or action == GameAction.ESCAPE:
            # 취소
            self.mode = InventoryMode.BROWSE
            self.selected_item_index = None

        return False

    def _handle_target_select(self, action: GameAction) -> bool:
        """대상 선택 모드 입력"""
        # USE_ITEM과 동일
        return self._handle_use_or_equip(action)

    def _update_scroll(self):
        """스크롤 업데이트"""
        if self.cursor < self.scroll_offset:
            self.scroll_offset = self.cursor
        elif self.cursor >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.cursor - self.max_visible + 1

    def _change_filter(self, direction: int):
        """필터 변경"""
        filters = [None, ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY, ItemType.CONSUMABLE]

        if self.filter_type is None:
            current_idx = 0
        else:
            current_idx = filters.index(self.filter_type)

        new_idx = (current_idx + direction) % len(filters)
        self.filter_type = filters[new_idx]

        # 커서 초기화
        self.cursor = 0
        self.scroll_offset = 0

        logger.debug(f"필터 변경: {self.filter_type}")

    def _open_sort_menu(self):
        """정렬 메뉴 열기"""
        items = [
            MenuItem("등급순", "전설 → 일반", True, "rarity"),
            MenuItem("타입순", "무기 → 소비품", True, "type"),
            MenuItem("이름순", "가나다순", True, "name"),
        ]

        self.sort_menu = CursorMenu(
            title="정렬",
            items=items,
            x=30,
            y=15,
            width=25
        )

    def _equip_item(self, character: Any, item: Equipment):
        """장비 착용"""
        # 장비 슬롯 결정
        slot_name = item.equip_slot.value  # "weapon", "armor", "accessory"

        # 기존 장비 해제
        old_item = character.equipment.get(slot_name)
        if old_item:
            # 인벤토리에 되돌림
            self.inventory.add_item(old_item)
            logger.info(f"{character.name}: {old_item.name} 해제")

        # 새 장비 착용
        character.equip_item(slot_name, item)
        logger.info(f"{character.name}: {item.name} 착용")

        # 인벤토리에서 제거
        self.inventory.remove_item(self.selected_item_index)

    def render(self, console: tcod.console.Console):
        """인벤토리 화면 렌더링"""
        console.clear()

        # 제목
        title = "인벤토리"
        console.print(
            (self.screen_width - len(title)) // 2,
            1,
            title,
            fg=Colors.UI_TEXT_SELECTED
        )

        # 골드
        gold_text = f"골드: {self.inventory.gold}G"
        console.print(
            self.screen_width - len(gold_text) - 2,
            1,
            gold_text,
            fg=(255, 215, 0)
        )

        # 필터 표시
        filter_text = "전체"
        if self.filter_type == ItemType.WEAPON:
            filter_text = "무기"
        elif self.filter_type == ItemType.ARMOR:
            filter_text = "방어구"
        elif self.filter_type == ItemType.ACCESSORY:
            filter_text = "악세서리"
        elif self.filter_type == ItemType.CONSUMABLE:
            filter_text = "소비품"

        console.print(
            5,
            3,
            f"필터: {filter_text} (← →)",
            fg=Colors.GRAY
        )

        # 무게 정보
        current = self.inventory.current_weight
        maximum = self.inventory.max_weight
        weight_percent = (current / maximum * 100) if maximum > 0 else 0

        weight_color = Colors.UI_TEXT
        if weight_percent >= 90:
            weight_color = (255, 100, 100)  # 빨강 (거의 가득)
        elif weight_percent >= 70:
            weight_color = (255, 255, 100)  # 노랑 (많이 참)

        console.print(
            self.screen_width - 30,
            3,
            f"무게: {current}kg/{maximum}kg ({int(weight_percent)}%)",
            fg=weight_color
        )

        # 아이템 목록
        y = 5
        console.print(5, y, "─" * 70, fg=Colors.UI_BORDER)
        y += 1

        # 필터링
        visible_items = []
        for i, slot in enumerate(self.inventory.slots):
            if self.filter_type is None or slot.item.item_type == self.filter_type:
                visible_items.append((i, slot))

        # 스크롤된 아이템 표시
        for idx, (slot_idx, slot) in enumerate(visible_items[self.scroll_offset:self.scroll_offset + self.max_visible]):
            item = slot.item
            is_selected = (self.cursor == slot_idx and self.mode == InventoryMode.BROWSE)

            # 선택 표시
            prefix = "►" if is_selected else " "

            # 아이템 이름 (등급 색상)
            rarity_color = getattr(item.rarity, 'color', Colors.UI_TEXT)
            item_name = item.name

            # 수량 (소비품만)
            if isinstance(item, Consumable):
                item_name += f" x{slot.quantity}"

            # 레벨 요구사항
            if hasattr(item, 'level_requirement') and item.level_requirement > 1:
                item_name += f" (Lv.{item.level_requirement})"

            console.print(
                5,
                y,
                f"{prefix} {item_name}",
                fg=rarity_color if is_selected else Colors.UI_TEXT
            )

            y += 1

        # 스크롤 표시
        if len(visible_items) > self.max_visible:
            scroll_info = f"(↑↓: {self.scroll_offset + 1}-{min(self.scroll_offset + self.max_visible, len(visible_items))} / {len(visible_items)})"
            console.print(5, y, scroll_info, fg=Colors.DARK_GRAY)
            y += 1

        # 아이템 상세 정보
        y += 1
        if len(self.inventory) > 0:
            item = self.inventory.get_item(self.cursor)
            if item:
                self._render_item_details(console, item, 5, y)

        # 대상 선택 모드
        if self.mode in [InventoryMode.USE_ITEM, InventoryMode.EQUIP]:
            self._render_target_selection(console)

        # 도움말
        help_y = self.screen_height - 2
        if self.mode == InventoryMode.BROWSE:
            help_text = "Z: 사용/착용  X: 닫기  ←→: 필터  M: 정렬"
            console.print(2, help_y, help_text, fg=Colors.GRAY)
        else:
            help_text = "↑↓: 대상 선택  Z: 확인  X: 취소"
            console.print(2, help_y, help_text, fg=Colors.GRAY)

    def _render_item_details(self, console: tcod.console.Console, item: Item, x: int, y: int):
        """아이템 상세 정보 렌더링"""
        console.print(x, y, "─" * 70, fg=Colors.UI_BORDER)
        y += 1

        # 이름 + 등급
        rarity_name = getattr(item.rarity, 'display_name', '일반')
        console.print(
            x,
            y,
            f"{item.name} [{rarity_name}]",
            fg=getattr(item.rarity, 'color', Colors.UI_TEXT)
        )
        y += 1

        # 설명
        console.print(x, y, item.description, fg=Colors.GRAY)
        y += 1

        # 무게
        console.print(x, y, f"무게: {item.weight}kg", fg=Colors.DARK_GRAY)
        y += 1

        # 장비 정보
        if isinstance(item, Equipment):
            y += 1
            console.print(x, y, "기본 스탯:", fg=Colors.UI_TEXT)
            y += 1

            for stat_name, value in item.base_stats.items():
                if value != 0:
                    console.print(x + 2, y, f"{stat_name}: +{value}", fg=Colors.UI_TEXT)
                    y += 1

            # 접사
            if item.affixes:
                y += 1
                console.print(x, y, "추가 효과:", fg=Colors.UI_TEXT_SELECTED)
                y += 1

                for affix in item.affixes:
                    if affix.is_percentage:
                        console.print(x + 2, y, f"{affix.name} +{affix.value}%", fg=(150, 255, 150))
                    else:
                        console.print(x + 2, y, f"{affix.name} +{int(affix.value)}", fg=(150, 255, 150))
                    y += 1

            # 유니크 효과
            if hasattr(item, 'unique_effect') and item.unique_effect:
                y += 1
                console.print(x, y, f"유니크: {item.unique_effect}", fg=(255, 100, 255))

        # 소비품 정보
        elif isinstance(item, Consumable):
            y += 1
            effect_desc = {
                "heal_hp": f"HP {item.effect_value} 회복",
                "heal_mp": f"MP {item.effect_value} 회복",
                "heal_both": f"HP/MP {item.effect_value} 회복",
                "revive": f"HP {item.effect_value}로 부활",
                "cure_status": "모든 상태이상 치료"
            }

            desc = effect_desc.get(item.effect_type, "효과 불명")
            console.print(x, y, f"효과: {desc}", fg=Colors.UI_TEXT)

    def _render_target_selection(self, console: tcod.console.Console):
        """대상 선택 UI"""
        # 중앙에 대상 선택 창
        box_width = 40
        box_height = 10 + len(self.party)
        box_x = (self.screen_width - box_width) // 2
        box_y = (self.screen_height - box_height) // 2

        # 배경 박스
        console.draw_frame(
            box_x,
            box_y,
            box_width,
            box_height,
            "대상 선택",
            fg=Colors.UI_BORDER,
            bg=Colors.UI_BG
        )

        # 파티 멤버 목록
        y = box_y + 2
        for i, character in enumerate(self.party):
            is_selected = (i == self.target_cursor)
            prefix = "►" if is_selected else " "

            char_name = getattr(character, 'name', str(character))
            char_hp = getattr(character, 'current_hp', 0)
            char_max_hp = getattr(character, 'max_hp', 1)

            console.print(
                box_x + 2,
                y,
                f"{prefix} {char_name}",
                fg=Colors.UI_TEXT_SELECTED if is_selected else Colors.UI_TEXT
            )

            console.print(
                box_x + 20,
                y,
                f"HP {char_hp}/{char_max_hp}",
                fg=Colors.GRAY
            )

            y += 1


def open_inventory(
    console: tcod.console.Console,
    context: tcod.context.Context,
    inventory: Inventory,
    party: List[Any]
) -> None:
    """
    인벤토리 열기

    Args:
        console: TCOD 콘솔
        context: TCOD 컨텍스트
        inventory: 인벤토리
        party: 파티 멤버
    """
    ui = InventoryUI(console.width, console.height, inventory, party)
    handler = InputHandler()

    logger.info("인벤토리 열기")

    while not ui.closed:
        # 렌더링
        ui.render(console)
        context.present(console)

        # 입력 처리
        for event in tcod.event.wait():
            action = handler.dispatch(event)

            if action:
                if ui.handle_input(action):
                    return

            # 윈도우 닫기
            if isinstance(event, tcod.event.Quit):
                ui.closed = True
                return

    logger.info("인벤토리 닫기")
