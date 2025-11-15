#!/usr/bin/env python3
"""
Dawn of Stellar 게임 런처 (GUI)

TCOD 기반 그래픽 런처
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

import tcod
import tcod.event

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.cursor_menu import CursorMenu, MenuItem
from src.ui.tcod_display import Colors
from src.audio import initialize_audio, play_bgm, play_sfx


class LauncherState:
    """런처 상태"""
    MAIN_MENU = "main_menu"
    SAVE_MANAGER = "save_manager"
    LOG_VIEWER = "log_viewer"
    SETTINGS = "settings"
    GAME_INFO = "game_info"
    SYSTEM_CHECK = "system_check"
    RUNNING_GAME = "running_game"
    EXIT = "exit"


class GameLauncher:
    """게임 런처 GUI"""

    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.saves_dir = self.root_dir / "saves"
        self.logs_dir = self.root_dir / "logs"
        self.config_file = self.root_dir / "config.yaml"
        self.main_script = self.root_dir / "main.py"

        # 디렉토리 생성
        self.saves_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # 화면 설정
        self.screen_width = 100
        self.screen_height = 50
        self.title = "Dawn of Stellar - Game Launcher"

        # 폰트 로드
        font_path = self.root_dir / "D2Coding.ttc"
        if not font_path.exists():
            font_path = None

        # TCOD 초기화
        if font_path and font_path.exists():
            tcod.console.set_custom_font(
                str(font_path),
                tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
                nb_char_horizontal=32,
                nb_char_vertical=64
            )

        self.context = tcod.context.new(
            width=self.screen_width,
            height=self.screen_height,
            title=self.title,
            vsync=True,
            sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE
        )

        self.console = tcod.console.Console(self.screen_width, self.screen_height, order="F")

        # 상태
        self.state = LauncherState.MAIN_MENU
        self.running = True
        self.message = ""
        self.message_color = Colors.WHITE
        self.message_timer = 0

        # 메뉴
        self.current_menu: Optional[CursorMenu] = None
        self.submenu_data: Optional[List] = None

        # 오디오 초기화
        try:
            initialize_audio()
            play_bgm("menu", loop=True)
        except Exception:
            pass

    def show_message(self, text: str, color: Tuple[int, int, int] = Colors.WHITE, duration: int = 180):
        """메시지 표시"""
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def create_main_menu(self) -> CursorMenu:
        """메인 메뉴 생성"""
        items = [
            MenuItem("🎮 게임 시작", value="game_normal", description="일반 모드로 게임을 시작합니다"),
            MenuItem("🔧 개발 모드", value="game_dev", description="모든 직업 잠금 해제"),
            MenuItem("🐛 디버그 모드", value="game_debug", description="상세 로그 출력 모드"),
            MenuItem("💾 세이브 관리", value="save_manager", description="세이브 파일 백업/삭제/확인"),
            MenuItem("📋 로그 확인", value="log_viewer", description="게임 로그 파일 확인"),
            MenuItem("⚙️  설정", value="settings", description="게임 설정 확인"),
            MenuItem("ℹ️  게임 정보", value="game_info", description="게임 정보 및 버전 확인"),
            MenuItem("🔍 시스템 체크", value="system_check", description="시스템 요구사항 확인"),
            MenuItem("🚪 종료", value="exit", description="런처 종료"),
        ]

        return CursorMenu(
            title="Dawn of Stellar - 별빛의 여명",
            items=items,
            x=25,
            y=10,
            width=50,
            show_description=True
        )

    def create_save_menu(self) -> CursorMenu:
        """세이브 관리 메뉴 생성"""
        save_files = sorted(self.saves_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
        self.submenu_data = list(save_files)

        items = []

        if not save_files:
            items.append(MenuItem("세이브 파일이 없습니다", enabled=False))
        else:
            for i, save_file in enumerate(save_files[:15]):  # 최대 15개
                size = save_file.stat().st_size
                mtime = datetime.fromtimestamp(save_file.stat().st_mtime)

                # 세이브 정보 미리보기
                preview = ""
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'floor' in data:
                            preview = f" [{data['floor']}층]"
                except Exception:
                    pass

                desc = f"크기: {size:,} bytes | {mtime.strftime('%Y-%m-%d %H:%M:%S')}{preview}"
                items.append(MenuItem(save_file.name, value=i, description=desc))

        items.append(MenuItem("", enabled=False))  # 구분선
        items.append(MenuItem("💾 모든 세이브 백업", value="backup_all", description="모든 세이브 파일 백업"))
        items.append(MenuItem("🗑️  선택 파일 삭제", value="delete_selected", description="선택한 세이브 삭제"))
        items.append(MenuItem("← 뒤로 가기", value="back", description="메인 메뉴로 돌아가기"))

        return CursorMenu(
            title="세이브 파일 관리",
            items=items,
            x=10,
            y=5,
            width=80,
            show_description=True
        )

    def create_log_menu(self) -> CursorMenu:
        """로그 확인 메뉴 생성"""
        log_files = sorted(self.logs_dir.glob("*.log"), key=os.path.getmtime, reverse=True)[:20]
        self.submenu_data = list(log_files)

        items = []

        if not log_files:
            items.append(MenuItem("로그 파일이 없습니다", enabled=False))
        else:
            for i, log_file in enumerate(log_files):
                size = log_file.stat().st_size
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                desc = f"크기: {size:,} bytes | {mtime.strftime('%Y-%m-%d %H:%M:%S')}"
                items.append(MenuItem(log_file.name, value=i, description=desc))

        items.append(MenuItem("", enabled=False))  # 구분선
        items.append(MenuItem("🗑️  선택 파일 삭제", value="delete_selected", description="선택한 로그 삭제"))
        items.append(MenuItem("🧹 모든 로그 삭제", value="delete_all", description="모든 로그 파일 삭제"))
        items.append(MenuItem("← 뒤로 가기", value="back", description="메인 메뉴로 돌아가기"))

        return CursorMenu(
            title="로그 파일 확인",
            items=items,
            x=10,
            y=5,
            width=80,
            show_description=True
        )

    def handle_input(self, event: tcod.event.Event) -> None:
        """입력 처리"""
        if isinstance(event, tcod.event.Quit):
            self.running = False
            return

        if not isinstance(event, tcod.event.KeyDown):
            return

        key = event.sym

        # ESC - 뒤로가기 또는 종료
        if key == tcod.event.KeySym.ESCAPE:
            if self.state == LauncherState.MAIN_MENU:
                self.running = False
            else:
                self.state = LauncherState.MAIN_MENU
                self.current_menu = self.create_main_menu()
                play_sfx("ui", "cancel")
            return

        if not self.current_menu:
            return

        # 메뉴 조작
        if key == tcod.event.KeySym.UP or key == tcod.event.KeySym.k:
            self.current_menu.move_cursor_up()
        elif key == tcod.event.KeySym.DOWN or key == tcod.event.KeySym.j:
            self.current_menu.move_cursor_down()
        elif key == tcod.event.KeySym.RETURN or key == tcod.event.KeySym.z:
            self.handle_menu_selection()
        elif key == tcod.event.KeySym.x or key == tcod.event.KeySym.BACKSPACE:
            if self.state != LauncherState.MAIN_MENU:
                self.state = LauncherState.MAIN_MENU
                self.current_menu = self.create_main_menu()
                play_sfx("ui", "cancel")

    def handle_menu_selection(self) -> None:
        """메뉴 선택 처리"""
        if not self.current_menu:
            return

        selected = self.current_menu.get_selected_item()
        if not selected or not selected.enabled:
            return

        play_sfx("ui", "confirm")
        value = selected.value

        # 메인 메뉴
        if self.state == LauncherState.MAIN_MENU:
            if value == "game_normal":
                self.run_game("normal")
            elif value == "game_dev":
                self.run_game("dev")
            elif value == "game_debug":
                self.run_game("debug")
            elif value == "save_manager":
                self.state = LauncherState.SAVE_MANAGER
                self.current_menu = self.create_save_menu()
            elif value == "log_viewer":
                self.state = LauncherState.LOG_VIEWER
                self.current_menu = self.create_log_menu()
            elif value == "settings":
                self.state = LauncherState.SETTINGS
            elif value == "game_info":
                self.state = LauncherState.GAME_INFO
            elif value == "system_check":
                self.state = LauncherState.SYSTEM_CHECK
            elif value == "exit":
                self.running = False

        # 세이브 관리 메뉴
        elif self.state == LauncherState.SAVE_MANAGER:
            if value == "back":
                self.state = LauncherState.MAIN_MENU
                self.current_menu = self.create_main_menu()
            elif value == "backup_all":
                self.backup_all_saves()
            elif value == "delete_selected":
                self.delete_selected_save()
            elif isinstance(value, int):
                self.show_save_info(value)

        # 로그 확인 메뉴
        elif self.state == LauncherState.LOG_VIEWER:
            if value == "back":
                self.state = LauncherState.MAIN_MENU
                self.current_menu = self.create_main_menu()
            elif value == "delete_selected":
                self.delete_selected_log()
            elif value == "delete_all":
                self.delete_all_logs()
            elif isinstance(value, int):
                self.show_log_info(value)

    def run_game(self, mode: str):
        """게임 실행"""
        cmd = [sys.executable, str(self.main_script)]

        if mode == "dev":
            cmd.append("--dev")
            self.show_message("개발 모드로 게임을 시작합니다...", Colors.CYAN)
        elif mode == "debug":
            cmd.extend(["--debug", "--log=DEBUG"])
            self.show_message("디버그 모드로 게임을 시작합니다...", Colors.CYAN)
        else:
            self.show_message("게임을 시작합니다...", Colors.GREEN)

        # 화면 업데이트
        self.render()
        self.context.present(self.console)

        # 게임 실행
        try:
            result = subprocess.run(cmd, cwd=self.root_dir)
            if result.returncode == 0:
                self.show_message("게임이 정상 종료되었습니다.", Colors.GREEN)
            else:
                self.show_message(f"게임이 오류로 종료되었습니다. (코드: {result.returncode})", Colors.RED)
        except Exception as e:
            self.show_message(f"게임 실행 중 오류 발생: {e}", Colors.RED)

    def backup_all_saves(self):
        """모든 세이브 백업"""
        backup_dir = self.root_dir / "saves_backup"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"

        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            count = 0
            for save_file in self.saves_dir.glob("*.json"):
                shutil.copy2(save_file, backup_path / save_file.name)
                count += 1

            self.show_message(f"✓ {count}개의 세이브 파일을 백업했습니다.", Colors.GREEN)
            self.current_menu = self.create_save_menu()
        except Exception as e:
            self.show_message(f"✗ 백업 중 오류 발생: {e}", Colors.RED)

    def delete_selected_save(self):
        """선택한 세이브 삭제"""
        if not self.submenu_data:
            return

        selected = self.current_menu.get_selected_item()
        if not selected or not isinstance(selected.value, int):
            self.show_message("삭제할 파일을 선택하세요", Colors.YELLOW)
            return

        try:
            save_file = self.submenu_data[selected.value]
            save_file.unlink()
            self.show_message(f"✓ '{save_file.name}' 파일이 삭제되었습니다.", Colors.GREEN)
            self.current_menu = self.create_save_menu()
        except Exception as e:
            self.show_message(f"✗ 삭제 중 오류 발생: {e}", Colors.RED)

    def show_save_info(self, index: int):
        """세이브 정보 표시"""
        if not self.submenu_data or index >= len(self.submenu_data):
            return

        try:
            save_file = self.submenu_data[index]
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            info = f"파일: {save_file.name}"
            if 'floor' in data:
                info += f" | 층수: {data['floor']}층"
            if 'party' in data:
                party_count = len(data['party'])
                info += f" | 파티: {party_count}명"

            self.show_message(info, Colors.CYAN, duration=300)
        except Exception as e:
            self.show_message(f"✗ 정보 읽기 오류: {e}", Colors.RED)

    def delete_selected_log(self):
        """선택한 로그 삭제"""
        if not self.submenu_data:
            return

        selected = self.current_menu.get_selected_item()
        if not selected or not isinstance(selected.value, int):
            self.show_message("삭제할 로그를 선택하세요", Colors.YELLOW)
            return

        try:
            log_file = self.submenu_data[selected.value]
            log_file.unlink()
            self.show_message(f"✓ '{log_file.name}' 로그가 삭제되었습니다.", Colors.GREEN)
            self.current_menu = self.create_log_menu()
        except Exception as e:
            self.show_message(f"✗ 삭제 중 오류 발생: {e}", Colors.RED)

    def delete_all_logs(self):
        """모든 로그 삭제"""
        try:
            count = 0
            for log_file in self.logs_dir.glob("*.log"):
                log_file.unlink()
                count += 1
            self.show_message(f"✓ {count}개의 로그 파일이 삭제되었습니다.", Colors.GREEN)
            self.current_menu = self.create_log_menu()
        except Exception as e:
            self.show_message(f"✗ 삭제 중 오류 발생: {e}", Colors.RED)

    def show_log_info(self, index: int):
        """로그 정보 표시"""
        if not self.submenu_data or index >= len(self.submenu_data):
            return

        log_file = self.submenu_data[index]
        size = log_file.stat().st_size
        self.show_message(f"{log_file.name} | 크기: {size:,} bytes", Colors.CYAN, duration=300)

    def render(self):
        """화면 렌더링"""
        self.console.clear()

        # 배경
        for y in range(self.screen_height):
            for x in range(self.screen_width):
                self.console.print(x, y, " ", bg=(10, 10, 30))

        # 헤더
        self.render_header()

        # 상태별 렌더링
        if self.state in [LauncherState.MAIN_MENU, LauncherState.SAVE_MANAGER, LauncherState.LOG_VIEWER]:
            if self.current_menu:
                self.current_menu.render(self.console)
        elif self.state == LauncherState.SETTINGS:
            self.render_settings()
        elif self.state == LauncherState.GAME_INFO:
            self.render_game_info()
        elif self.state == LauncherState.SYSTEM_CHECK:
            self.render_system_check()

        # 메시지 표시
        if self.message_timer > 0:
            self.console.print(
                self.screen_width // 2 - len(self.message) // 2,
                self.screen_height - 3,
                self.message,
                fg=self.message_color
            )
            self.message_timer -= 1

        # 하단 도움말
        help_text = "↑↓: 이동 | Enter/Z: 선택 | ESC/X: 뒤로"
        self.console.print(
            self.screen_width // 2 - len(help_text) // 2,
            self.screen_height - 1,
            help_text,
            fg=Colors.GRAY
        )

    def render_header(self):
        """헤더 렌더링"""
        title = "⭐ Dawn of Stellar - 별빛의 여명 ⭐"
        subtitle = "Game Launcher v2.0.0"

        # 타이틀
        self.console.print(
            self.screen_width // 2 - len(title) // 2,
            2,
            title,
            fg=Colors.YELLOW
        )

        # 서브타이틀
        self.console.print(
            self.screen_width // 2 - len(subtitle) // 2,
            3,
            subtitle,
            fg=Colors.CYAN
        )

        # 구분선
        line = "─" * (self.screen_width - 4)
        self.console.print(2, 5, line, fg=Colors.GRAY)

    def render_settings(self):
        """설정 화면"""
        y = 10
        self.console.print(10, y, "⚙️  설정", fg=Colors.YELLOW)
        y += 2

        if self.config_file.exists():
            self.console.print(10, y, f"설정 파일: {self.config_file}", fg=Colors.CYAN)
            y += 2
            self.console.print(10, y, "설정 파일을 직접 편집하세요.", fg=Colors.WHITE)
        else:
            self.console.print(10, y, "설정 파일이 없습니다.", fg=Colors.RED)

        y += 3
        self.console.print(10, y, "ESC: 뒤로 가기", fg=Colors.GRAY)

    def render_game_info(self):
        """게임 정보 화면"""
        y = 10
        info_lines = [
            ("게임 이름:", "Dawn of Stellar - 별빛의 여명"),
            ("버전:", "5.0.0 (재구조화)"),
            ("장르:", "로그라이크 RPG + JRPG 퓨전"),
            ("엔진:", "Python 3.10+ / TCOD"),
            ("", ""),
            ("주요 기능:", ""),
            ("", "• 28개 직업 시스템"),
            ("", "• ATB + Brave 전투 시스템"),
            ("", "• AI 동료 시스템"),
            ("", "• 절차적 던전 생성"),
        ]

        self.console.print(10, y, "ℹ️  게임 정보", fg=Colors.YELLOW)
        y += 2

        for label, value in info_lines:
            if label:
                self.console.print(12, y, label, fg=Colors.CYAN)
                self.console.print(12 + len(label) + 1, y, value, fg=Colors.WHITE)
            else:
                self.console.print(12, y, value, fg=Colors.WHITE)
            y += 1

        y += 2
        self.console.print(10, y, "ESC: 뒤로 가기", fg=Colors.GRAY)

    def render_system_check(self):
        """시스템 체크 화면"""
        y = 10
        self.console.print(10, y, "🔍 시스템 체크", fg=Colors.YELLOW)
        y += 2

        # Python 버전
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.console.print(12, y, "Python 버전:", fg=Colors.CYAN)
        self.console.print(30, y, python_version, fg=Colors.GREEN if sys.version_info >= (3, 10) else Colors.RED)
        y += 2

        # 필수 파일
        self.console.print(12, y, "필수 파일:", fg=Colors.CYAN)
        y += 1

        essential_files = [
            ("main.py", self.main_script),
            ("config.yaml", self.config_file),
            ("src/", self.root_dir / "src"),
        ]

        for name, path in essential_files:
            exists = path.exists()
            status = "✓" if exists else "✗"
            color = Colors.GREEN if exists else Colors.RED
            self.console.print(14, y, f"{name:20} {status}", fg=color)
            y += 1

        y += 2
        self.console.print(10, y, "ESC: 뒤로 가기", fg=Colors.GRAY)

    def run(self):
        """메인 루프"""
        self.current_menu = self.create_main_menu()

        while self.running:
            # 렌더링
            self.render()
            self.context.present(self.console)

            # 이벤트 처리
            for event in tcod.event.wait():
                self.handle_input(event)

        self.context.close()


def main():
    """메인 함수"""
    try:
        launcher = GameLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n게임 런처를 종료합니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
