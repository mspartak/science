import numpy as np

class EnvironmentParametersClass():

    def __init__(self, SoundSpeed):
        self.SoundSpeed = SoundSpeed

class GlobalConfigtionClass():

    def __init__(self):
        self.FlyCfg = {
            "X": 5,     # m
            "Y": 10,     # m
            "V": 1,      # m/s
            "Azim": 0,   # degrees
            "Wave": 500  # Hz
        }
        self.FlyCfg["Azim"] = np.deg2rad(self.FlyCfg["Azim"])

        self.Mic1Cfg = {
            "X": 0,   # m
            "Y": 0,   # m
        }

        self.Mic2Cfg = {
            "X": 10,   # m
            "Y": 0,    # m
        }

        self.Tsampl = 2  # s

        self.EnvParams = EnvironmentParametersClass(
            SoundSpeed=340  # m/s
        )