
import numpy as np

def RotateVector(x,y,angle):
    xn = x * np.cos(angle) - y * np.sin(angle)
    yn = x * np.sin(angle) + y * np.cos(angle)

    return xn, yn

def Move(X,Y,Angle, Distance):
    xn = X + Distance * np.cos(Angle)
    yn = Y - Distance * np.sin(Angle)

    return xn, yn

def Doppler_SineWave(Vsource, Vmedium, f0):
    fd = f0 * Vmedium / (Vmedium - Vsource)

    return fd