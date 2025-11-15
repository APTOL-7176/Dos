"""
인트로 스토리 시스템 - Dawn of Stellar

게임 시작 시 보여지는 스토리 인트로
다양한 화면 효과로 몰입도 향상
"""

import tcod
import tcod.console
import tcod.event
import time
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass

from src.core.logger import get_logger, Loggers


logger = get_logger(Loggers.SYSTEM)


@dataclass
class StoryLine:
    """스토리 라인"""
    text: str
    color: Tuple[int, int, int] = (255, 255, 255)  # 기본 흰색
    delay: float = 0.05  # 타이핑 딜레이
    pause: float = 1.5   # 라인 후 일시정지
    effect: str = "typing"  # typing, fade_in, flash, glitch


class IntroStorySystem:
    """인트로 스토리 시스템"""

    def __init__(self, console: tcod.console.Console, context: tcod.context.Context):
        self.console = console
        self.context = context
        self.screen_width = console.width
        self.screen_height = console.height
        self.skip_requested = False
        self.logger = logger

    def show_intro(self) -> bool:
        """
        인트로 스토리 표시

        Returns:
            True: 정상 완료, False: 스킵됨
        """
        # 인트로 BGM 재생
        try:
            from src.audio import play_bgm
            play_bgm("intro", loop=False, fade_in=True)
            logger.info("인트로 BGM 재생")
        except Exception as e:
            logger.warning(f"인트로 BGM 재생 실패: {e}")

        # 스토리 라인들
        story_lines = self._get_story_lines()

        # 페이드 인 효과
        self._fade_in()

        # 스토리 진행
        for i, line in enumerate(story_lines):
            if self._check_skip():
                logger.info("인트로 스킵됨")
                return False

            # 라인 표시
            if line.effect == "typing":
                self._show_typing_effect(line, i)
            elif line.effect == "fade_in":
                self._show_fade_in_line(line, i)
            elif line.effect == "flash":
                self._show_flash_line(line, i)
            elif line.effect == "glitch":
                self._show_glitch_line(line, i)

            # 일시정지
            if not self._wait_with_skip_check(line.pause):
                logger.info("인트로 스킵됨")
                return False

        # 마지막 메시지
        if not self._show_continue_prompt():
            logger.info("인트로 스킵됨")
            return False

        # 페이드 아웃
        self._fade_out()

        logger.info("인트로 정상 완료")
        return True

    def _get_story_lines(self) -> List[StoryLine]:
        """스토리 라인 목록"""
        return [
            # 시작
            StoryLine(
                "별빛의 여명",
                color=(255, 215, 0),  # 금색
                delay=0.08,
                pause=2.0,
                effect="fade_in"
            ),
            StoryLine(
                "Dawn of Stellar",
                color=(200, 200, 255),  # 연한 청색
                delay=0.06,
                pause=2.5,
                effect="typing"
            ),

            # 빈 줄
            StoryLine("", pause=1.0),

            # 스토리 시작
            StoryLine(
                "서기 2157년, 지구...",
                color=(220, 220, 220),
                delay=0.04,
                pause=1.8,
                effect="typing"
            ),
            StoryLine(
                "인류는 마침내 수백 년의 꿈을 이루어냈다.",
                color=(200, 200, 200),
                delay=0.03,
                pause=1.5,
                effect="typing"
            ),
            StoryLine(
                "전쟁은 역사책 속 이야기가 되었고,",
                color=(180, 180, 180),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "병과 기아는 정복되었으며,",
                color=(180, 180, 180),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "인간의 평균 수명은 150세를 넘어섰다.",
                color=(160, 160, 160),
                delay=0.03,
                pause=2.0,
                effect="typing"
            ),

            # 빈 줄
            StoryLine("", pause=1.0),

            # 전환
            StoryLine(
                "그러나...",
                color=(255, 100, 100),  # 붉은색
                delay=0.06,
                pause=2.0,
                effect="flash"
            ),

            # 사건
            StoryLine(
                "2157년 3월 15일, 오전 9시 27분.",
                color=(255, 255, 100),  # 노란색
                delay=0.04,
                pause=1.5,
                effect="typing"
            ),
            StoryLine(
                "시공간 연구소에서 실험 중이던 시간 도약 장치가",
                color=(200, 200, 200),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "예기치 않은 공명을 일으켰다.",
                color=(200, 200, 200),
                delay=0.03,
                pause=2.0,
                effect="typing"
            ),

            # 빈 줄
            StoryLine("", pause=1.0),

            # 글리치 효과
            StoryLine(
                "[ 시 공 교 란 발 생 ]",
                color=(255, 50, 50),
                delay=0.08,
                pause=2.0,
                effect="glitch"
            ),

            # 빈 줄
            StoryLine("", pause=1.0),

            # 결과
            StoryLine(
                "과거와 미래, 다른 차원의 역사들이",
                color=(150, 200, 255),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "뒤섞이기 시작했다.",
                color=(150, 200, 255),
                delay=0.03,
                pause=2.0,
                effect="typing"
            ),
            StoryLine(
                "전설 속의 영웅들, 신화의 괴물들,",
                color=(200, 150, 255),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "그리고 이름 없는 모험가들이",
                color=(200, 150, 255),
                delay=0.03,
                pause=1.2,
                effect="typing"
            ),
            StoryLine(
                "우리의 세계로 쏟아져 들어왔다.",
                color=(200, 150, 255),
                delay=0.03,
                pause=2.5,
                effect="typing"
            ),

            # 빈 줄
            StoryLine("", pause=1.5),

            # 마지막
            StoryLine(
                "당신은 그 혼돈 속에서 깨어난",
                color=(255, 255, 255),
                delay=0.04,
                pause=1.5,
                effect="fade_in"
            ),
            StoryLine(
                "한 명의 모험가이다.",
                color=(255, 255, 255),
                delay=0.04,
                pause=2.5,
                effect="fade_in"
            ),

            # 빈 줄
            StoryLine("", pause=1.0),

            # 제목 반복
            StoryLine(
                "별빛의 여명",
                color=(255, 215, 0),
                delay=0.06,
                pause=3.0,
                effect="flash"
            ),
        ]

    def _show_typing_effect(self, line: StoryLine, line_index: int):
        """타이핑 효과"""
        y = self.screen_height // 2 - 10 + line_index * 2

        displayed_text = ""
        for char in line.text:
            if self._check_skip():
                # 스킵 시 전체 텍스트 즉시 표시
                self.console.print(
                    (self.screen_width - len(line.text)) // 2,
                    y,
                    line.text,
                    fg=line.color
                )
                self.context.present(self.console)
                return

            displayed_text += char
            self.console.print(
                (self.screen_width - len(line.text)) // 2,
                y,
                displayed_text,
                fg=line.color
            )
            self.context.present(self.console)
            time.sleep(line.delay)

    def _show_fade_in_line(self, line: StoryLine, line_index: int):
        """페이드 인 효과"""
        y = self.screen_height // 2 - 10 + line_index * 2
        x = (self.screen_width - len(line.text)) // 2

        # 10단계 페이드 인
        for alpha in range(0, 11):
            if self._check_skip():
                self.console.print(x, y, line.text, fg=line.color)
                self.context.present(self.console)
                return

            brightness = alpha / 10.0
            faded_color = tuple(int(c * brightness) for c in line.color)
            self.console.print(x, y, line.text, fg=faded_color)
            self.context.present(self.console)
            time.sleep(0.05)

    def _show_flash_line(self, line: StoryLine, line_index: int):
        """깜빡임 효과"""
        y = self.screen_height // 2 - 10 + line_index * 2
        x = (self.screen_width - len(line.text)) // 2

        # 3번 깜빡임
        for _ in range(3):
            if self._check_skip():
                self.console.print(x, y, line.text, fg=line.color)
                self.context.present(self.console)
                return

            # 밝게
            self.console.print(x, y, line.text, fg=line.color)
            self.context.present(self.console)
            time.sleep(0.2)

            # 어둡게
            dark_color = tuple(c // 3 for c in line.color)
            self.console.print(x, y, line.text, fg=dark_color)
            self.context.present(self.console)
            time.sleep(0.2)

        # 최종적으로 밝게
        self.console.print(x, y, line.text, fg=line.color)
        self.context.present(self.console)

    def _show_glitch_line(self, line: StoryLine, line_index: int):
        """글리치 효과"""
        y = self.screen_height // 2 - 10 + line_index * 2
        x = (self.screen_width - len(line.text)) // 2

        # 글리치 문자들
        glitch_chars = ['█', '▓', '▒', '░', '▄', '▀', '■', '□']

        # 5번 글리치
        for _ in range(5):
            if self._check_skip():
                self.console.print(x, y, line.text, fg=line.color)
                self.context.present(self.console)
                return

            # 랜덤 글리치 텍스트
            glitched = ''.join(
                random.choice(glitch_chars) if random.random() < 0.3 else c
                for c in line.text
            )
            self.console.print(x, y, glitched, fg=line.color)
            self.context.present(self.console)
            time.sleep(0.1)

        # 원본 텍스트
        self.console.print(x, y, line.text, fg=line.color)
        self.context.present(self.console)

    def _fade_in(self):
        """화면 페이드 인"""
        for alpha in range(0, 11):
            if self._check_skip():
                return

            brightness = alpha / 10.0
            bg_color = tuple(int(0 * brightness) for _ in range(3))

            # 배경 채우기
            for y in range(self.screen_height):
                for x in range(self.screen_width):
                    self.console.rgb["bg"][y, x] = bg_color

            self.context.present(self.console)
            time.sleep(0.05)

    def _fade_out(self):
        """화면 페이드 아웃"""
        for alpha in range(10, -1, -1):
            if self._check_skip():
                self.console.clear()
                self.context.present(self.console)
                return

            brightness = alpha / 10.0

            # 모든 텍스트를 어둡게
            for y in range(self.screen_height):
                for x in range(self.screen_width):
                    current_fg = self.console.rgb["fg"][y, x]
                    faded_fg = tuple(int(c * brightness) for c in current_fg)
                    self.console.rgb["fg"][y, x] = faded_fg

            self.context.present(self.console)
            time.sleep(0.05)

        self.console.clear()
        self.context.present(self.console)

    def _show_continue_prompt(self) -> bool:
        """계속 진행 프롬프트"""
        prompt = "Press Enter to continue..."
        y = self.screen_height - 3
        x = (self.screen_width - len(prompt)) // 2

        # 깜빡이는 프롬프트
        for _ in range(10):  # 최대 10번 깜빡임
            if self._check_skip():
                return True

            # 밝게
            self.console.print(x, y, prompt, fg=(200, 200, 200))
            self.context.present(self.console)
            if self._wait_with_skip_check(0.5):
                return True

            # 어둡게
            self.console.print(x, y, prompt, fg=(100, 100, 100))
            self.context.present(self.console)
            if self._wait_with_skip_check(0.5):
                return True

        return True

    def _check_skip(self) -> bool:
        """스킵 체크 (Enter 키)"""
        for event in tcod.event.get():
            if isinstance(event, tcod.event.KeyDown):
                if event.sym == tcod.event.KeySym.RETURN or event.sym == tcod.event.KeySym.KP_ENTER:
                    self.skip_requested = True
                    return True
            elif isinstance(event, tcod.event.Quit):
                self.skip_requested = True
                return True

        return self.skip_requested

    def _wait_with_skip_check(self, duration: float) -> bool:
        """
        대기하면서 스킵 체크

        Returns:
            True: 스킵됨, False: 정상 대기
        """
        start_time = time.time()
        while time.time() - start_time < duration:
            if self._check_skip():
                return True
            time.sleep(0.01)
        return False


def show_intro_story(console: tcod.console.Console, context: tcod.context.Context) -> bool:
    """
    인트로 스토리 표시

    Args:
        console: TCOD 콘솔
        context: TCOD 컨텍스트

    Returns:
        True: 정상 완료, False: 스킵됨
    """
    intro = IntroStorySystem(console, context)
    return intro.show_intro()
