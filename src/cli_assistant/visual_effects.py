"""
Гарні візуальні ефекти для термінального інтерфейсу.

Цей модуль містить різноманітні візуальні ефекти, анімації та прикраси
для створення вражаючого інтерфейсу користувача в терміналі.
"""

import random
import time
from typing import List, Optional

import pyfiglet
from art import text2art
from halo import Halo
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.layout import Layout
from rich.rule import Rule
from colorama import Fore, Back, Style
from .animated_effects import AnimatedEffects


class VisualEffects:
    """Клас для створення гарних візуальних ефектів у терміналі."""
    
    def __init__(self, console: Optional[Console] = None):
        """Ініціалізація візуальних ефектів."""
        self.console = console or Console()
        self.animated = AnimatedEffects(self.console)
        self.colors = [
            "red", "green", "yellow", "blue", "magenta", "cyan", "white",
            "bright_red", "bright_green", "bright_yellow", "bright_blue",
            "bright_magenta", "bright_cyan", "bright_white"
        ]
        self.gradient_colors = [
            "#FF0000", "#FF3300", "#FF6600", "#FF9900", "#FFCC00", "#FFFF00",
            "#CCFF00", "#99FF00", "#66FF00", "#33FF00", "#00FF00", "#00FF33",
            "#00FF66", "#00FF99", "#00FFCC", "#00FFFF", "#00CCFF", "#0099FF",
            "#0066FF", "#0033FF", "#0000FF", "#3300FF", "#6600FF", "#9900FF",
            "#CC00FF", "#FF00FF", "#FF00CC", "#FF0099", "#FF0066", "#FF0033"
        ]
    
    def create_ascii_title(self, text: str, font: str = "big") -> str:
        """Створює ASCII-заголовок великими літерами."""
        try:
            return pyfiglet.figlet_format(text, font=font)
        except:
            # Якщо шрифт не знайдено, використовується стандартний
            return pyfiglet.figlet_format(text)
    
    def create_art_title(self, text: str, font: str = "block") -> str:
        """Створює художній ASCII-заголовок."""
        try:
            return text2art(text, font=font)
        except:
            # Якщо шрифт не знайдено, використовується стандартний
            return text2art(text)
    
    def display_animated_title(self, title: str, subtitle: str = "") -> None:
        """Відображає анімований заголовок з ефектами."""
        self.console.clear()
        
        # Створюємо ASCII-заголовок
        ascii_title = self.create_ascii_title(title)
        
        # Додаємо градієнтні кольори за допомогою стандартних назв кольорів Rich
        lines = ascii_title.split('\n')
        colored_lines = []
        
        color_sequence = [
            "red", "bright_red", "yellow", "bright_yellow", "green", 
            "bright_green", "cyan", "bright_cyan", "blue", "bright_blue", 
            "magenta", "bright_magenta"
        ]
        
        for i, line in enumerate(lines):
            if line.strip():  # Якщо рядок не порожній
                color = color_sequence[i % len(color_sequence)]
                colored_lines.append(Text(line, style=f"bold {color}"))
            else:
                colored_lines.append(Text(line))
        
        # Створюємо гарну панель
        panel = Panel(
            Align.center("\n".join(str(line) for line in colored_lines)),
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
            style="bold bright_white",
            border_style="bright_magenta"
        )
        
        self.console.print(panel)
        
        if subtitle:
            subtitle_panel = Panel(
                Align.center(Text(subtitle, style="italic bright_cyan")),
                box=box.ROUNDED,
                padding=(0, 1),
                style="bright_blue"
            )
            self.console.print(subtitle_panel)
        
        self.console.print()
    
    def display_loading_animation(self, text: str = "Loading...", duration: float = 0.8) -> None:
        """Відображає гарну анімацію завантаження."""
        spinner_styles = ['dots', 'line', 'pipe', 'simpleDots', 'simpleDotsScrolling', 
                         'star', 'star2', 'flip', 'hamburger', 'growVertical', 
                         'growHorizontal', 'balloon', 'balloon2', 'noise', 'bounce']
        
        spinner = Halo(
            text=text, 
            spinner=random.choice(spinner_styles),
            color='cyan'
        )
        
        spinner.start()
        time.sleep(duration)
        spinner.stop()
    
    def display_progress_bar(self, total: int, description: str = "Progress") -> Progress:
        """Створює гарний прогрес-бар з анімацією."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_green", finished_style="green"),
            TaskProgressColumn(),
            console=self.console
        )
        return progress
    
    def create_rainbow_text(self, text: str) -> Text:
        """Створює текст з райдужними кольорами."""
        rainbow_text = Text()
        colors = ["red", "bright_red", "yellow", "green", "cyan", "blue", "magenta"]
        
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            rainbow_text.append(char, style=f"bold {color}")
        
        return rainbow_text
    
    def display_success_message(self, message: str) -> None:
        """Відображає повідомлення про успіх з ефектами."""
        success_text = Text("✅ SUCCESS!", style="bold bright_green")
        
        panel = Panel(
            Align.center(f"{success_text}\n\n{message}"),
            box=box.DOUBLE,
            padding=(1, 2),
            style="bright_green",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def display_error_message(self, message: str) -> None:
        """Відображає повідомлення про помилку з ефектами."""
        error_text = Text("❌ ERROR!", style="bold bright_red")
        
        panel = Panel(
            Align.center(f"{error_text}\n\n{message}"),
            box=box.DOUBLE,
            padding=(1, 2),
            style="bright_red",
            border_style="red"
        )
        
        self.console.print(panel)
    
    def display_info_message(self, message: str, title: str = "INFO") -> None:
        """Відображає інформаційне повідомлення з ефектами."""
        info_text = Text(f"ℹ️  {title}!", style="bold bright_blue")
        
        panel = Panel(
            Align.center(f"{info_text}\n\n{message}"),
            box=box.ROUNDED,
            padding=(1, 2),
            style="bright_blue",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def create_gradient_rule(self, title: str = "") -> None:
        """Створює гарну лінію-розділювач з градієнтом."""
        self.console.print(Rule(title, style="bold magenta"))
    
    def display_celebration_animation(self) -> None:
        """Відображає анімацію святкування."""
        celebration_symbols = ["🎉", "🎊", "✨", "🌟", "💫", "🎆", "🎇"]
        
        for _ in range(2):  # Швидша анімація
            symbols = " ".join(random.choices(celebration_symbols, k=10))
            self.console.print(Align.center(Text(symbols, style="bright_yellow")))
            time.sleep(0.2)  # Швидший таймінг
    
    def create_fancy_table_style(self, table: Table) -> Table:
        """Застосовує гарний стиль до таблиці."""
        table.box = box.DOUBLE_EDGE
        table.border_style = "bright_blue"
        table.header_style = "bold bright_white on blue"
        table.row_styles = ["none", "dim"]
        return table
    
    def display_matrix_effect(self, duration: float = 3.0) -> None:
        """Відображає ефект 'Матриці' з падаючими символами."""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        width = self.console.size.width
        height = self.console.size.height
        
        with Live(auto_refresh=False) as live:
            for _ in range(int(duration * 10)):
                lines = []
                for _ in range(height - 5):
                    line = "".join(random.choices(chars, k=width))
                    lines.append(Text(line, style="bright_green"))
                
                live.update(Align.center("\n".join(str(line) for line in lines)))
                live.refresh()
                time.sleep(0.1)
    
    def create_neon_text(self, text: str, color: str = "bright_magenta") -> Text:
        """Створює неоновий ефект для тексту."""
        neon_text = Text()
        
        # Додаємо 'світіння' через повторення з різною інтенсивністю
        shadow_colors = ["dim " + color, color, "bold " + color]
        
        for shadow_color in shadow_colors:
            for char in text:
                neon_text.append(char, style=shadow_color)
            neon_text.append("\n")
        
        return neon_text
    
    def display_startup_sequence(self, app_name: str = "CLI Assistant") -> None:
        """Відображає гарну послідовність запуску додатку з анімаціями."""
        self.console.clear()
        
        # 1. Зворотний відлік
        self.animated.countdown_animation(3)
        
        # 2. Анімований логотип
        self.animated.animated_logo(3.0)
        
        # 3. Ефект Матриці
        self.animated.matrix_rain(2.0)
        
        # 4. Машинописний ефект для назви
        self.console.clear()
        self.animated.typewriter_effect(f"🤖 {app_name} 🤖", 0.08)
        time.sleep(1)
        
        # 5. Хвильова анімація для підзаголовка
        self.animated.wave_animation("Персональный ІІ-помічник нового покоління!", 2.0)
        
        # 6. Прогрес завантаження компонентів з анімацією
        components = [
            "🧠 Завантаження AI модуля",
            "💾 Ініціалізація бази даних", 
            "🎨 Налаштування інтерфейсу",
            "🔧 Перевірка системи",
            "✅ Готовий до роботи!"
        ]
        
        with self.display_progress_bar(len(components), "🚀 Запуск системи") as progress:
            task = progress.add_task("startup", total=len(components))
            
            for component in components:
                progress.update(task, description=component)
                # Додаємо випадкові затримки для реалістичності
                time.sleep(random.uniform(0.8, 1.5))
                progress.advance(task)
        
        # 7. Феєрверк успіху
        self.console.clear()
        self.animated.fireworks_effect(2.0)
        
        # 8. Фінальне повідомлення
        self.display_success_message("Система успішно запущена!")
        
        # 9. Стрибаюче привітання
        self.animated.bouncing_text("🌟 Ласкаво просимо в майбутнє! 🌟", 2.0)
    
    def display_menu_with_effects(self, title: str, options: List[str]) -> None:
        """Відображає гарне меню з візуальними ефектами."""
        self.create_gradient_rule(f"✨ {title} ✨")
        
        # Створюємо колонки для гарного відображення опцій
        columns = []
        for i, option in enumerate(options, 1):
            option_text = Text(f"{i}. {option}", style="bold bright_cyan")
            panel = Panel(
                option_text,
                box=box.ROUNDED,
                padding=(0, 1),
                style="blue"
            )
            columns.append(panel)
        
        self.console.print(Columns(columns, equal=True, expand=True))
        self.console.print()
