from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import h5py
import s3fs
from carla_dataset.intrinsics import CylindricalIntrinsics, SphericalIntrinsics, PinholeIntrinsics
from carla_dataset.intrinsics._intrinsics import Intrinsics


class DataSource(ABC):
    @property
    @abstractmethod
    def data(self) -> Data:
        pass

    def __enter__(self) -> Data:
        if not self.is_downloaded:
            raise ValueError(f"{self} is  not downloaded")

        return self.data

    def __exit__(self, exc_type, exc_val: Data, exc_tb):
        exc_val.close()

    @abstractmethod
    def download(self, force: bool = False) -> DataSource:
        pass

    @abstractmethod
    def is_downloaded(self) -> bool:
        pass


class PoseData:
    def __init__(self, file: h5py.File):
        self._file = file

    def close(self):
        return self._file.close()

    @property
    def absolute_pose(self) -> h5py.Dataset:
        """
        The absolute pose (origin is determined by the simulator, and is not significant)

        :return: A (frames, 6) float32 Dataset
        """
        return self._file["abs_pose"]

    @property
    def relative_pose(self) -> h5py.Dataset:
        """
        The pose relative to the previous pose

        :return: A (frames, 6) float32 Dataset
        """
        return self._file["rel_pose"]

    @property
    def start_relative_pose(self) -> h5py.Dataset:
        """
        The pose relative to the initial pose

        :return: A (frames, 6) float32 Dataset
        """
        return self._file["start_rel_pose"]


class Data:
    def __init__(self, file: h5py.File, data: h5py.Group, intrinsics: Intrinsics):
        self._data: h5py.Group = data
        self._file: h5py.File = file
        self._intrinsics = intrinsics

    @property
    def color(self) -> h5py.Dataset:
        """
        :return: A (frames, height, width, 3) uint8 Dataset
        """
        return self._data["rgb"]

    @property
    def depth(self) -> h5py.Dataset:
        """
        #TODO check is this (*, 1)
        Depth is measured in dm (10th of a meter).
        :return: A (frames, height, width) uint16 Dataset
        """
        return self._data["depth"]

    @property
    def intrinsics(self) -> Intrinsics:
        return self._intrinsics

    def close(self):
        return self._file.close()


class SplitData:
    def __init__(self, file: h5py.File, intrinsics: Intrinsics):
        self._intrinsics = intrinsics
        self._file: h5py.File = file

    @property
    def top(self) -> Data:
        return Data(self._file, self._file["top"], self._intrinsics)

    @property
    def bottom(self) -> Data:
        return Data(self._file, self._file["bottom"], self._intrinsics)

    @property
    def left(self) -> Data:
        return Data(self._file, self._file["left"], self._intrinsics)

    @property
    def right(self) -> Data:
        return Data(self._file, self._file["right"], self._intrinsics)

    @property
    def front(self) -> Data:
        return Data(self._file, self._file["front"], self._intrinsics)

    @property
    def back(self) -> Data:
        return Data(self._file, self._file["back"], self._intrinsics)


class DataFile(ABC):
    def __init__(self, config):
        self._config = config

    @property
    @abstractmethod
    def filename(self) -> str:
        pass

    @property
    def download_file(self) -> Path:
        return self._config.download_location / self.filename

    @property
    def download_file_if_exists(self) -> Path:
        if not self.is_downloaded:
            raise ValueError(f"{self} is  not downloaded")

        return self._config.download_location / self.filename

    @property
    def remote_location(self) -> str:
        return self._config.remote_location + self.filename

    @property
    def is_downloaded(self) -> bool:
        return self.download_file.exists()

    @abstractmethod
    def download(self, force: bool = False) -> DataFile:
        pass

    @property
    @abstractmethod
    def intrinsics(self) -> Intrinsics:
        pass

    @property
    def remote_exists(self) -> bool:
        if self.is_downloaded:
            return True

        fs = s3fs.S3FileSystem()

        return fs.exists(self.remote_location)


    def _download(self, force: bool = False):
        if self.is_downloaded and not force:
            return

        if self.is_downloaded:
            self.download_file.unlink(missing_ok=True)

        fs = s3fs.S3FileSystem()
        fs.get(self.remote_location, str(self.download_file))


class PoseDataFile(DataFile):

    @property
    def filename(self) -> str:
        return "pose.hdf5"

    def download(self, force: bool = False) -> DataFile:
        self._download(force)
        return self

    @property
    def data(self) -> PoseData:
        return PoseData(h5py.File(self.download_file_if_exists, 'r'))

    def __enter__(self) -> PoseData:
        if not self.is_downloaded:
            raise ValueError(f"{self} is  not downloaded")

        return self.data

    def __exit__(self, exc_type, exc_val: Data, exc_tb):
        exc_val.close()


class CylindricalDataFile(DataFile, DataSource):

    def __init__(self, config):
        super().__init__(config)

    def __repr__(self):
        return f"CylindricalDataFile(config={self._config}, location={str(self.download_file)}, downloaded=" \
               f"{self.is_downloaded})"

    @property
    def filename(self) -> str:
        return "cylindrical.hdf5"

    @property
    def data(self) -> Data:
        file = h5py.File(self.download_file_if_exists, 'r')
        return Data(file, file, self.intrinsics)

    @property
    def intrinsics(self) -> CylindricalIntrinsics:
        return CylindricalIntrinsics()

    def download(self, force: bool = False) -> CylindricalDataFile:
        self._download(force)
        return self


class SphericalDataFile(DataFile, DataSource):
    def __init__(self, config):
        super().__init__(config)

    def __repr__(self):
        return f"SphericalDataFile(config={self._config}, location={str(self.download_file)}, down" \
               f"loaded={self.is_downloaded})"

    @property
    def filename(self) -> str:
        return "spherical.hdf5"

    @property
    def data(self) -> Data:
        file = h5py.File(self.download_file_if_exists, 'r')
        return Data(file, file, self.intrinsics)

    @property
    def intrinsics(self) -> SphericalIntrinsics:
        return SphericalIntrinsics()

    def download(self, force: bool = False) -> SphericalDataFile:
        self._download(force)
        return self


class PinholeDataFile(DataFile):

    def __init__(self, config):
        super().__init__(config)

    def __repr__(self):
        return f"PinholeDataFile(config={self._config}, location={str(self.download_file)}, down" \
               f"loaded={self.is_downloaded})"

    @property
    def filename(self) -> str:
        return "pinhole.hdf5"

    def __enter__(self) -> SplitData:
        if not self.is_downloaded:
            raise ValueError(f"{self} is  not downloaded")

        file = h5py.File(self.download_file_if_exists, 'r')
        return SplitData(file, self.intrinsics)

    def __exit__(self, exc_type, exc_val: SplitData, exc_tb):
        exc_val._file.close()

    @property
    def intrinsics(self) -> PinholeIntrinsics:
        return PinholeIntrinsics()

    @property
    def top(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "top")

    @property
    def bottom(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "bottom")

    @property
    def left(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "left")

    @property
    def right(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "right")

    @property
    def front(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "front")

    @property
    def back(self) -> PinholeDataFileSide:
        return PinholeDataFileSide(self, "back")

    def download(self, force: bool = False) -> PinholeDataFile:
        self._download(force)
        return self


@dataclass
class PinholeDataFileSide(DataSource):
    data_file: PinholeDataFile
    side: str

    @property
    def data(self) -> Data:
        file = h5py.File(self.data_file.download_file_if_exists, 'r')
        return Data(file, file[self.side])

    def download(self, force: bool = False) -> PinholeDataFileSide:
        self.data_file.download(force)
        return self

    def is_downloaded(self) -> bool:
        return self.data_file.is_downloaded
