from textual.widgets import OptionList
from typing import List
from ..models import Format


class FormatList(OptionList):
    """A widget for displaying and selecting video formats."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._formats: List[Format] = []

    def set_formats(self, formats: List[Format]):
        self._formats = formats
        self.clear_options()

        for fmt in formats:
            self.add_option(str(fmt))

        if formats:
            self.highlighted = 0

    def clear(self):
        self._formats = []
        self.clear_options()

    def get_selected_format(self) -> str:
        index = self.highlighted

        if index is not None and 0 <= index < len(self._formats):
            return self._formats[index].format_id

        return "best"
