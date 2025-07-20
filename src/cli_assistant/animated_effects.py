"""
Додаткові анімовані ефекти для термінального інтерфейсу.

Цей модуль містить більш складні анімації та візуальні ефекти,
включаючи анімовані логотипи, інтерактивні елементи та тривимірні ефекти.
"""

import random
import threading
import time
from typing import List, TypedDict

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# Глобальное определение TypedDict для matrix_rain
class RainColumn(TypedDict):
    x: int
    y: float
    speed: float
    chars: str


class AnimatedEffects:
    """Клас для створення анімованих ефектів."""

    def __init__(self, console: Console):
        """Ініціалізація анімованих ефектів."""
        self.console = console
        self.is_animating = False

    def animated_logo(self, duration: float = 5.0) -> None:
        """Відображає анімований логотип з миганням."""
        frames = [
            """
   ██████╗██╗     ██╗    ██╗
  ██╔════╝██║     ██║    ██║
  ██║     ██║     ██║    ██║
  ██║     ██║     ██║    ██║
  ╚██████╗███████╗██║    ██║
   ╚═════╝╚══════╝╚═╝    ╚═╝
            """,
            """
   ██████╗██╗     ██╗    ██╗
  ██╔════╝██║     ██║    ██║
  ██║     ██║     ██║    ██║
  ██║     ██║     ██║    ██║
  ╚██████╗███████╗██║ ██╗██║
   ╚═════╝╚══════╝╚═╝ ╚═╝╚═╝
            """,
            """
   ██████╗██╗     ██╗ ██╗██╗
  ██╔════╝██║     ██║ ██║██║
  ██║     ██║     ██║ ██║██║
  ██║     ██║     ██║ ██║██║
  ╚██████╗███████╗██║ ██║██║
   ╚═════╝╚══════╝╚═╝ ╚═╝╚═╝
            """,
            """
   ██████╗██╗     ██║███║██╗
  ██╔════╝██║     ██║███║██║
  ██║     ██║     ██║███║██║
  ██║     ██║     ██║███║██║
  ╚██████╗███████╗██║███║██║
   ╚═════╝╚══════╝╚═╝╚══╝╚═╝
            """,
        ]

        colors = [
            "bright_red",
            "bright_green",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_yellow",
        ]

        with Live(auto_refresh=False) as live:
            start_time = time.time()
            frame_index = 0

            while time.time() - start_time < duration:
                color = random.choice(colors)
                frame = frames[frame_index % len(frames)]

                colored_frame = Text(frame, style=f"bold {color}")
                panel = Panel(
                    Align.center(colored_frame),
                    box=box.DOUBLE_EDGE,
                    border_style=color,
                    title="CLI Assistant",
                    title_align="center",
                )

                live.update(panel)
                live.refresh()

                time.sleep(0.3)
                frame_index += 1

    def wave_animation(self, text: str, duration: float = 3.0) -> None:
        """Створює хвильову анімацію тексту."""
        colors = [
            "red",
            "bright_red",
            "yellow",
            "bright_yellow",
            "green",
            "bright_green",
            "cyan",
            "bright_cyan",
            "blue",
            "bright_blue",
            "magenta",
            "bright_magenta",
        ]

        with Live(auto_refresh=False) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                wave_text = Text()
                for i, char in enumerate(text):
                    # Створюємо хвильовий ефект зі зміщенням по часу
                    wave_offset = int((time.time() * 5 + i * 0.5) % len(colors))
                    color = colors[wave_offset]
                    wave_text.append(char, style=f"bold {color}")

                panel = Panel(
                    Align.center(wave_text),
                    box=box.ROUNDED,
                    border_style="bright_white",
                )

                live.update(panel)
                live.refresh()
                time.sleep(0.1)

    def bouncing_text(self, text: str, duration: float = 4.0) -> None:
        """Створює ефект стрибаючого тексту."""
        height: int = int(self.console.size.height)
        width: int = int(self.console.size.width)

        with Live(auto_refresh=False) as live:
            start_time = time.time()
            y_position = 0
            direction = 1

            while time.time() - start_time < duration:
                # Обчислюємо позицію Y для стрибка
                y_position += direction
                if y_position >= height - 10 or y_position <= 0:
                    direction *= -1

                # Створюємо порожні рядки для позиціонування
                lines = [""] * int(y_position)

                # Додаємо текст з ефектом
                bounce_text = Text(text, style="bold bright_green")
                lines.append(str(Align.center(bounce_text)))

                # Додаємо решту порожніх рядків
                lines.extend([""] * (height - len(lines)))

                live.update("\n".join(lines[: height - 5]))
                live.refresh()
                time.sleep(0.1)

    def typewriter_effect(self, text: str, speed: float = 0.1) -> None:
        """Створює ефект друкарської машинки."""
        displayed_text = ""

        for char in text:
            displayed_text += char

            # Очищаємо консоль і виводимо поточний текст
            self.console.clear()
            typewriter_text = Text(displayed_text + "█", style="bright_green")
            panel = Panel(
                Align.center(typewriter_text),
                box=box.ROUNDED,
                border_style="green",
                title="Набираю текст...",
                title_align="center",
            )
            self.console.print(panel)

            # Випадкова затримка для реалістичності
            time.sleep(speed + random.uniform(0, 0.05))

        # Прибираємо курсор в кінці
        time.sleep(0.5)
        self.console.clear()
        final_text = Text(displayed_text, style="bright_green")
        panel = Panel(
            Align.center(final_text),
            box=box.ROUNDED,
            border_style="green",
            title="✅ Готово!",
            title_align="center",
        )
        self.console.print(panel)

    def matrix_rain(self, duration: float = 5.0) -> None:
        """Створює ефект дощу з Матриці."""
        chars: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        width: int = int(self.console.size.width)
        height: int = int(self.console.size.height) - 5
        # Ініціалізуємо колонки дощу
        rain_columns: list[RainColumn] = []
        for _ in range(width // 2):
            rain_columns.append(
                {
                    "x": int(random.randint(0, width - 1)),
                    "y": float(random.randint(-height, 0)),
                    "speed": float(random.uniform(0.5, 2.0)),
                    "chars": "".join(random.choices(chars, k=height)),
                }
            )

        with Live(auto_refresh=False) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                lines = [" " * width for _ in range(height)]

                # Оновлюємо кожну колонку дощу
                for column in rain_columns:
                    column["y"] = float(column["y"]) + float(column["speed"])
                    # Якщо колонка пройшла екран, скидаємо її
                    if float(column["y"]) > float(height):
                        column["y"] = float(-random.randint(10, 30))
                        column["x"] = int(random.randint(0, width - 1))
                        column["chars"] = "".join(random.choices(chars, k=height))
                    # Малюємо символи колонки
                    for i, char in enumerate(column["chars"]):
                        y_pos = int(float(column["y"]) - float(i))
                        if 0 <= y_pos < height and 0 <= int(column["x"]) < width:
                            lines[y_pos] = (
                                lines[y_pos][: int(column["x"])]
                                + char
                                + lines[y_pos][int(column["x"]) + 1 :]
                            )

                # Застосовуємо зелений колір до тексту
                matrix_text = Text("\n".join(lines), style="bright_green")
                live.update(matrix_text)
                live.refresh()

                time.sleep(0.05)

    def pulsating_border(self, text: str, duration: float = 3.0) -> None:
        """Створює ефект пульсуючої границі."""
        colors = ["dim", "bright_red", "red", "bright_red"]

        with Live(auto_refresh=False) as live:
            start_time = time.time()
            color_index = 0

            while time.time() - start_time < duration:
                color = colors[color_index % len(colors)]

                pulse_text = Text(text, style=f"bold {color}")
                panel = Panel(
                    Align.center(pulse_text),
                    box=box.DOUBLE_EDGE,
                    border_style=color,
                    padding=(2, 4),
                )

                live.update(panel)
                live.refresh()

                time.sleep(0.3)
                color_index += 1

    def spinning_loader(
        self, text: str = "Завантаження", duration: float = 2.0
    ) -> None:
        """Створює анімований спіннер."""
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        with Live(auto_refresh=False) as live:
            start_time = time.time()
            spinner_index = 0

            while time.time() - start_time < duration:
                spinner = spinner_chars[spinner_index % len(spinner_chars)]

                loading_text = Text(
                    f"{spinner} {text} {spinner}", style="bold bright_cyan"
                )
                panel = Panel(
                    Align.center(loading_text),
                    box=box.ROUNDED,
                    border_style="cyan",
                    padding=(1, 2),
                )

                live.update(panel)
                live.refresh()

                time.sleep(0.1)
                spinner_index += 1

    def fireworks_effect(self, duration: float = 3.0) -> None:
        """Створює ефект феєрверку."""
        firework_chars = ["*", "✦", "✧", "✩", "✪", "✫", "✬", "✭", "✮", "✯"]
        colors = [
            "bright_red",
            "bright_yellow",
            "bright_green",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
        ]

        with Live(auto_refresh=False) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                # Створюємо випадкові вибухи феєрверків
                fireworks = []
                for _ in range(random.randint(3, 8)):
                    x = random.randint(10, self.console.size.width - 10)
                    y = random.randint(3, self.console.size.height - 8)
                    char = random.choice(firework_chars)
                    color = random.choice(colors)
                    fireworks.append((x, y, char, color))

                # Створюємо текстові лінії
                lines = []
                for y in range(self.console.size.height - 5):
                    line: list[str] = [" "] * self.console.size.width
                    for fx, fy, char, color in fireworks:
                        if fy == y and 0 <= fx < len(line):
                            line[fx] = char
                    lines.append(line)

                # Застосовуємо кольори
                colored_lines: list[Text] = []
                for line in lines:
                    colored_line = Text()
                    for char in line:
                        if char != " ":
                            color = random.choice(colors)
                            colored_line.append(char, style=f"bold {color}")
                        else:
                            colored_line.append(char)
                    colored_lines.append(colored_line)
                display_text = Text("\n".join(str(line) for line in colored_lines))
                live.update(display_text)
                live.refresh()
                time.sleep(0.2)

    def countdown_animation(self, start: int = 5) -> None:
        """Створює анімований зворотний відлік."""
        for i in range(start, 0, -1):
            self.console.clear()

            # Створюємо велику цифру
            big_number = Text(str(i), style="bold bright_red")
            big_number.stylize("bold", 0, len(str(i)))

            # Розмір залежить від числа
            font_size = "█" * (20 - i * 3)  # Збільшуємо розмір до кінця

            panel = Panel(
                Align.center(big_number),
                box=box.DOUBLE_EDGE,
                border_style="bright_red" if i <= 3 else "yellow",
                padding=(3, 6),
                title=f"Запуск через {i}...",
                title_align="center",
            )

            self.console.print(panel)
            time.sleep(1)

        # Фінальний вибух
        self.console.clear()
        launch_text = Text("🚀 СТАРТ! 🚀", style="bold bright_green")
        panel = Panel(
            Align.center(launch_text),
            box=box.DOUBLE_EDGE,
            border_style="bright_green",
            padding=(2, 4),
        )
        self.console.print(panel)
        time.sleep(1)
