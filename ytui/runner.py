import asyncio
import subprocess
from typing import AsyncGenerator, List, Optional
from .models import Format
from .parser import OutputParser

class DownloadRunner:
    def __init__(self):
        self._process: Optional[asyncio.subprocess.Process] = None

    async def fetch_formats(self, url: str) -> List[Format]:
        """Fetch available formats for a given URL."""
        try:
            cmd = ["yt-dlp", "-F", url]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"yt-dlp failed: {stderr.decode()}")
            
            return OutputParser.parse_formats(stdout.decode())
        except Exception as e:
            raise Exception(f"Error fetching formats: {e}")

    async def download(self, url: str, output_path: str, format_id: Optional[str] = None) -> AsyncGenerator[float, None]:
        """Run the download and yield progress."""
        cmd = ["yt-dlp", "--newline", "--progress", "-o", f"{output_path}/%(title)s.%(ext)s"]
        if format_id:
            cmd.extend(["-f", format_id])
        cmd.append(url)

        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            if self._process.stdout:
                while True:
                    line_bytes = await self._process.stdout.readline()
                    if not line_bytes:
                        break
                    
                    line = line_bytes.decode(errors="replace").strip()
                    progress = OutputParser.parse_progress(line)
                    if progress is not None:
                        yield progress

            await self._process.wait()
            if self._process.returncode != 0 and self._process.returncode != -9:
                 raise Exception(f"Download failed with code {self._process.returncode}")

        except asyncio.CancelledError:
            self.cancel()
            raise
        except Exception as e:
            raise Exception(f"Download error: {e}")
        finally:
            self._process = None

    def cancel(self):
        """Cancel the current download process."""
        if self._process:
            try:
                self._process.terminate()
            except ProcessLookupError:
                pass
