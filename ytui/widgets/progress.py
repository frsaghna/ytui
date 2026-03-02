from textual.widgets import Static, ProgressBar
from textual.app import ComposeResult

class ProgressWidget(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._progress_bar = ProgressBar(total=100, show_percentage=True)

    def compose(self) -> ComposeResult:
        yield self._progress_bar

    def update_progress(self, progress: float, info: str = ""):
        self._progress_bar.progress = progress
