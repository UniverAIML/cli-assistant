"""
Interactive table with search, sort, and mouse navigation support.
Uses Textual for advanced terminal UI with mouse support.
"""

from typing import List, Dict, Any, Optional, Callable
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Input, Button, Header, Footer, Label
from textual.screen import Screen
from rich.text import Text
from rich.console import Console


class InteractiveTableScreen(Screen):
    """Interactive table screen with search and sort functionality."""
    
    def __init__(self, title: str, data: List[Dict[str, Any]], columns: List[str]):
        super().__init__()
        self.title = title
        self.original_data = data
        self.filtered_data = data.copy()
        self.columns = columns
        self.sort_column = None
        self.sort_reverse = False
        
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Label(f"📊 {self.title}", id="title")
            
            with Horizontal(id="controls"):
                yield Input(placeholder="🔍 Search...", id="search_input")
                yield Button("Clear", id="clear_btn")
                yield Button("Exit", id="exit_btn", variant="primary")
            
            yield DataTable(id="data_table", cursor_type="row")
            
            with Horizontal(id="stats"):
                yield Label("", id="stats_label")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the table when screen mounts."""
        table = self.query_one("#data_table", DataTable)
        
        # Add columns
        for col in self.columns:
            table.add_column(col, key=col)
        
        # Populate initial data
        self.update_table()
        self.update_stats()
        
        # Focus search input
        self.query_one("#search_input", Input).focus()
    
    def update_table(self) -> None:
        """Update table with current filtered data."""
        table = self.query_one("#data_table", DataTable)
        table.clear()
        
        # Sort data if needed
        if self.sort_column:
            self.filtered_data.sort(
                key=lambda x: str(x.get(self.sort_column, "")),
                reverse=self.sort_reverse
            )
        
        # Add rows
        for row_data in self.filtered_data:
            row_values = []
            for col in self.columns:
                value = row_data.get(col, "")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row_values.append(str(value))
            
            table.add_row(*row_values)
    
    def update_stats(self) -> None:
        """Update statistics label."""
        stats_label = self.query_one("#stats_label", Label)
        total = len(self.original_data)
        filtered = len(self.filtered_data)
        
        if filtered == total:
            stats_label.update(f"📈 Total: {total} items")
        else:
            stats_label.update(f"📈 Showing: {filtered} of {total} items")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search_input":
            search_term = event.value.lower().strip()
            
            if not search_term:
                self.filtered_data = self.original_data.copy()
            else:
                self.filtered_data = []
                for item in self.original_data:
                    # Search in all string fields
                    for value in item.values():
                        if isinstance(value, str) and search_term in value.lower():
                            self.filtered_data.append(item)
                            break
                        elif isinstance(value, list):
                            # Search in list items
                            for list_item in value:
                                if isinstance(list_item, str) and search_term in str(list_item).lower():
                                    self.filtered_data.append(item)
                                    break
            
            self.update_table()
            self.update_stats()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "clear_btn":
            search_input = self.query_one("#search_input", Input)
            search_input.value = ""
            self.filtered_data = self.original_data.copy()
            self.update_table()
            self.update_stats()
        elif event.button.id == "exit_btn":
            self.app.exit()
    
    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header clicks for sorting."""
        column_key = event.column_key
        
        # Get column name from ColumnKey object
        column_name = str(column_key) if hasattr(column_key, '__str__') else column_key
        if hasattr(column_key, 'value'):
            column_name = column_key.value
        elif hasattr(column_key, 'key'):
            column_name = column_key.key
        
        # Toggle sort direction if same column
        if self.sort_column == column_name:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_name
            self.sort_reverse = False
        
        self.update_table()
        
        # Show sort indicator in title
        sort_indicator = "↓" if self.sort_reverse else "↑"
        title_label = self.query_one("#title", Label)
        title_label.update(f"📊 {self.title} (Sorted by {column_name} {sort_indicator})")


class InteractiveTableApp(App):
    """Textual app for interactive tables."""
    
    CSS = """
    #main {
        padding: 1;
    }
    
    #title {
        text-align: center;
        background: blue;
        color: white;
        padding: 1;
        margin-bottom: 1;
    }
    
    #controls {
        height: 3;
        margin-bottom: 1;
    }
    
    #search_input {
        width: 1fr;
        margin-right: 1;
    }
    
    #clear_btn {
        min-width: 8;
        margin-right: 1;
    }
    
    #exit_btn {
        min-width: 8;
    }
    
    #data_table {
        height: 1fr;
        margin-bottom: 1;
    }
    
    #stats {
        height: 1;
        align: center middle;
    }
    
    #stats_label {
        text-align: center;
        color: cyan;
    }
    """
    
    def __init__(self, title: str, data: List[Dict[str, Any]], columns: List[str]):
        super().__init__()
        self.table_title = title
        self.table_data = data
        self.table_columns = columns
    
    def on_mount(self) -> None:
        """Mount the interactive table screen."""
        screen = InteractiveTableScreen(self.table_title, self.table_data, self.table_columns)
        self.push_screen(screen)


def show_interactive_contacts_table(contacts_data: List[Dict[str, Any]]) -> None:
    """Show interactive contacts table."""
    columns = ["Name", "Phones", "Birthday"]
    app = InteractiveTableApp("CONTACTS DATABASE", contacts_data, columns)
    app.run()


def show_interactive_notes_table(notes_data: List[Dict[str, Any]]) -> None:
    """Show interactive notes table."""
    columns = ["ID", "Title", "Content", "Tags", "Created"]
    app = InteractiveTableApp("NOTES DATABASE", notes_data, columns)
    app.run()


# Mouse-enabled menu for main navigation
class InteractiveMenuScreen(Screen):
    """Interactive menu with mouse support."""
    
    def __init__(self, title: str, options: List[str], callbacks: List[Callable]):
        super().__init__()
        self.title = title
        self.options = options
        self.callbacks = callbacks
    
    def compose(self) -> ComposeResult:
        """Compose menu layout."""
        yield Header(show_clock=True)
        
        with Container(id="menu_main"):
            yield Label(f"🌟 {self.title} 🌟", id="menu_title")
            
            with Vertical(id="menu_options"):
                for i, option in enumerate(self.options):
                    yield Button(f"{i+1}. {option}", id=f"option_{i}", variant="default")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu option selection."""
        button_id = event.button.id
        if button_id.startswith("option_"):
            option_index = int(button_id.split("_")[1])
            if option_index < len(self.callbacks):
                self.app.exit()  # Exit the menu
                # Execute callback
                self.callbacks[option_index]()


class MouseEnabledMenuApp(App):
    """Mouse-enabled menu application."""
    
    CSS = """
    #menu_main {
        padding: 2;
        align: center middle;
    }
    
    #menu_title {
        text-align: center;
        background: magenta;
        color: white;
        padding: 1;
        margin-bottom: 2;
    }
    
    #menu_options {
        width: 60%;
        align: center middle;
    }
    
    #menu_options Button {
        width: 100%;
        margin: 1;
        height: 3;
    }
    """
    
    def __init__(self, title: str, options: List[str], callbacks: List[Callable]):
        super().__init__()
        self.menu_title = title
        self.menu_options = options
        self.menu_callbacks = callbacks
    
    def on_mount(self) -> None:
        """Mount the menu screen."""
        screen = InteractiveMenuScreen(self.menu_title, self.menu_options, self.menu_callbacks)
        self.push_screen(screen)


def show_mouse_menu(title: str, options: List[str], callbacks: List[Callable]) -> None:
    """Show mouse-enabled menu."""
    app = MouseEnabledMenuApp(title, options, callbacks)
    app.run()
