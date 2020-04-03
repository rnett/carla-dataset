from abc import ABC, abstractmethod
import numpy as np


class Intrinsics(ABC):

    @property
    @abstractmethod
    def f_x(self) -> np.float32:
        pass

    @property
    @abstractmethod
    def f_y(self) -> np.float32:
        pass

    @property
    @abstractmethod
    def c_x(self) -> np.float32:
        pass

    @property
    @abstractmethod
    def c_y(self) -> np.float32:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    def K(self) -> np.ndarray:
        return np.array([[self.f_x, 0, self.c_x, 0],
                         [0, self.f_y, self.c_y, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype='float32')

    @property
    def normalized_K(self):
        K = self.K
        K[0, :] /= self.width
        K[1, :] /= self.height
        return K



class CylindricalIntrinsics(Intrinsics):
    @property
    def height(self) -> int:
        return 1024

    @property
    def width(self) -> int:
        return 2048

    @property
    def f_x(self) -> np.float32:
        return np.float32(325.949323452201668)

    @property
    def c_x(self) -> np.float32:
        return np.float32(1024.000000000000000)

    @property
    def f_y(self) -> np.float32:
        return np.float32(1023.000000000000000)

    @property
    def c_y(self) -> np.float32:
        return np.float32(511.500000000000000)


class SphericalIntrinsics(Intrinsics):
    @property
    def height(self) -> int:
        return 1024

    @property
    def width(self) -> int:
        return 2048

    @property
    def f_x(self) -> np.float32:
        return np.float32(325.949323452201668)

    @property
    def c_x(self) -> np.float32:
        return np.float32(1024.000000000000000)

    @property
    def f_y(self) -> np.float32:
        return np.float32(325.949323452201668)

    @property
    def c_y(self) -> np.float32:
        return np.float32(512.000000000000000)


class PinholeIntrinsics(Intrinsics):
    @property
    def f_x(self) -> np.float32:
        return np.float32(322.2142583720755)

    @property
    def f_y(self) -> np.float32:
        return np.float32(322.2142583720755)

    @property
    def c_x(self) -> np.float32:
        return np.float32(384.0)

    @property
    def c_y(self) -> np.float32:
        return np.float32(384.0)

    @property
    def height(self) -> int:
        return 768

    @property
    def width(self) -> int:
        return 768

    @property
    def fov(self) -> int:
        return 100


class Pinhole90Intrinsics(Intrinsics):
    @property
    def f_x(self) -> np.float32:
        return np.float32(384.0)

    @property
    def f_y(self) -> np.float32:
        return np.float32(384.0)

    @property
    def c_x(self) -> np.float32:
        return np.float32(384.0)

    @property
    def c_y(self) -> np.float32:
        return np.float32(384.0)

    @property
    def height(self) -> int:
        return 768

    @property
    def width(self) -> int:
        return 768

    @property
    def fov(self) -> int:
        return 90
