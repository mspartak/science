
from fly import FlyClass
from owlears import OwlearsClass, MicCfgClass
from global_config import GlobalConfigtionClass
import numpy as np
import common_functions

class EnvClass():

    def __init__(self, EnvCfg):
        self.EnvCfg = EnvCfg

    def __calc_radial_velocity(self,X,Y,Xmic,Ymic,Azim,V):

        # Get rotation angle
        dX = X - Xmic
        dY = Y - Ymic
        a1 = np.arctan(dX / dY)
        rot_angle = 0.5 * np.pi - Azim + a1

        # Radial Velocity
        Vrad = V * np.cos(rot_angle)

        return Vrad


    def Process(self, FlyCfg: FlyClass, MicCfg: MicCfgClass, Cfg: GlobalConfigtionClass):

        # Calc Radial Velocity at point A
        VrA = self.__calc_radial_velocity(
            X=FlyCfg.X,
            Y=FlyCfg.Y,
            Xmic=MicCfg.X,
            Ymic=MicCfg.Y,
            Azim=FlyCfg.Azim,
            V=FlyCfg.V
        )

        # Calculate coordinates of point B.
        # After Tsample time
        xn, yn = common_functions.Move(
            X=FlyCfg.X,
            Y=FlyCfg.Y,
            Angle=FlyCfg.Azim,
            Distance=FlyCfg.V * Cfg.Tsampl
        )

        # Calc Radial Velocity at point B
        VrB = self.__calc_radial_velocity(
            X=xn,
            Y=yn,
            Xmic=MicCfg.X,
            Ymic=MicCfg.Y,
            Azim=FlyCfg.Azim,
            V=FlyCfg.V
        )

        # Frequency after Doppler effect impact
        fA = common_functions.Doppler_SineWave(
            Vsource=VrA,
            Vmedium=Cfg.EnvParams.SoundSpeed,
            f0=FlyCfg.Wave
        )
        fB = common_functions.Doppler_SineWave(
            Vsource=VrB,
            Vmedium=Cfg.EnvParams.SoundSpeed,
            f0=FlyCfg.Wave
        )

        report_text = f'''
        -------- Environment processing results: --------
        Radial velocity of point A: {VrA}
        Radial velocity of point B: {VrB}
        Sound frequency from point A: {fA}
        Sound frequency from point B: {fB}
        Point B (x={xn}, y={yn})
        -------- Environment processing (end) --------
        '''

        print(report_text)

        return fA, fB


