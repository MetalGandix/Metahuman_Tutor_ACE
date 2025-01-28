#include "GetSoundFromName.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFilemanager.h"
#include "Sound/SoundWave.h"
#include "AudioDecompress.h"
#include "AudioDevice.h"

USoundWave* UGetSoundFromName::GetSoundWaveFromPath(const FString& FilePath)
{
    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogTemp, Warning, TEXT("File does not exist: %s"), *FilePath);
        return nullptr;
    }

    TArray<uint8> RawFileData;
    if (!FFileHelper::LoadFileToArray(RawFileData, *FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load file: %s"), *FilePath);
        return nullptr;
    }

    USoundWave* SoundWave = NewObject<USoundWave>(USoundWave::StaticClass());
    if (!SoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create SoundWave object"));
        return nullptr;
    }

    FWaveModInfo WaveInfo;
    if (!WaveInfo.ReadWaveInfo(RawFileData.GetData(), RawFileData.Num()))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to read wave info"));
        return nullptr;
    }

    SoundWave->InvalidateCompressedData();
    SoundWave->RawPCMDataSize = WaveInfo.SampleDataSize;
    SoundWave->RawPCMData = static_cast<uint8*>(FMemory::Malloc(WaveInfo.SampleDataSize));
    FMemory::Memcpy(SoundWave->RawPCMData, WaveInfo.SampleDataStart, WaveInfo.SampleDataSize);

    int32 DurationDiv = *WaveInfo.pChannels * (*WaveInfo.pBitsPerSample / 8) * *WaveInfo.pSamplesPerSec;
    if (DurationDiv > 0)
    {
        SoundWave->Duration = static_cast<float>(*WaveInfo.pWaveDataSize * 8.0f / DurationDiv);
    }
    else
    {
        SoundWave->Duration = 0.0f;
    }

    SoundWave->SetSampleRate(*WaveInfo.pSamplesPerSec);
    SoundWave->NumChannels = *WaveInfo.pChannels;
    SoundWave->SoundGroup = SOUNDGROUP_Default;

    return SoundWave;
}
