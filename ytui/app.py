import asyncio
from typing import List, Optional
from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Static, ProgressBar, OptionList
from textual.containers import Vertical, Container
from textual import on, work
from textual.binding import Binding

from .models import DownloadJob, DownloadStatus, Format
from .runner import DownloadRunner
from .queue import DownloadQueue
from .widgets.progress import ProgressWidget
from .widgets.format_list import FormatList
from .widgets.status_bar import StatusBar

CSS = """
Screen {
    background: #121212;
    color: #e0e0e0;
}

#main-container {
    padding: 1 2;
}

/* Inputs */
.step-container {
    height: auto;
    margin-top: 1;
}

Input {
    border: none;
    background: transparent;
    padding: 0 1;
    height: 1;
}

.input-label {
    text-style: bold;
    padding-left: 1;
}

/* Highlight active step label */
.step-container:focus-within .input-label {
    color: #bb86fc;
}

.theme-light .step-container:focus-within .input-label {
    color: #6200ee;
}

.theme-nord .step-container:focus-within .input-label {
    color: #88c0d0;
}

/* Format selection */
#format-selection {
    height: 8;
    background: transparent;
    border: none;
    padding: 0;
}

/* Log */
#log-panel {
    height: 1fr;
    margin-top: 1;
    border: none;
    opacity: 60%;
}

#log-panel > .log--content {
    padding: 0;
}

/* Progress */
#progress-container {
    height: 1;
    margin-top: 1;
}

ProgressWidget Horizontal {
    height: 1;
}

ProgressBar {
    width: 20;
    padding: 0;
    margin: 0;
}

/* Status bar */
StatusBar {
    dock: bottom;
    padding: 0 2;
    height: 1;
}

/* ===================== */
/* THEMES */
/* ===================== */

/* DARK (default) */
.theme-dark Screen {
    background: #121212;
    color: #e0e0e0;
}

.theme-dark .input-label,
.theme-dark Input:focus {
    color: #bb86fc;
}

.theme-dark StatusBar {
    background: #1e1e1e;
    color: #e0e0e0;
}

.theme-dark ProgressBar > .progress--bar {
    color: #bb86fc;
    background: #1e1e1e;
}

/* LIGHT */
.theme-light Screen {
    background: #ffffff;
    color: #000000;
}

.theme-light .input-label,
.theme-light Input:focus {
    color: #6200ee;
}

.theme-light StatusBar {
    background: #f0f0f0;
    color: #000000;
}

.theme-light ProgressBar > .progress--bar {
    color: #6200ee;
    background: #e0e0e0;
}

/* NORD */
.theme-nord Screen {
    background: #2e3440;
    color: #d8dee9;
}

.theme-nord .input-label,
.theme-nord Input:focus {
    color: #88c0d0;
}

.theme-nord StatusBar {
    background: #3b4252;
    color: #d8dee9;
}

.theme-nord ProgressBar > .progress--bar {
    color: #88c0d0;
    background: #3b4252;
}
"""
class YTUIApp(App):
    CSS = CSS
    TITLE = "ytui"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("enter", "context_submit", "Submit"),
        Binding("ctrl+f", "fetch_formats", "Fetch"),
        Binding("ctrl+d", "start_download", "Download"),
        Binding("ctrl+t", "toggle_theme", "Theme"),
        Binding("ctrl+c", "cancel_download", "Cancel"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("tab", "focus_next", "Next"),
        Binding("shift+tab", "focus_previous", "Prev"),
        Binding("ctrl+h", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self._runner = DownloadRunner()
        self._queue = DownloadQueue(self._on_queue_update)
        self._current_formats: List[Format] = []
        self._themes = ["theme-dark", "theme-light", "theme-nord"]
        self._current_theme_idx = 0
        self._formats_loaded = False

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def compose(self) -> ComposeResult:
        with Vertical(id="main-container"):
            with Vertical(classes="step-container"):
                yield Static("1. OUTPUT PATH", id="label-path", classes="input-label")
                yield Input(
                    placeholder="Where to save? (default: .)",
                    id="path-input",
                    value="."
                )

            with Vertical(classes="step-container"):
                yield Static("2. VIDEO URL", id="label-url", classes="input-label")
                yield Input(
                    placeholder="Paste YouTube link and press Enter",
                    id="url-input"
                )

            with Vertical(classes="step-container"):
                yield Static("3. SELECT FORMAT", id="label-format", classes="input-label")
                yield FormatList(id="format-selection")

            yield Log(id="log-panel")

            with Container(id="progress-container"):
                yield ProgressWidget(id="download-progress")

        yield StatusBar(id="status-bar")

    def on_mount(self):
        self.add_class(self._themes[self._current_theme_idx])
        self.query_one("#path-input", Input).focus()
        self._set_hint(
            "Step 1: Set Path → Enter | Tab: Navigate | Ctrl+H: Help"
        )

    # --------------------------------------------------
    # Status Helpers
    # --------------------------------------------------

    def _set_hint(self, text: str):
        self.query_one("#status-bar", StatusBar).set_status(text)

    def _log(self, text: str):
        self.query_one("#log-panel", Log).write_line(text)

    # --------------------------------------------------
    # Flow Logic
    # --------------------------------------------------

    @on(Input.Submitted, "#path-input")
    def on_path_submitted(self):
        self.query_one("#url-input", Input).focus()
        self._set_hint("Step 2: Enter URL → Enter to Fetch Formats")

    @on(Input.Submitted, "#url-input")
    def on_url_submitted(self):
        self.run_worker(self.action_fetch_formats())

    @on(OptionList.OptionSelected, "#format-selection")
    def on_format_selected(self):
        self.action_start_download()

    def action_context_submit(self):
        focused = self.focused

        if focused and focused.id == "path-input":
            self.on_path_submitted()
        elif focused and focused.id == "url-input":
            self.on_url_submitted()
        elif focused and isinstance(focused, FormatList):
            self.action_start_download()

    # --------------------------------------------------
    # Fetch Formats
    # --------------------------------------------------

    async def action_fetch_formats(self):
        url = self.query_one("#url-input", Input).value.strip()

        if not url:
            self.notify("URL required")
            return

        self._formats_loaded = False
        self._set_hint("Fetching formats...")
        self._log(f"Fetching formats for: {url}")

        try:
            formats = await self._runner.fetch_formats(url)
            self._current_formats = formats

            format_list = self.query_one("#format-selection", FormatList)
            format_list.set_formats(formats)

            

            self._formats_loaded = True
            format_list.focus()

            self._set_hint(
                "Step 3: Select Format ↑↓ → Press Enter to Download"
            )

        except Exception as e:
            self.notify(str(e))
            self._log(f"Error: {e}")
            self._set_hint("Failed to fetch formats | Check URL")

    # --------------------------------------------------
    # Download
    # --------------------------------------------------

    def action_start_download(self):
        if not self._formats_loaded:
            self._set_hint("Fetch formats before downloading")
            return

        url = self.query_one("#url-input", Input).value.strip()
        path = self.query_one("#path-input", Input).value.strip() or "."
        format_id = self.query_one("#format-selection", FormatList).get_selected_format()

        if not url:
            self.notify("URL required", variant="error")
            return

        if not format_id:
            self.notify("Select a format", variant="error")
            return

        self.query_one("#download-progress", ProgressWidget).update_progress(0, "0%")

        job = DownloadJob(url=url, output_path=path, format_id=format_id)
        self._queue.add_job(job)

        self._log(f"Queued: {url}")
        self._set_hint("Downloading... Ctrl+C to cancel")

        self.process_queue()

    @work(exclusive=True)
    async def process_queue(self):
        await self._queue.start(self.run_download)

    async def run_download(self, job: DownloadJob):
        job.status = DownloadStatus.DOWNLOADING

        try:
            async for progress in self._runner.download(
                job.url,
                job.output_path,
                job.format_id
            ):
                job.progress = progress
                self.query_one("#download-progress", ProgressWidget).update_progress(
                    progress,
                    f"{progress}%"
                )

            job.status = DownloadStatus.COMPLETED
            self._log(f"Completed: {job.url}")
            self._set_hint("Download finished! → Press Enter to start new")

            self.query_one("#path-input", Input).focus()
            

        except Exception as e:
            job.status = DownloadStatus.FAILED
            job.error_message = str(e)

            self._log(f"Failed: {e}")
            self._set_hint("Download failed")

    # --------------------------------------------------
    # Cancel / Theme / Help
    # --------------------------------------------------

    def action_cancel_download(self):
        self._runner.cancel()
        self._set_hint("Download cancelled")

    def action_reset(self):
        self.query_one("#path-input", Input).value = "."
        self.query_one("#url-input", Input).value = ""
        self.query_one("#format-selection", FormatList).clear()
        self._formats_loaded = False
        self.query_one("#path-input", Input).focus()
        self._set_hint("App reset | Step 1: Set Path")
        self._log("App reset")

    def action_toggle_theme(self):
        self.remove_class(self._themes[self._current_theme_idx])
        self._current_theme_idx = (
            self._current_theme_idx + 1
        ) % len(self._themes)
        self.add_class(self._themes[self._current_theme_idx])

        theme_name = self._themes[self._current_theme_idx].replace("theme-", "")
        self._set_hint(f"Theme: {theme_name}")

    def action_help(self):
        self._set_hint(
            "Flow: Path → Enter → URL → Enter → Select Format → Enter | "
            "Tab: Navigate | Ctrl+T: Theme | Ctrl+C: Cancel | q: Quit"
        )

    # --------------------------------------------------

    def _on_queue_update(self, job: DownloadJob):
        self._log(f"Added to queue: {job.url}")

def main():
    app = YTUIApp()
    app.run()

if __name__ == "__main__":
    main()
