

class MicCfgClass():

    def __init__(self, MicCfgDict):
        self.X = MicCfgDict["X"]
        self.Y = MicCfgDict["Y"]


class OwlearsClass():

    def __init__(self, Mic1Cfg, Mic2Cfg):
        self.Mic1 = MicCfgClass(Mic1Cfg)
        self.Mic2 = MicCfgClass(Mic2Cfg)