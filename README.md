# ytui

tui for yt-dlp i guess idk



## Installation

Ensure you have `yt-dlp` installed system-wide.

```bash
# Clone the repository
git clone https://github.com/frsaghna/ytui.git
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

idk man its shouldnt be that hard

### Requirements

- Python 3.12+
- `textual`
- `rich`
- `yt-dlp` (System-wide)

### Running in Development Mode

```fybash
textual run --dev ytui/app.py
```
