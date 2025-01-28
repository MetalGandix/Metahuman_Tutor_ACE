#pragma once

#include "CoreMinimal.h"
#include "Sound/SoundWave.h"
#include "UObject/Object.h"
#include "GetSoundFromName.generated.h"

UCLASS()
class SKILLA_PROJECT_5_3_API UGetSoundFromName : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Audio")
    static USoundWave* GetSoundWaveFromPath(const FString& FilePath);
};
