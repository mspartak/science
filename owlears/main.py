from fly import FlyClass
from env import EnvClass
from owlears import OwlearsClass
from visualizer import VisualizerClass
from analyzer   import AnalyserClass
from global_config import GlobalConfigtionClass

cfg   = GlobalConfigtionClass()
fly   = FlyClass(cfg.FlyCfg)
env1  = EnvClass(cfg.EnvParams)
env2  = EnvClass(cfg.EnvParams)
owl   = OwlearsClass(cfg.Mic1Cfg, cfg.Mic2Cfg)
visualizer = VisualizerClass([cfg.Mic1Cfg, cfg.Mic2Cfg])
analyser   = AnalyserClass()

# ===== execute ==========
print("======== Microphone 1 signal ========")
f1A, f1B = env1.Process(fly, owl.Mic1, cfg)
print("======== Microphone 2 signal ========")
f2A, f2B = env1.Process(fly, owl.Mic2, cfg)

