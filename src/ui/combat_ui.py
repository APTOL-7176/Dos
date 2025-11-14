"""
전투 UI

6가지 전투 메뉴 (BRV 공격, HP 공격, 스킬, 아이템, 방어, 도망)와
전투 상태 표시
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import tcod
import random

from src.ui.input_handler import InputHandler, GameAction
from src.ui.cursor_menu import CursorMenu, MenuItem
from src.ui.gauge_renderer import GaugeRenderer
from src.combat.combat_manager import CombatManager, CombatState, ActionType
from src.combat.casting_system import get_casting_system, CastingSystem
from src.core.logger import get_logger, Loggers
from src.audio import play_sfx, play_bgm


logger = get_logger(Loggers.UI)
gauge_renderer = GaugeRenderer()
casting_system = get_casting_system()


class CombatUIState(Enum):
    """전투 UI 상태"""
    WAITING_ATB = "waiting_atb"  # ATB 대기 중
    ACTION_MENU = "action_menu"  # 행동 선택
    SKILL_MENU = "skill_menu"  # 스킬 선택
    TARGET_SELECT = "target_select"  # 대상 선택
    ITEM_MENU = "item_menu"  # 아이템 선택
    EXECUTING = "executing"  # 행동 실행 중
    BATTLE_END = "battle_end"  # 전투 종료


@dataclass
class CombatMessage:
    """전투 메시지"""
    text: str
    color: Tuple[int, int, int] = (255, 255, 255)
    frames_remaining: int = 180  # 3초 (60 FPS 기준)


class CombatUI:
    """전투 UI"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        combat_manager: CombatManager
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.combat_manager = combat_manager

        # UI 상태
        self.state = CombatUIState.WAITING_ATB
        self.current_actor: Optional[Any] = None
        self.selected_action: Optional[ActionType] = None
        self.selected_skill: Optional[Any] = None
        self.selected_target: Optional[Any] = None

        # 메시지 로그
        self.messages: List[CombatMessage] = []
        self.max_messages = 5

        # 메뉴
        self.action_menu: Optional[CursorMenu] = None
        self.skill_menu: Optional[CursorMenu] = None
        self.target_cursor = 0

        # 전투 종료 플래그
        self.battle_ended = False
        self.battle_result: Optional[CombatState] = None

        logger.info("전투 UI 초기화")

    def _create_action_menu(self) -> CursorMenu:
        """행동 메뉴 생성"""
        items = [
            MenuItem("BRV 공격", description="BRV를 축적하여 적의 BRV를 파괴", enabled=True, value=ActionType.BRV_ATTACK),
            MenuItem("HP 공격", description="축적한 BRV로 적의 HP에 직접 데미지", enabled=True, value=ActionType.HP_ATTACK),
            MenuItem("스킬", description="특수 기술 사용", enabled=True, value=ActionType.SKILL),
            MenuItem("아이템", description="아이템 사용", enabled=True, value=ActionType.ITEM),
            MenuItem("방어", description="방어 자세로 피해 감소", enabled=True, value=ActionType.DEFEND),
            MenuItem("도망", description="전투에서 도망", enabled=True, value=ActionType.FLEE),
        ]

        return CursorMenu(
            title="행동 선택",
            items=items,
            x=5,
            y=35,
            width=30,
            show_description=True
        )

    def _create_skill_menu(self, actor: Any) -> CursorMenu:
        """스킬 메뉴 생성"""
        skills = getattr(actor, 'skills', [])
        items = []

        for skill in skills:
            # MP 체크
            mp_cost = getattr(skill, 'mp_cost', 0)
            can_use = actor.current_mp >= mp_cost

            name = getattr(skill, 'name', str(skill))
            desc = getattr(skill, 'description', '')
            mp_text = f" (MP: {mp_cost})" if mp_cost > 0 else ""

            items.append(MenuItem(
                text=f"{name}{mp_text}",
                description=desc,
                enabled=can_use,
                value=skill
            ))

        # 뒤로가기
        items.append(MenuItem("← 뒤로", "행동 메뉴로 돌아가기", True, None))

        return CursorMenu(
            title=f"{actor.name}의 스킬",
            items=items,
            x=5,
            y=30,
            width=40,
            show_description=True
        )

    def handle_input(self, action: GameAction) -> bool:
        """
        입력 처리

        Returns:
            True면 전투 종료
        """
        if self.state == CombatUIState.BATTLE_END:
            return True

        # 행동 메뉴
        if self.state == CombatUIState.ACTION_MENU:
            return self._handle_action_menu(action)

        # 스킬 메뉴
        elif self.state == CombatUIState.SKILL_MENU:
            return self._handle_skill_menu(action)

        # 대상 선택
        elif self.state == CombatUIState.TARGET_SELECT:
            return self._handle_target_select(action)

        # 아이템 메뉴
        elif self.state == CombatUIState.ITEM_MENU:
            return self._handle_item_menu(action)

        return False

    def _handle_action_menu(self, action: GameAction) -> bool:
        """행동 메뉴 입력 처리"""
        if not self.action_menu:
            return False

        if action == GameAction.MOVE_UP:
            self.action_menu.move_cursor_up()
        elif action == GameAction.MOVE_DOWN:
            self.action_menu.move_cursor_down()
        elif action == GameAction.CONFIRM:
            selected_item = self.action_menu.get_selected_item()
            if selected_item:
                self.selected_action = selected_item.value
                self._on_action_selected()
        elif action == GameAction.CANCEL:
            # 취소 불가 (턴은 넘어가야 함)
            pass

        return False

    def _handle_skill_menu(self, action: GameAction) -> bool:
        """스킬 메뉴 입력 처리"""
        if not self.skill_menu:
            return False

        if action == GameAction.MOVE_UP:
            self.skill_menu.move_cursor_up()
        elif action == GameAction.MOVE_DOWN:
            self.skill_menu.move_cursor_down()
        elif action == GameAction.CONFIRM:
            selected_item = self.skill_menu.get_selected_item()
            if selected_item:
                if selected_item.value is None:  # 뒤로가기
                    self.state = CombatUIState.ACTION_MENU
                else:
                    self.selected_skill = selected_item.value
                    self._start_target_selection()
        elif action == GameAction.CANCEL:
            self.state = CombatUIState.ACTION_MENU

        return False

    def _handle_target_select(self, action: GameAction) -> bool:
        """대상 선택 입력 처리"""
        enemies = [e for e in self.combat_manager.enemies if e.is_alive]

        if not enemies:
            return False

        if action == GameAction.MOVE_UP:
            self.target_cursor = (self.target_cursor - 1) % len(enemies)
        elif action == GameAction.MOVE_DOWN:
            self.target_cursor = (self.target_cursor + 1) % len(enemies)
        elif action == GameAction.MOVE_LEFT:
            self.target_cursor = (self.target_cursor - 1) % len(enemies)
        elif action == GameAction.MOVE_RIGHT:
            self.target_cursor = (self.target_cursor + 1) % len(enemies)
        elif action == GameAction.CONFIRM:
            self.selected_target = enemies[self.target_cursor]
            self._execute_current_action()
        elif action == GameAction.CANCEL:
            # 취소 - 이전 상태로
            if self.selected_action == ActionType.SKILL:
                self.state = CombatUIState.SKILL_MENU
            else:
                self.state = CombatUIState.ACTION_MENU
            self.selected_skill = None

        return False

    def _handle_item_menu(self, action: GameAction) -> bool:
        """아이템 메뉴 입력 처리 (TODO)"""
        if action == GameAction.CANCEL:
            self.state = CombatUIState.ACTION_MENU
        elif action == GameAction.CONFIRM:
            # TODO: 아이템 구현
            self.add_message("아이템은 아직 구현되지 않았습니다", (255, 200, 100))
            self.state = CombatUIState.ACTION_MENU

        return False

    def _on_action_selected(self):
        """행동 선택 후 처리"""
        if self.selected_action == ActionType.SKILL:
            # 스킬 메뉴 열기
            self.skill_menu = self._create_skill_menu(self.current_actor)
            self.state = CombatUIState.SKILL_MENU

        elif self.selected_action == ActionType.ITEM:
            # 아이템 메뉴 열기
            self.state = CombatUIState.ITEM_MENU

        elif self.selected_action == ActionType.DEFEND:
            # 방어는 대상 선택 불필요
            self._execute_current_action()

        elif self.selected_action == ActionType.FLEE:
            # 도망도 대상 선택 불필요
            self._execute_current_action()

        else:
            # BRV/HP 공격 - 대상 선택
            self._start_target_selection()

    def _start_target_selection(self):
        """대상 선택 시작"""
        self.target_cursor = 0
        self.state = CombatUIState.TARGET_SELECT

    def _execute_current_action(self):
        """현재 선택된 행동 실행"""
        self.state = CombatUIState.EXECUTING

        result = self.combat_manager.execute_action(
            actor=self.current_actor,
            action_type=self.selected_action,
            target=self.selected_target,
            skill=self.selected_skill
        )

        # 결과 메시지 표시
        self._show_action_result(result)

        # 상태 초기화
        self.current_actor = None
        self.selected_action = None
        self.selected_skill = None
        self.selected_target = None
        self.state = CombatUIState.WAITING_ATB

        # 전투 종료 확인
        if self.combat_manager.state in [CombatState.VICTORY, CombatState.DEFEAT, CombatState.FLED]:
            self.battle_ended = True
            self.battle_result = self.combat_manager.state
            self.state = CombatUIState.BATTLE_END

            # 전투 종료 BGM 재생
            if self.combat_manager.state == CombatState.VICTORY:
                play_bgm("victory")
            elif self.combat_manager.state == CombatState.DEFEAT:
                play_bgm("defeat")

    def _show_action_result(self, result: Dict[str, Any]):
        """행동 결과 메시지 표시"""
        action = result.get("action", "unknown")

        if action == "brv_attack":
            damage = result.get("damage", 0)
            is_crit = result.get("is_critical", False)
            is_break = result.get("is_break", False)

            msg = f"BRV 공격! {damage} 데미지"
            if is_crit:
                msg += " [크리티컬!]"
            if is_break:
                msg += " [BREAK!]"

            color = (255, 255, 100) if is_crit else (200, 200, 200)
            self.add_message(msg, color)

        elif action == "hp_attack":
            damage = result.get("hp_damage", 0)
            is_ko = result.get("is_ko", False)

            msg = f"HP 공격! {damage} HP 데미지"
            if is_ko:
                msg += " [격파!]"

            color = (255, 100, 100)
            self.add_message(msg, color)

        elif action == "defend":
            self.add_message("방어 자세!", (100, 200, 255))

        elif action == "flee":
            success = result.get("success", False)
            if success:
                self.add_message("도망쳤다!", (255, 255, 100))
            else:
                self.add_message("도망칠 수 없다!", (255, 100, 100))

    def update(self, delta_time: float = 1.0):
        """업데이트 (매 프레임)"""
        # 플레이어가 선택 중인지 확인
        is_player_selecting = self.state in [
            CombatUIState.ACTION_MENU,
            CombatUIState.SKILL_MENU,
            CombatUIState.TARGET_SELECT,
            CombatUIState.ITEM_MENU
        ]

        # 플레이어가 선택 중일 때는 ATB 증가를 멈춤
        if is_player_selecting:
            # ATB 업데이트 스킵 (시간 정지)
            # 플레이어 턴으로 표시하여 ATB 증가 방지
            self.combat_manager.state = CombatState.PLAYER_TURN
        else:
            # 일반 진행
            if self.combat_manager.state == CombatState.PLAYER_TURN:
                self.combat_manager.state = CombatState.IN_PROGRESS

        # 전투 매니저 업데이트
        self.combat_manager.update(delta_time)

        # 전투 종료 확인
        if self.combat_manager.state in [CombatState.VICTORY, CombatState.DEFEAT, CombatState.FLED]:
            if not self.battle_ended:
                self.battle_ended = True
                self.battle_result = self.combat_manager.state
                self.state = CombatUIState.BATTLE_END
                logger.info(f"전투 종료 감지: {self.battle_result.value}")

        # 메시지 타이머 감소
        for msg in self.messages:
            msg.frames_remaining -= 1

        # 만료된 메시지 제거
        self.messages = [m for m in self.messages if m.frames_remaining > 0]

        # ATB 대기 중 - 턴 체크
        if self.state == CombatUIState.WAITING_ATB:
            self._check_ready_combatants()

    def _check_ready_combatants(self):
        """행동 가능한 전투원 확인"""
        ready = self.combat_manager.atb.get_action_order()

        if not ready:
            return

        # 아군 턴
        for combatant in ready:
            if combatant in self.combat_manager.allies:
                # 아군 턴 시작 SFX
                play_sfx("combat", "turn_start")

                self.current_actor = combatant
                self.action_menu = self._create_action_menu()
                self.state = CombatUIState.ACTION_MENU
                self.add_message(f"{combatant.name}의 턴!", (100, 255, 255))
                return

        # 적군 턴 (AI)
        for combatant in ready:
            if combatant in self.combat_manager.enemies:
                self._execute_enemy_turn(combatant)
                return

    def _execute_enemy_turn(self, enemy: Any):
        """적 턴 실행 (간단한 AI)"""
        # 간단한 AI: 랜덤 대상에게 BRV 공격 또는 HP 공격
        import random

        allies_alive = [a for a in self.combat_manager.allies if a.is_alive]
        if not allies_alive:
            return

        target = random.choice(allies_alive)

        # BRV가 충분하면 HP 공격, 아니면 BRV 공격
        if enemy.current_brv > 500:
            action = ActionType.HP_ATTACK
        else:
            action = ActionType.BRV_ATTACK

        self.add_message(f"{enemy.name}의 공격!", (255, 150, 150))

        result = self.combat_manager.execute_action(
            actor=enemy,
            action_type=action,
            target=target
        )

        self._show_action_result(result)

        # 전투 종료 확인
        if self.combat_manager.state in [CombatState.VICTORY, CombatState.DEFEAT]:
            self.battle_ended = True
            self.battle_result = self.combat_manager.state
            self.state = CombatUIState.BATTLE_END

    def add_message(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)):
        """메시지 추가"""
        msg = CombatMessage(text=text, color=color)
        self.messages.append(msg)

        # 최대 개수 초과 시 오래된 것 제거
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

        logger.debug(f"전투 메시지: {text}")

    def render(self, console: tcod.console.Console):
        """렌더링"""
        console.clear()

        # 제목
        console.print(
            self.screen_width // 2 - 5,
            1,
            "⚔ 전투 ⚔",
            fg=(255, 255, 100)
        )

        # 아군 상태
        self._render_allies(console)

        # 적군 상태
        self._render_enemies(console)

        # 메시지 로그
        self._render_messages(console)

        # 상태별 UI
        if self.state == CombatUIState.ACTION_MENU and self.action_menu:
            self.action_menu.render(console)

        elif self.state == CombatUIState.SKILL_MENU and self.skill_menu:
            self.skill_menu.render(console)

        elif self.state == CombatUIState.TARGET_SELECT:
            self._render_target_select(console)

        elif self.state == CombatUIState.ITEM_MENU:
            self._render_item_menu(console)

        elif self.state == CombatUIState.BATTLE_END:
            self._render_battle_end(console)

    def _render_allies(self, console: tcod.console.Console):
        """아군 상태 렌더링 (상세)"""
        console.print(5, 4, "[아군 파티]", fg=(100, 255, 100))

        for i, ally in enumerate(self.combat_manager.allies):
            y = 6 + i * 6  # 더 큰 간격

            # 이름 + 상태
            name_color = (255, 255, 255) if ally.is_alive else (100, 100, 100)
            console.print(5, y, f"{i+1}. {ally.name}", fg=name_color)

            # 상태이상 아이콘
            status_effects = getattr(ally, 'status_effects', {})
            if status_effects:
                status_text = gauge_renderer.render_status_icons(status_effects)
                console.print(5 + len(ally.name) + 4, y, status_text, fg=(200, 200, 255))

            # HP 게이지 (정밀)
            console.print(8, y + 1, "HP:", fg=(200, 200, 200))
            gauge_renderer.render_bar(
                console, 12, y + 1, 15,
                ally.current_hp, ally.max_hp, show_numbers=True
            )

            # MP 게이지 (파란색)
            console.print(33, y + 2, "MP:", fg=(200, 200, 200))
            # MP 게이지: 파란색 계열
            mp_ratio = ally.current_mp / max(1, ally.max_mp)
            if mp_ratio > 0.6:
                mp_fg = (100, 150, 255)  # 밝은 파랑
                mp_bg = (50, 75, 150)
            elif mp_ratio > 0.3:
                mp_fg = (80, 120, 200)  # 중간 파랑
                mp_bg = (40, 60, 100)
            else:
                mp_fg = (60, 90, 150)  # 어두운 파랑
                mp_bg = (30, 45, 75)
            console.draw_rect(37, y + 2, 10, 1, ord(" "), bg=mp_bg)
            filled_mp = int(mp_ratio * 10)
            if filled_mp > 0:
                console.draw_rect(37, y + 2, filled_mp, 1, ord(" "), bg=mp_fg)
            mp_text = f"{ally.current_mp}/{ally.max_mp}"
            console.print(37 + (10 - len(mp_text)) // 2, y + 2, mp_text, fg=(255, 255, 255))

            # BRV 게이지 (노란색)
            max_brv = getattr(ally, 'max_brv', 999)
            console.print(8, y + 2, "BRV:", fg=(200, 200, 200))
            # BRV 게이지: 노란색 계열
            brv_ratio = ally.current_brv / max(1, max_brv)
            if brv_ratio > 0.8:
                brv_fg = (255, 220, 100)  # 황금색
                brv_bg = (150, 130, 50)
            elif brv_ratio > 0.5:
                brv_fg = (255, 200, 80)  # 밝은 노랑
                brv_bg = (120, 100, 40)
            elif brv_ratio > 0.2:
                brv_fg = (200, 160, 60)  # 중간 노랑
                brv_bg = (100, 80, 30)
            else:
                brv_fg = (150, 120, 40)  # 어두운 노랑
                brv_bg = (75, 60, 20)
            console.draw_rect(13, y + 2, 10, 1, ord(" "), bg=brv_bg)
            filled_brv = int(brv_ratio * 10)
            if filled_brv > 0:
                console.draw_rect(13, y + 2, filled_brv, 1, ord(" "), bg=brv_fg)
            brv_text = f"{int(ally.current_brv)}/{int(max_brv)}"
            console.print(13 + (10 - len(brv_text)) // 2, y + 2, brv_text, fg=(255, 255, 255))

            # ATB 게이지 (더 정밀)
            gauge = self.combat_manager.atb.get_gauge(ally)
            atb_value = gauge.current if gauge else 0
            console.print(33, y + 1, "ATB:", fg=(200, 200, 200))
            gauge_renderer.render_percentage_bar(
                console, 38, y + 1, 15,
                atb_value / 1000.0, show_percent=False, custom_color=(200, 200, 255)
            )

            # 상처 표시
            wound_damage = getattr(ally, 'wound_damage', 0)
            if wound_damage > 0:
                gauge_renderer.render_wound_indicator(console, 33, y + 2, wound_damage)

            # 캐스팅 표시
            cast_info = casting_system.get_cast_info(ally)
            if cast_info:
                skill_name = getattr(cast_info.skill, 'name', 'Unknown')
                gauge_renderer.render_casting_bar(
                    console, 8, y + 4, 20,
                    cast_info.progress, skill_name=f"시전:{skill_name}"
                )

    def _render_enemies(self, console: tcod.console.Console):
        """적군 상태 렌더링 (상세)"""
        console.print(self.screen_width - 30, 4, "[적군]", fg=(255, 100, 100))

        for i, enemy in enumerate(self.combat_manager.enemies):
            y = 6 + i * 6
            x = self.screen_width - 30

            # 이름
            name_color = (255, 255, 255) if enemy.is_alive else (100, 100, 100)

            # 대상 선택 커서
            cursor = "▶ " if (
                self.state == CombatUIState.TARGET_SELECT and
                i == self.target_cursor
            ) else "  "

            console.print(x, y, f"{cursor}{chr(65+i)}. {enemy.name}", fg=name_color)

            # 상태이상
            status_effects = getattr(enemy, 'status_effects', {})
            if status_effects:
                status_text = gauge_renderer.render_status_icons(status_effects)
                console.print(x, y + 1, status_text, fg=(200, 200, 255))

            # HP 게이지
            console.print(x + 3, y + 2, "HP:", fg=(200, 200, 200))
            gauge_renderer.render_bar(
                console, x + 7, y + 2, 12,
                enemy.current_hp, enemy.max_hp, show_numbers=True
            )

            # BRV 게이지
            max_brv = getattr(enemy, 'max_brv', 9999)
            console.print(x + 3, y + 3, "BRV:", fg=(200, 200, 200))
            gauge_renderer.render_bar(
                console, x + 8, y + 3, 10,
                enemy.current_brv, max_brv, show_numbers=True, color_gradient=False
            )

            # BREAK 상태 표시
            if self.combat_manager.brave.is_broken(enemy):
                console.print(x + 3, y + 4, "💔 BREAK!", fg=(255, 50, 50))

            # 캐스팅 표시
            cast_info = casting_system.get_cast_info(enemy)
            if cast_info:
                skill_name = getattr(cast_info.skill, 'name', 'Unknown')
                gauge_renderer.render_casting_bar(
                    console, x + 3, y + 5, 15,
                    cast_info.progress, skill_name=f"시전:{skill_name[:8]}"
                )

    def _render_messages(self, console: tcod.console.Console):
        """메시지 로그 렌더링"""
        msg_y = 28
        console.print(5, msg_y, "─" * (self.screen_width - 10), fg=(100, 100, 100))

        for i, msg in enumerate(self.messages[-self.max_messages:]):
            console.print(5, msg_y + 1 + i, msg.text, fg=msg.color)

    def _render_target_select(self, console: tcod.console.Console):
        """대상 선택 UI 렌더링"""
        console.print(
            self.screen_width // 2 - 10,
            35,
            "대상을 선택하세요 (↑↓ 또는 ←→)",
            fg=(255, 255, 100)
        )

        console.print(
            self.screen_width // 2 - 8,
            36,
            "Z: 확정  X: 취소",
            fg=(180, 180, 180)
        )

    def _render_item_menu(self, console: tcod.console.Console):
        """아이템 메뉴 렌더링 (TODO)"""
        console.print(
            self.screen_width // 2 - 10,
            35,
            "아이템 (구현 예정)",
            fg=(255, 255, 100)
        )

        console.print(
            self.screen_width // 2 - 8,
            36,
            "X: 취소",
            fg=(180, 180, 180)
        )

    def _render_battle_end(self, console: tcod.console.Console):
        """전투 종료 화면 렌더링"""
        if self.battle_result == CombatState.VICTORY:
            msg = "승리!"
            color = (255, 255, 100)
        elif self.battle_result == CombatState.DEFEAT:
            msg = "패배..."
            color = (255, 100, 100)
        else:
            msg = "도망쳤다"
            color = (200, 200, 200)

        console.print(
            self.screen_width // 2 - len(msg) // 2,
            self.screen_height // 2,
            msg,
            fg=color
        )

        console.print(
            self.screen_width // 2 - 10,
            self.screen_height // 2 + 2,
            "아무 키나 눌러 계속...",
            fg=(180, 180, 180)
        )


def run_combat(
    console: tcod.console.Console,
    context: tcod.context.Context,
    party: List[Any],
    enemies: List[Any]
) -> CombatState:
    """
    전투 실행

    Args:
        console: TCOD 콘솔
        context: TCOD 컨텍스트
        party: 아군 파티
        enemies: 적군 리스트

    Returns:
        전투 결과 (승리/패배/도주)
    """
    # 전투 시작 SFX (Battle Swirl)
    play_sfx("combat", "battle_start")

    # 적 타입에 따라 BGM 선택
    # 1. 세피로스 확인
    is_sephiroth = any(hasattr(e, 'enemy_id') and e.enemy_id == "sephiroth" for e in enemies)
    # 2. 보스 확인 (enemy_id가 "boss_"로 시작)
    is_boss = any(hasattr(e, 'enemy_id') and e.enemy_id.startswith("boss_") for e in enemies)

    if is_sephiroth:
        # 세피로스전: One-Winged Angel 고정
        selected_bgm = "battle_final_boss"
    elif is_boss:
        # 보스전: 2개 중 랜덤
        boss_bgm_tracks = ["battle_jenova", "battle_birth_of_god"]
        selected_bgm = random.choice(boss_bgm_tracks)
    else:
        # 일반 전투: 3개 중 랜덤
        battle_bgm_tracks = [
            "battle_boss",              # 21-Still More Fighting
            "battle_jenova_absolute",   # 85-Jenova Absolute
            "battle_normal"             # 11-Fighting
        ]
        selected_bgm = random.choice(battle_bgm_tracks)

    play_bgm(selected_bgm, loop=True, fade_in=True)

    # 전투 매니저 생성
    combat_manager = CombatManager()
    combat_manager.start_combat(party, enemies)

    # 전투 UI 생성
    ui = CombatUI(console.width, console.height, combat_manager)
    handler = InputHandler()

    logger.info(f"전투 시작: 아군 {len(party)}명 vs 적군 {len(enemies)}명 (BGM: {selected_bgm})")

    # 전투 루프
    while not ui.battle_ended:
        # 업데이트
        ui.update(delta_time=1.0)

        # 렌더링
        ui.render(console)
        context.present(console)

        # 입력 처리
        for event in tcod.event.wait(timeout=0.016):  # ~60 FPS
            action = handler.dispatch(event)

            if action:
                if ui.handle_input(action):
                    break

            # 윈도우 닫기
            if isinstance(event, tcod.event.Quit):
                return CombatState.FLED

    logger.info(f"전투 종료: {ui.battle_result.value if ui.battle_result else 'unknown'}")
    return ui.battle_result or CombatState.FLED
