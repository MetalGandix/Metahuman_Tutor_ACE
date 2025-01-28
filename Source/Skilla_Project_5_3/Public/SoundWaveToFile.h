#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Sound/SoundWave.h"
#include "SoundWaveToFile.generated.h"

UCLASS()
class SKILLA_PROJECT_5_3_API USoundWaveToFile : public UObject
{
    GENERATED_BODY()

public:
    USoundWaveToFile();

    // Funzione per esportare un SoundWave in un file .wav
    UFUNCTION(BlueprintCallable, Category = "Audio")
    static bool ExportSoundWaveToWav(USoundWave* SoundWave, const FString& FilePath);
};
