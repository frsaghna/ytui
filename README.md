# ytui

A production-ready terminal TUI wrapper for `yt-dlp` built with Python and Textual.

## Features

- **Asynchronous Execution**: Downloads run in the background without blocking the UI.
- **Format Selection**: Fetch and select specific video/audio formats before downloading.
- **Download Queue**: Queue up multiple downloads to be processed sequentially.
- **Live Progress**: Real-time progress bar and status updates.
- **Clean Architecture**: Separation of concerns between UI, business logic, and subprocess handling.
- **Log Panel**: Detailed logs for all operations.

## Installation

Ensure you have `yt-dlp` installed system-wide.

```bash
# Clone the repository
git clone https://github.com/yourusername/ytui.git
cd ytui

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package in editable mode
pip install -e .
```

## Usage

Run the application using the `ytui` command:

```bash
ytui
```

### Keybindings

- `q`: Quit the application.
- `d`: Start download (Add to queue).
- `c`: Cancel the current active download.

### Workflow

1. Enter a valid YouTube (or other supported) URL.
2. Click **Fetch Formats** to see available quality options.
3. Select a format from the list.
4. Click **Add to Queue** to start the download.

## Architecture Overview

The project follows a clean architecture pattern:

- `ytui/app.py`: The Textual application orchestration layer.
- `ytui/runner.py`: Handles `yt-dlp` subprocess management and stdout streaming.
- `ytui/parser.py`: Regex-based parsing of `yt-dlp` output for progress and formats.
- `ytui/models.py`: Data structures (`DownloadJob`, `Format`).
- `ytui/queue.py`: FIFO queue logic for sequential downloads.
- `ytui/widgets/`: Reusable Textual components for progress, format selection, and status.

## Development

### Requirements

- Python 3.12+
- `textual`
- `rich`
- `yt-dlp` (System-wide)

### Running in Development Mode

```fybash
textual run --dev ytui/app.py
```
