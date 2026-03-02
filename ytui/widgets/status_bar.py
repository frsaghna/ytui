from textual.widgets import Static
from textual.app import ComposeResult

class StatusBar(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = "Ready"

    def compose(self) -> ComposeResult:
        yield Static(self.content, id="status-text")

    def set_status(self, text: str):
        self.content = text
        self.query_one("#status-text", Static).update(text)
