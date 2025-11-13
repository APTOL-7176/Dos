"""
월드 탐험 UI

플레이어가 던전을 돌아다니는 화면
"""

from typing import List, Optional
import tcod

from src.world.exploration import ExplorationSystem, ExplorationEvent, ExplorationResult
from src.world.map_renderer import MapRenderer
from src.ui.input_handler import InputHandler, GameAction
from src.ui.gauge_renderer import GaugeRenderer
from src.core.logger import get_logger, Loggers


logger = get_logger(Loggers.UI)


class WorldUI:
    """월드 탐험 UI"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        exploration: ExplorationSystem
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.exploration = exploration
        self.map_renderer = MapRenderer(map_x=0, map_y=5)
        self.gauge_renderer = GaugeRenderer()

        # 메시지 로그
        self.messages: List[str] = []
        self.max_messages = 5

        # 상태
        self.quit_requested = False
        self.combat_requested = False
        self.floor_change_requested = None  # "up" or "down"

    def add_message(self, text: str):
        """메시지 추가"""
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        logger.debug(f"메시지: {text}")

    def handle_input(self, action: GameAction) -> bool:
        """
        입력 처리

        Returns:
            True면 종료
        """
        if action == GameAction.QUIT or action == GameAction.ESCAPE:
            self.quit_requested = True
            return True

        # 이동
        dx, dy = 0, 0

        if action == GameAction.MOVE_UP:
            dy = -1
        elif action == GameAction.MOVE_DOWN:
            dy = 1
        elif action == GameAction.MOVE_LEFT:
            dx = -1
        elif action == GameAction.MOVE_RIGHT:
            dx = 1

        if dx != 0 or dy != 0:
            result = self.exploration.move_player(dx, dy)
            self._handle_exploration_result(result)

        # 계단 이동
        elif action == GameAction.CONFIRM:
            tile = self.exploration.dungeon.get_tile(
                self.exploration.player.x,
                self.exploration.player.y
            )

            if tile:
                from src.world.tile import TileType
                if tile.tile_type == TileType.STAIRS_DOWN:
                    self.floor_change_requested = "down"
                    self.add_message("아래층으로 내려갑니다...")
                    return True
                elif tile.tile_type == TileType.STAIRS_UP:
                    self.floor_change_requested = "up"
                    self.add_message("위층으로 올라갑니다...")
                    return True

        return False

    def _handle_exploration_result(self, result: ExplorationResult):
        """탐험 결과 처리"""
        if result.message:
            self.add_message(result.message)

        if result.event == ExplorationEvent.COMBAT:
            self.combat_requested = True

        elif result.event == ExplorationEvent.TRAP_TRIGGERED:
            # 함정 데미지는 이미 적용됨
            pass

        elif result.event == ExplorationEvent.HEAL:
            # 회복은 이미 적용됨
            pass

        elif result.event == ExplorationEvent.TELEPORT:
            self.add_message(f"위치: ({self.exploration.player.x}, {self.exploration.player.y})")

    def render(self, console: tcod.console.Console):
        """렌더링"""
        console.clear()

        # 제목
        console.print(
            self.screen_width // 2 - 15,
            1,
            f"던전 탐험 - {self.exploration.floor_number}층",
            fg=(255, 255, 100)
        )

        # 맵 렌더링 (플레이어 중심)
        player = self.exploration.player
        self.map_renderer.render(
            console,
            self.exploration.dungeon,
            camera_x=max(0, player.x - 40),
            camera_y=max(0, player.y - 20),
            view_width=self.screen_width,
            view_height=35
        )

        # 플레이어 위치 표시
        screen_x = player.x - max(0, player.x - 40)
        screen_y = 5 + (player.y - max(0, player.y - 20))
        if 0 <= screen_x < self.screen_width and 0 <= screen_y < 40:
            console.print(screen_x, screen_y, "@", fg=(255, 255, 100))

        # 파티 상태 (우측 상단)
        self._render_party_status(console)

        # 메시지 로그 (하단)
        self._render_messages(console)

        # 미니맵 (우측 하단)
        self.map_renderer.render_minimap(
            console,
            self.exploration.dungeon,
            minimap_x=self.screen_width - 22,
            minimap_y=self.screen_height - 17
        )

        # 조작법 (하단)
        console.print(
            5,
            self.screen_height - 2,
            "방향키: 이동  Z: 계단 이용  ESC: 종료",
            fg=(180, 180, 180)
        )

    def _render_party_status(self, console: tcod.console.Console):
        """파티 상태 렌더링 (간단)"""
        x = self.screen_width - 30
        y = 3

        console.print(x, y, "[파티 상태]", fg=(100, 255, 100))

        for i, member in enumerate(self.exploration.player.party[:4]):
            my = y + 2 + i * 3

            # 이름
            console.print(x, my, f"{i+1}. {member.name[:10]}", fg=(255, 255, 255))

            # HP 게이지 (작게)
            hp_bar, hp_color = self.gauge_renderer.render_bar(
                member.current_hp, member.max_hp, width=10, show_numbers=False
            )
            console.print(x + 3, my + 1, f"HP:{hp_bar}", fg=hp_color)

        # 인벤토리 정보
        inv_y = y + 15
        console.print(x, inv_y, "[소지품]", fg=(200, 200, 255))
        console.print(x + 2, inv_y + 1, f"열쇠: {len(self.exploration.player.keys)}개", fg=(255, 215, 0))
        console.print(x + 2, inv_y + 2, f"아이템: {len(self.exploration.player.inventory)}개", fg=(200, 200, 200))

    def _render_messages(self, console: tcod.console.Console):
        """메시지 로그"""
        msg_y = 40
        console.print(0, msg_y, "─" * self.screen_width, fg=(100, 100, 100))

        for i, msg in enumerate(self.messages[-self.max_messages:]):
            console.print(2, msg_y + 1 + i, msg, fg=(200, 200, 200))


def run_exploration(
    console: tcod.console.Console,
    context: tcod.context.Context,
    exploration: ExplorationSystem
) -> str:
    """
    탐험 실행

    Returns:
        "quit", "combat", "floor_up", "floor_down"
    """
    ui = WorldUI(console.width, console.height, exploration)
    handler = InputHandler()

    logger.info(f"탐험 시작: {exploration.floor_number}층")

    while True:
        # 렌더링
        ui.render(console)
        context.present(console)

        # 입력 처리
        for event in tcod.event.wait():
            action = handler.dispatch(event)

            if action:
                done = ui.handle_input(action)
                if done:
                    break

            # 윈도우 닫기
            if isinstance(event, tcod.event.Quit):
                return "quit"

        # 상태 체크
        if ui.quit_requested:
            return "quit"
        elif ui.combat_requested:
            return "combat"
        elif ui.floor_change_requested:
            return ui.floor_change_requested
