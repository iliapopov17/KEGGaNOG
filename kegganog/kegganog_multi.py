from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from .processing.pipeline import PipelineResult, run_multi

_log = logging.getLogger(__name__)


@dataclass
class MultiSampleRunner:
    """
    Orchestrates the multi-sample CLI pipeline.

    Responsibilities:
    - Resolve input file paths from a single path or a .txt list.
    - Read file bytes from disk.
    - Delegate processing to pipeline.run_multi().

    Parameters:
    - input_path: Path to a single annotation file or a .txt file
                  containing one annotation file path per line.
    - output_dir: Directory where results will be saved.
    - dpi: Resolution of the output image.
    - color: Seaborn colormap name.
    - group: Whether to use grouped heatmap layout.
    """

    input_path: str
    output_dir: str
    dpi: int = 300
    color: str = "Blues"
    group: bool = False

    def run(self) -> PipelineResult:
        """Execute the full multi-sample pipeline. Returns PipelineResult."""
        named_files = self._load_files()
        return run_multi(
            named_files=named_files,
            dpi=self.dpi,
            color=self.color,
            group=self.group,
            output_dir=self.output_dir,
        )

    def _collect_input_paths(self) -> list[str]:
        """Return a list of annotation file paths from a .txt list or a single path."""
        if self.input_path.endswith(".txt"):
            with open(self.input_path) as fh:
                return [line.strip() for line in fh if line.strip()]
        return [self.input_path]

    def _load_files(self) -> list[tuple[str, bytes]]:
        """Read each annotation file from disk. Skips missing files with a warning."""
        named_files: list[tuple[str, bytes]] = []
        for file_path in self._collect_input_paths():
            fp = Path(file_path)
            if not fp.is_file():
                _log.warning("Input file %s does not exist. Skipping.", file_path)
                continue
            named_files.append((fp.name, fp.read_bytes()))
        return named_files
