from collections import deque
from pathlib import Path
from typing import List, Union

import pandas

from carla_dataset.config import City, Config, Rain


def cars_for_city(city: City):
    """
    The number of cars used for a city (necessary as city sizes vary).
    :param city:
    :return:
    """
    if city is City.Town01:
        return 30
    elif city is City.Town02:
        return 10
    elif city is City.Town03:
        return 40
    elif city is City.Town04:
        return 30
    elif city is City.Town05:
        return 40
    else:
        raise ValueError


def all() -> List[Config]:
    """
    :return: All existing Configs
    """
    return expand_wildcards()


def expand_wildcards(city=None, rain=None, sunset=None, num_cars=None, num_peds=None, index=None) -> List[Config]:
    """
    Expands any wildcard (None) values to existing values.  Passing all Nones returns all existing configs,
    the same as all().
    :param city:
    :param rain:
    :param sunset:
    :param num_cars:
    :param num_peds:
    :param index:
    :return:
    """
    done = []
    waiting = deque([(city, rain, sunset, num_cars, num_peds, index),] )

    while len(waiting) > 0:
        item = waiting.popleft()

        if item[0] is None:  # city
            for c in list(City):
                waiting.append((c, item[1], item[2], item[3], item[4], item[5]))
        elif item[1] is None: # rain
            # for r in list(Rain):
            #     waiting.append((item[0], r, item[2], item[3], item[4], item[5]))
            waiting.append((item[0], Rain.Clear, item[2], item[3], item[4], item[5]))
        elif item[2] is None: # sunset
            waiting.append((item[0], item[1], False, item[3], item[4], item[5]))
            waiting.append((item[0], item[1], True, item[3], item[4], item[5]))
        elif item[3] is None: # cars
            waiting.append((item[0], item[1], item[2], cars_for_city(item[0]), item[4], item[5]))
        elif item[4] is None: # peds
            waiting.append((item[0], item[1], item[2], item[3], 200, item[5]))
        elif item[5] is None: # indices
            if item[0] is City.Town01: #TODO get rid of this eventually
                for i in range(4) if item[2] else range(10):
                    waiting.append((item[0], item[1], item[2], item[3], item[4], i))
            else:
                for i in range(2) if item[2] else range(5):
                    waiting.append((item[0], item[1], item[2], item[3], item[4], i))
        else:
            done.append(item)

    return [Config(item[0], item[1], item[2], item[3], item[4], item[5]) for item in done]


def load_df(df: pandas.DataFrame) -> List[Config]:
    """
    Loads a list of configs from a pandas data frame.  Both column names and values are non case sensitive.

    |  Expects columns (non case sensitive):
    |  city: the name of a City
    |  rain: the name of a Rain
    |  time: sunset or noon
    |  num_cars: an int
    |  num_peds: an int
    |  index: an int

    | All values can be * to fill in all existing values.

    :param df: The data frame to load from
    :return: A list of Configs
    """

    # df.columns = map(str.lower, df.columns)
    configs = []

    for row in df.itertuples(index=False):
        num_cars = None if row.num_cars == "*" else int(row.num_cars)
        num_peds = None if row.num_peds == "*" else int(row.num_peds)
        index = None if row.index == "*" else int(row.index)
        city_name = None if row.city == "*" else row.city.lower()

        if city_name is not None:
            for c in list(City):
                if c.name.lower() == city_name:
                    city = c
                    break
            else:
                raise ValueError(f"{city_name} is not a valid city")
        else:
            city = None

        rain_name = None if row.rain == "*" else row.rain.lower()

        if rain_name is not None:
            for r in list(Rain):
                if r.name.lower() == rain_name:
                    rain = r
                    break
            else:
                raise ValueError(f"{rain_name} is not a valid rain")
        else:
            rain = None

        sunset_name = None if row.time == "*" else row.time.lower()
        if sunset_name is None:
            sunset = None
        elif sunset_name == "sunset":
            sunset = True
        elif sunset_name == "noon":
            sunset = False
        else:
            raise ValueError(f"{sunset_name} is not a valid time")

        configs.extend(expand_wildcards(city, rain, sunset, num_cars, num_peds, index))

    return configs


def load_txt(file: Union[Path, str]) -> List[Config]:
    """
    Loads a list of configs from a space-delimited text file.  Both column datas are non case sensitive.

    |  Expects columns (non case sensitive):
    |  city: the name of a City
    |  rain: the name of a Rain
    |  time: sunset or noon
    |  num_cars: an int
    |  num_peds: an int
    |  index: an int


    :param file: The file to read from
    :return: A list of Configs
    """

    if not isinstance(file, Path):
        file = Path(file)

    return load_df(pandas.read_csv(file, delim_whitespace=True))


def load_csv(file: Union[Path, str]) -> List[Config]:
    """
    Loads a list of configs from a comma delimited file.  Both column datas are non case sensitive.

    |  Expects columns (non case sensitive):
    |  city: the name of a City
    |  rain: the name of a Rain
    |  time: sunset or noon
    |  num_cars: an int
    |  num_peds: an int
    |  index: an int


    :param file: The file to read from
    :return: A list of Configs
    """

    if not isinstance(file, Path):
        file = Path(file)

    return load_df(pandas.read_csv(file))
