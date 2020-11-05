from pathlib import Path
from typing import Union
import os


def get_download_location() -> Path:
    if os.getenv("CARLA_DOWNLOAD_LOCATION") is None:
        set_download_location("~/.cpdd_dataset")

    return Path(os.getenv("CARLA_DOWNLOAD_LOCATION")).expanduser()


def set_download_location(new_loc: Union[str, Path]):
    if not isinstance(new_loc, Path):
        new_loc = Path(new_loc)

    new_loc.mkdir(parents=True, exist_ok=True)
    os.environ["CARLA_DOWNLOAD_LOCATION"] = str(new_loc)
