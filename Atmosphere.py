kSpeedOfSoundSeaLevel = 661.47
kSpeedOfSoundStratosphere = 573.6076655357
kTropopause = 36089.0

def speedOfSound(altitude):
    if altitude <= kTropopause:
        gradient = (kSpeedOfSoundSeaLevel - 
                    kSpeedOfSoundStratosphere) / kTropopause
        return kSpeedOfSoundSeaLevel - gradient * altitude
    else:
        return kSpeedOfSoundStratosphere
