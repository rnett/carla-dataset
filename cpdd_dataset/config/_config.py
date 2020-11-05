from __future__ import annotations

from enum import Enum
from pathlib import Path

from ..data import CylindricalDataFile, PinholeDataFile, SphericalDataFile
from ..data import get_download_location
from ..data._run_data import PoseDataFile


class Rain(Enum):
    Clear = 1
    Cloudy = 2
    Wet = 3
    WetCloudy = 4
    Soft = 5
    Mid = 6
    Hard = 7


class Weather:
    def __init__(self, rain: Rain, sunset: bool = False):
        self.rain = rain
        self.sunset = sunset


class City(Enum):
    Town01 = 1
    Town02 = 2
    Town03 = 3
    Town04 = 4
    Town05 = 5

    @property
    def map(self) -> str:
        return f"/Game/Carla/Maps/{self.name}"


class Config:

    def __init__(self, city: City, rain: Rain, sunset: bool, num_cars: int, num_peds: int, index: int):

        self.num_peds = num_peds
        self.num_cars = num_cars
        self.sunset = sunset
        self.rain = rain
        self.city = city
        self.index = index
        self.weather = Weather(rain, sunset)

    def __repr__(self):
        return f"Config(city={self.city.name}, rain={self.rain.name}, sunset={self.sunset}, num_cars={self.num_cars}, num_peds={self.num_peds}, index={self.index})"

    @property
    def folder_name(self) -> str:
        if self.sunset:
            time = 'sunset'
        else:
            time = 'noon'

        return f"{self.city.name.lower()}/" \
               f"{self.rain.name.lower()}/{time}/cars_{self.num_cars}_peds_" \
               f"{self.num_peds}_index_{self.index}"

    @property
    def download_location(self) -> Path:
        return get_download_location() / self.folder_name

    @property
    def remote_location(self) -> str:
        return "s3://cscdatasets/jventu09/cpdd_dataset/" + self.folder_name + "/"

    @property
    def cylindrical_data(self) -> CylindricalDataFile:
        return CylindricalDataFile(self)

    @property
    def spherical_data(self) -> SphericalDataFile:
        return SphericalDataFile(self)

    @property
    def pinhole_data(self) -> PinholeDataFile:
        return PinholeDataFile(self)

    @property
    def pose_data(self) -> PoseDataFile:
        return PoseDataFile(self)

    def download_all(self, force: bool = False):
        self.pose_data.download(force)
        self.cylindrical_data.download(force)
        self.spherical_data.download(force)
        self.pinhole_data.download(force)

    @staticmethod
    def from_folder_name(name: str):
        """
        name should be like "[/]{town}/{rain}/{time}/{folder_name}[/]"
        """

        parts = name.strip('/').split('/')

        town_name = parts[0]

        town = None

        for t in list(City):
            if t.name.lower() == town_name.lower():
                town = t
                break

        if town is None:
            raise ValueError(f"No town found for name {parts[0]}")

        rain_name = parts[1]

        rain = None

        for t in list(Rain):
            if t.name.lower() == rain_name.lower():
                rain = t
                break

        if rain is None:
            raise ValueError(f"No rain setting found for name {parts[1]}")

        sunset = parts[2] == "sunset"

        folder_name = parts[3].split('_')
        cars = int(folder_name[1])
        peds = int(folder_name[3])

        if len(folder_name) > 5:
            index = int(folder_name[5])
        else:
            index = 0

        return Config(town, rain, sunset, cars, peds, index)
