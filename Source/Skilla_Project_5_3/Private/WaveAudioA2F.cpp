// Fill out your copyright notice in the Description page of Project Settings.

#include "../Public/WaveAudioA2F.h"

USoundWave* UWaveAudioA2F::SetSoundWaveLoadingBehavior(USoundWave* SoundWave)
{
    SoundWave->LoadingBehavior = ESoundWaveLoadingBehavior::ForceInline;
    return SoundWave;
}
