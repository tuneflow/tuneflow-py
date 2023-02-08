from math import exp

def dbToVolumeValue(db: float):
  return  exp((db - 6) * (1 / 20)) if db > -100 else 0