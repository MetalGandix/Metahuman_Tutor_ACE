// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Sound/SoundWave.h"
#include "WaveAudioA2F.generated.h"

/**
 *
 */
UCLASS()
class SKILLA_PROJECT_5_3_API UWaveAudioA2F : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Audio")
    static USoundWave* SetSoundWaveLoadingBehavior(USoundWave* SoundWave);
};
