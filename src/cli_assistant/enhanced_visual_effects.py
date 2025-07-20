"""
Enhanced visual effects with faster animations and better error handling.
"""

import random
import time
from typing import List, Optional

import pyfiglet  # type: ignore
from art import text2art  # type: ignore
from halo import Halo  # type: ignore
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


class EnhancedVisualEffects:
    """Enhanced visual effects class with better error handling."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize enhanced visual effects."""
        self.console = console or Console()
        self.colors = [
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
        ]

    def create_ascii_title(self, text: str, font: str = "big") -> str:
        """Create ASCII title with fallback."""
        try:
            return str(pyfiglet.figlet_format(text, font=font))
        except Exception:
            try:
                return str(pyfiglet.figlet_format(text))  # Use default font
            except Exception:
                pass

        # Fallback: create simple ASCII art
        return self._create_simple_ascii(text)

    def _create_simple_ascii(self, text: str) -> str:
        """Create simple ASCII art as fallback."""
        lines = [
            "=" * (len(text) + 4),
            f"  {text.upper()}  ",
            "=" * (len(text) + 4),
        ]
        return "\n".join(lines)

    def display_animated_title(self, title: str, subtitle: str = "") -> None:
        """Display animated title with effects."""
        self.console.clear()

        # Create ASCII title
        ascii_title = self.create_ascii_title(title)

        # Add gradient colors using standard Rich color names
        lines = ascii_title.split("\n")
        colored_lines = []

        color_sequence = [
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

        for i, line in enumerate(lines):
            if line.strip():  # If line is not empty
                color = color_sequence[i % len(color_sequence)]
                colored_lines.append(Text(line, style=f"bold {color}"))
            else:
                colored_lines.append(Text(line))

        # Create beautiful panel
        combined_text = Text()
        for line in colored_lines:  # type: ignore
            if isinstance(line, Text):
                combined_text.append_text(line)
            else:
                combined_text.append(str(line))
            combined_text.append("\n")
        panel = Panel(
            Align.center(combined_text),
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
            style="bold bright_white",
            border_style="bright_magenta",
        )

        self.console.print(panel)

        if subtitle:
            subtitle_panel = Panel(
                Align.center(Text(subtitle, style="italic bright_cyan")),
                box=box.ROUNDED,
                padding=(0, 1),
                style="bright_blue",
            )
            self.console.print(subtitle_panel)

        self.console.print()

    def display_loading_animation(
        self, text: str = "Loading...", duration: float = 0.5
    ) -> None:
        """Display loading animation with fallback."""
        try:
            spinner_styles = ["dots", "line", "pipe", "simpleDots"]
            spinner = Halo(
                text=text, spinner=random.choice(spinner_styles), color="cyan"
            )
            spinner.start()
            time.sleep(duration)
            spinner.stop()
            return
        except Exception:
            pass
        # Fallback animation
        self.console.print(f"[cyan]⏳ {text}[/cyan]")
        time.sleep(duration)
        self.console.print("[green]✅ Done![/green]")

    def display_progress_bar(
        self, total: int, description: str = "Progress"
    ) -> Progress:
        """Create beautiful progress bar with animation."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_green", finished_style="green"),
            TaskProgressColumn(),
            console=self.console,
        )
        return progress

    def create_rainbow_text(self, text: str) -> Text:
        """Create text with rainbow colors."""
        rainbow_text = Text()
        colors = ["red", "bright_red", "yellow", "green", "cyan", "blue", "magenta"]

        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            rainbow_text.append(char, style=f"bold {color}")

        return rainbow_text

    def display_success_message(self, message: str) -> None:
        """Display success message with effects."""
        success_text = Text("✅ SUCCESS!", style="bold bright_green")

        panel = Panel(
            Align.center(f"{success_text}\n\n{message}"),
            box=box.DOUBLE,
            padding=(1, 2),
            style="bright_green",
            border_style="green",
        )

        self.console.print(panel)

    def display_error_message(self, message: str) -> None:
        """Display error message with effects."""
        error_text = Text("❌ ERROR!", style="bold bright_red")

        panel = Panel(
            Align.center(f"{error_text}\n\n{message}"),
            box=box.DOUBLE,
            padding=(1, 2),
            style="bright_red",
            border_style="red",
        )

        self.console.print(panel)

    def display_info_message(self, message: str, title: str = "INFO") -> None:
        """Display info message with effects."""
        info_text = Text(f"ℹ️  {title}!", style="bold bright_blue")

        panel = Panel(
            Align.center(f"{info_text}\n\n{message}"),
            box=box.ROUNDED,
            padding=(1, 2),
            style="bright_blue",
            border_style="blue",
        )

        self.console.print(panel)

    def create_gradient_rule(self, title: str = "") -> None:
        """Create beautiful gradient separator line."""
        self.console.print(Rule(title, style="bold magenta"))

    def display_celebration_animation(self) -> None:
        """Display celebration animation."""
        celebration_symbols = ["🎉", "🎊", "✨", "🌟", "💫"]

        for _ in range(2):  # Faster animation
            symbols = " ".join(random.choices(celebration_symbols, k=8))
            self.console.print(Align.center(Text(symbols, style="bright_yellow")))
            time.sleep(0.2)  # Faster timing

    def create_fancy_table_style(self, table: Table) -> Table:
        """Apply beautiful style to table."""
        table.box = box.DOUBLE_EDGE
        table.border_style = "bright_blue"
        table.header_style = "bold bright_white on blue"
        table.row_styles = ["none", "dim"]
        return table

    def display_startup_sequence(self, app_name: str = "CLI Assistant") -> None:
        """Display beautiful startup sequence."""
        self.console.clear()

        # 1. Show logo
        self.display_loading_animation("Initializing system...", 0.3)

        # 2. ASCII title
        self.display_animated_title(app_name, "🤖 Personal AI Assistant v2.0 ✨")

        # 3. Component loading progress
        components = [
            "Loading AI module",
            "Initializing database",
            "Setting up interface",
            "System check",
            "Ready!",
        ]

        with self.display_progress_bar(len(components), "Starting system") as progress:
            task = progress.add_task("startup", total=len(components))

            for component in components:
                progress.update(task, description=component)
                time.sleep(0.3)  # Fast timing
                progress.advance(task)

        self.display_success_message("System successfully started!")
        time.sleep(0.3)  # Fast timing

        # 4. Final welcome
        welcome_msg = self.create_rainbow_text(
            "Welcome to the future of personal assistance!"
        )
        self.console.print(Align.center(welcome_msg))
        self.console.print()

    def display_menu_with_effects(self, title: str, options: List[str]) -> None:
        """Display beautiful menu with visual effects."""
        self.create_gradient_rule(f"✨ {title} ✨")

        # Create columns for beautiful option display
        columns = []
        for i, option in enumerate(options, 1):
            option_text = Text(f"{i}. {option}", style="bold bright_cyan")
            panel = Panel(option_text, box=box.ROUNDED, padding=(0, 1), style="blue")
            columns.append(panel)

        self.console.print(Columns(columns, equal=True, expand=True))
        self.console.print()
