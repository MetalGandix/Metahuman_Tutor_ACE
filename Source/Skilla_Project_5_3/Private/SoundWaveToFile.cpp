#include "SoundWaveToFile.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFilemanager.h"
#include "Serialization/MemoryWriter.h"

USoundWaveToFile::USoundWaveToFile()
{
}

bool USoundWaveToFile::ExportSoundWaveToWav(USoundWave* SoundWave, const FString& FilePath)
{
    if (!SoundWave)
    {
        UE_LOG(LogTemp, Error, TEXT("SoundWave is null."));
        return false;
    }

    // Assicurati che i dati PCM siano disponibili
    if (!SoundWave->RawPCMData || SoundWave->RawPCMDataSize <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("SoundWave does not contain Raw PCM data."));
        return false;
    }

    // Preparare i dati WAV (Header + PCM)
    TArray<uint8> WavData;

    // Funzione per scrivere l'header WAV
    auto WriteWavHeader = [](TArray<uint8>& Data, int32 SampleRate, int32 NumChannels, int32 BitsPerSample, int32 DataSize)
        {
            int32 ByteRate = SampleRate * NumChannels * BitsPerSample / 8;
            int16 BlockAlign = NumChannels * BitsPerSample / 8;

            // RIFF Chunk
            Data.Append((uint8*)"RIFF", 4);
            int32 ChunkSize = 36 + DataSize;
            Data.Append((uint8*)&ChunkSize, 4);
            Data.Append((uint8*)"WAVE", 4);

            // fmt Subchunk
            Data.Append((uint8*)"fmt ", 4);
            int32 Subchunk1Size = 16;
            Data.Append((uint8*)&Subchunk1Size, 4);
            int16 AudioFormat = 1; // PCM
            Data.Append((uint8*)&AudioFormat, 2);
            Data.Append((uint8*)&NumChannels, 2);
            Data.Append((uint8*)&SampleRate, 4);
            Data.Append((uint8*)&ByteRate, 4);
            Data.Append((uint8*)&BlockAlign, 2);
            Data.Append((uint8*)&BitsPerSample, 2);

            // data Subchunk
            Data.Append((uint8*)"data", 4);
            Data.Append((uint8*)&DataSize, 4);
        };

    int32 SampleRate = SoundWave->GetSampleRateForCurrentPlatform();
    int32 NumChannels = SoundWave->NumChannels;
    int32 BitsPerSample = 16; // Supponiamo 16-bit PCM

    // Scrivi l'header WAV
    WriteWavHeader(WavData, SampleRate, NumChannels, BitsPerSample, SoundWave->RawPCMDataSize);

    // Aggiungi i dati PCM
    WavData.Append(SoundWave->RawPCMData, SoundWave->RawPCMDataSize);

    // Assicurati che la directory esista
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
    FString Directory = FPaths::GetPath(FilePath);
    if (!PlatformFile.DirectoryExists(*Directory))
    {
        PlatformFile.CreateDirectoryTree(*Directory);
    }

    // Salva il file
    if (!FFileHelper::SaveArrayToFile(WavData, *FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to save WAV file: %s"), *FilePath);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("WAV file saved successfully: %s"), *FilePath);
    return true;
}
