"""
게이지 렌더러

정밀한 유니코드 박스 문자 게이지
"""

from typing import Tuple


# 유니코드 블록 문자 (7단계) - 왼쪽에서 오른쪽으로 채워지는 블록 (U+258F ~ U+2588)
# 부분 블록만 (공백 제외)
BLOCK_CHARS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
FULL_BLOCK = "█"


class GaugeRenderer:
    """게이지 렌더러"""

    @staticmethod
    def render_bar(
        current: float,
        maximum: float,
        width: int = 10,
        show_numbers: bool = True,
        color_gradient: bool = True
    ) -> Tuple[str, Tuple[int, int, int]]:
        """
        게이지 바 렌더링

        Args:
            current: 현재 값
            maximum: 최대 값
            width: 게이지 너비 (문자 수)
            show_numbers: 숫자 표시 여부
            color_gradient: 색상 그라디언트 (빨강~노랑~초록)

        Returns:
            (게이지 문자열, 색상)
        """
        if maximum <= 0:
            ratio = 0.0
        else:
            ratio = min(1.0, current / maximum)

        # 채워진 블록 수 계산
        filled_blocks = ratio * width
        full_count = int(filled_blocks)
        partial = filled_blocks - full_count

        # 부분 블록 선택 (7단계)
        partial_index = int(partial * 7)
        partial_char = BLOCK_CHARS[partial_index] if partial > 0 and partial_index < len(BLOCK_CHARS) else ""

        # 게이지 문자열 생성 (공백 없이)
        gauge = FULL_BLOCK * full_count
        gauge += partial_char
        # 빈 공간은 표시하지 않음 (trailing spaces 제거)

        # 색상 계산
        if color_gradient:
            if ratio > 0.6:
                # 초록
                color = (100, 255, 100)
            elif ratio > 0.3:
                # 노랑
                color = (255, 255, 100)
            else:
                # 빨강
                color = (255, 100, 100)
        else:
            color = (200, 200, 200)

        # 숫자 추가
        if show_numbers:
            gauge += f" {int(current)}/{int(maximum)}"

        return gauge, color

    @staticmethod
    def render_percentage_bar(
        percentage: float,
        width: int = 10,
        show_percent: bool = True,
        custom_color: Tuple[int, int, int] = None
    ) -> Tuple[str, Tuple[int, int, int]]:
        """
        퍼센트 게이지 렌더링

        Args:
            percentage: 0.0 ~ 1.0
            width: 게이지 너비
            show_percent: 퍼센트 표시 여부
            custom_color: 커스텀 색상

        Returns:
            (게이지 문자열, 색상)
        """
        ratio = min(1.0, max(0.0, percentage))

        # 채워진 블록 수 계산
        filled_blocks = ratio * width
        full_count = int(filled_blocks)
        partial = filled_blocks - full_count

        # 부분 블록
        partial_index = int(partial * 7)
        partial_char = BLOCK_CHARS[partial_index] if partial > 0 and partial_index < len(BLOCK_CHARS) else ""

        # 게이지 문자열 (공백 없이)
        gauge = FULL_BLOCK * full_count
        gauge += partial_char
        # 빈 공간은 표시하지 않음 (trailing spaces 제거)

        # 색상
        if custom_color:
            color = custom_color
        else:
            # 기본 그라디언트
            if ratio > 0.6:
                color = (100, 255, 100)
            elif ratio > 0.3:
                color = (255, 255, 100)
            else:
                color = (255, 100, 100)

        # 퍼센트 추가
        if show_percent:
            gauge += f" {int(ratio * 100)}%"

        return gauge, color

    @staticmethod
    def render_casting_bar(
        progress: float,
        skill_name: str = "",
        width: int = 20
    ) -> Tuple[str, Tuple[int, int, int]]:
        """
        캐스팅 게이지 렌더링

        Args:
            progress: 진행도 (0.0 ~ 1.0)
            skill_name: 스킬 이름
            width: 게이지 너비

        Returns:
            (게이지 문자열, 색상)
        """
        ratio = min(1.0, max(0.0, progress))

        # 채워진 블록
        filled_blocks = ratio * width
        full_count = int(filled_blocks)
        partial = filled_blocks - full_count

        partial_index = int(partial * 7)
        partial_char = BLOCK_CHARS[partial_index] if partial > 0 and partial_index < len(BLOCK_CHARS) else ""

        # 게이지 (캐스팅은 항상 보라색)
        gauge = f"[{'▓' * full_count}{partial_char}{'░' * (width - full_count - (1 if partial_char else 0))}]"

        if skill_name:
            gauge = f"{skill_name}: {gauge}"

        color = (200, 150, 255)  # 보라색

        return gauge, color

    @staticmethod
    def render_status_icons(status_effects: dict) -> str:
        """
        상태이상 아이콘 렌더링

        Args:
            status_effects: {status_name: turns_remaining}

        Returns:
            아이콘 문자열
        """
        icon_map = {
            "poison": "🧪",
            "burn": "🔥",
            "freeze": "❄",
            "stun": "💫",
            "sleep": "💤",
            "silence": "🔇",
            "blind": "👁",
            "berserk": "😡",
            "haste": "⚡",
            "slow": "🐌",
            "regen": "💚",
            "reflect": "🛡",
            "barrier": "🔰",
            "break": "💔",
            "doom": "💀"
        }

        icons = []
        for status, turns in status_effects.items():
            icon = icon_map.get(status.lower(), "●")
            icons.append(f"{icon}{turns}")

        return " ".join(icons) if icons else ""

    @staticmethod
    def render_wound_indicator(wound_damage: int) -> Tuple[str, Tuple[int, int, int]]:
        """
        상처 데미지 표시

        Args:
            wound_damage: 상처 누적 데미지

        Returns:
            (표시 문자열, 색상)
        """
        if wound_damage <= 0:
            return "", (100, 100, 100)

        # 상처 레벨
        if wound_damage < 50:
            symbol = "🩹"  # 작은 상처
            color = (255, 200, 150)
        elif wound_damage < 150:
            symbol = "🤕"  # 중간 상처
            color = (255, 150, 100)
        else:
            symbol = "💀"  # 심각한 상처
            color = (255, 50, 50)

        return f"{symbol}{wound_damage}", color
