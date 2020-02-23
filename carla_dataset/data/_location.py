from pathlib import Path
from typing import Union

_download_location = Path("~/.carla_dataset").expanduser()


def get_download_location() -> Path:
    global _download_location
    return _download_location


def set_download_location(new_loc: Union[str, Path]):
    global _download_location
    if not isinstance(new_loc, Path):
        new_loc = Path(new_loc)

    new_loc.mkdir(parents=True, exist_ok=True)
    _download_location = new_loc
