import re
from typing import Optional, List
from .models import Format

class OutputParser:
    # Example: [download]  10.0% of 100.00MiB at 10.00MiB/s ETA 00:10
    PROGRESS_REGEX = re.compile(r"\[download\]\s+(\d+\.?\d*)%")
    
    # Format parsing: format_id extension resolution note
    # Example: 243         webm      640x360    360p 414k , vp9, 24fps, video only, 4.41MiB
    FORMAT_REGEX = re.compile(r"(\w+)\s+(\w+)\s+(\d+x\d+|audio only)\s+(.*)")

    @staticmethod
    def parse_progress(line: str) -> Optional[float]:
        match = OutputParser.PROGRESS_REGEX.search(line)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def parse_formats(output_text: str) -> List[Format]:
        formats = []
        lines = output_text.splitlines()
        
        # Skip headers until we find the format table
        start_parsing = False
        for line in lines:
            if "ID" in line and "EXT" in line and "RESOLUTION" in line:
                start_parsing = True
                continue
            if not start_parsing:
                continue
            if line.startswith("[") or not line.strip():
                continue
            
            # Use simple split for ID, EXT, RESOLUTION, then the rest is NOTE
            parts = line.split(maxsplit=3)
            if len(parts) >= 3:
                format_id = parts[0]
                extension = parts[1]
                resolution = parts[2]
                note = parts[3] if len(parts) > 3 else ""
                
                # Check for filesize in note (very basic)
                filesize = None
                size_match = re.search(r"(\d+\.?\d*[KMG]iB)", note)
                if size_match:
                    filesize = size_match.group(1)
                
                formats.append(Format(
                    format_id=format_id,
                    extension=extension,
                    resolution=resolution,
                    filesize=filesize,
                    note=note.strip()
                ))
        return formats
