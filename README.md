
# CPDD-Dataset

This is the data access package for the CARLA panoramaic depth detection dataset,
created and published as part of my thesis *Dataset and Evaluation of Self-Supervised Learning for Panoramic Depth Estimation*

The code used to generate the dataset is available at https://github.com/rnett/CARLASim.

## Example

Set the environment variable `CARLA_DOWNLOAD_LOCATION` to wherever you want to keep the data.

Then, loading the data is as simple as:

```python
import cpdd_dataset

train_configs = cpdd_dataset.config.load_csv("train_data.csv")
train_data = []

for config in train_configs:
    with config.cylindrical_data.download() as data:
        train_data.append({"color": data.color, "depth": data.depth})
```

You can make a csv file structured like:
```csv
city,rain,time,num_cars,num_peds,index
Town01,Clear,Noon,*,*,2
```
and load it in a single line: `carla_dataset.data.load_csv("train.csv")`.

If you need camera intrinsics, `CylindricalIntrinsics`, `SphericalIntrinsics`, `PinholeIntrinsics`, and `Pinhole90Intrinsics` (see Utilities) classes are available in `data`, and provide the intrinsics values and matrix.

```python
K = CylindricalIntrinsics().K
```


## Structure

### Data Location
To set the dataset download/loading location, you can use `data.set_download_location`, and `get_download_location` to get it.
However, this is not advised.
Instead, set the environment variable `CARLA_DOWNLOAD_LOCATION`.
The above methods are simply wrappers around it.
It is loaded using `pathlib.Path`, so use whatever path format your machine does.

### Config

Each simulation run is represented by a `config.Config` object, which contains the simulation parameters 
(city, rain, number of pedestrians, etc) necessary to get the location of the data files.
It provides utility methods and properties based on this, including getting data files for pinhole, cylindrical, 
spherical, and pose data, getting the local and remote locations, and downloading all of the data files.

#### Loading

A `Config` can be constructed manually or from the folder name (using `Config.from_folder_name`), 
but will probably be loaded from `config.expand_wildcards`.
`expand_wildcards` fills `None` parameters will all valid values.
You probably don't need to use it directly, as loader methods `load_df`, `load_csv`, and `load_text` methods are provided, as well as `all`.

### Data Files

Data files can be gotten from `Config` objects, and represent a data file.
They have `download` methods that accept a `force` parameter, an `is_downloaded()` method, and a `data` property.
Non-pose data files also have an `intrinsics` property to get the associated intrinsics (described later).
The `data` property opens and loads the file, returning a `DataFile`.
`DataFile`s also work with Python's `with` blocks, and can be used like `with file as data:`.
This has the advantage of automatically closing the file. 
The pinhole data file also exposes side methods `top`, `bottom`, etc. to get individual sides'
groups within the pinhole data file, and a `__getitem__` operator that takes a `data.Side` to do the same.

### Data

The data objects gotten from data files expose the ndarray data for the training run.
Pinhole data (gotten from pinhole data files) has properties to get the data for each side.
Pinhole side data (gotten from side data files), cylindrical data, and spherical data have `rgb` and `depth` properties
that return their respective data as `numpy` `ndarray`s.
Both are of shape `[batch, height, width, channels]`, where color images have 3 channels (RGB) and depth images have 1.
Depth images are `uint16` and have the depth in decimeters, while color images are the standard `uint8`.
Pinhole images are 768x768, while cylindrical and spherical images are 2048x1024 (width x height).


Pose data objects have fields `absolute_pose`, `relative_pose`, and `start_relative_pose`.
Relative pose is relative to the last pose value, while start relative pose is relative to the inital post of that simulation.
Pose data is shape `[batch, 6]`, where the 6 values are `[X, Y, Z, x, y, z]` where `[X, Y, Z]` is the position in meters, and `[x, y, z]` is the unit heading vector of the car.

### Intrinsics
`CylindricalIntrinsics`, `SphericalIntrinsics`, `PinholeIntrinsics`, and `Pinhole90Intrinsics` (see Utilities) are available in `data`, and provide the intrinsics values and matrix.
Each object has `K`, `normalized_K`, `height`, `width`, `f_x`, `f_y`, `c_x`, `c_y`, and `fov` (degrees) fields.

### Utilities

A method `data.crop_pinhole_to_90` is provided to crop the 100 degree FOV pinhole images into 90 degree FOV images of the same size.
It uses `cv2.getRectSubPix` internally.
The intrinsics for these images are provided by `Pinhole90Intrinsics` using the same format as other intrinsics.
