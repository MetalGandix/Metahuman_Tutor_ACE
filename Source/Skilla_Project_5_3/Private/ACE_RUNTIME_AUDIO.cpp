//#include "ACE_RUNTIME_AUDIO.h"
//#include "ACERuntimeModule.h"
//#include "Sound/SoundWave.h"
//#include "ACETypes.h"
//
//UACE_RUNTIME_AUDIO::UACE_RUNTIME_AUDIO()
//{
//}
//
//UACE_RUNTIME_AUDIO::~UACE_RUNTIME_AUDIO()
//{
//}
//
//bool UACE_RUNTIME_AUDIO::AnimateFromAudioSamplesFloat(IACEAnimDataConsumer* Consumer, TArray<float> SamplesFloat,
//    int32 NumChannels, int32 SampleRate, bool bEndOfSamples, FAudio2FaceEmotion EmotionParameters,
//    UAudio2FaceParameters* Audio2FaceParameters)
//{
//    return FACERuntimeModule::Get().AnimateFromAudioSamples(Consumer, TArrayView<const float>(SamplesFloat), NumChannels,
//        SampleRate, bEndOfSamples, EmotionParameters, Audio2FaceParameters);
//}
//
//bool UACE_RUNTIME_AUDIO::AnimateFromAudioSamplesInt16(IACEAnimDataConsumer* Consumer, TArray<int16> SamplesInt16,
//    int32 NumChannels, int32 SampleRate, bool bEndOfSamples, FAudio2FaceEmotion EmotionParameters,
//    UAudio2FaceParameters* Audio2FaceParameters)
//{
//    return FACERuntimeModule::Get().AnimateFromAudioSamples(Consumer, TArrayView<const int16>(SamplesInt16), NumChannels,
//        SampleRate, bEndOfSamples, EmotionParameters, Audio2FaceParameters);
//}
//
//bool UACE_RUNTIME_AUDIO::EndAudioSamples(IACEAnimDataConsumer* Consumer)
//{
//    return FACERuntimeModule::Get().EndAudioSamples(Consumer);
//}
//
//bool UACE_RUNTIME_AUDIO::AnimateFromSoundWave(IACEAnimDataConsumer* Consumer, USoundWave* SoundWave,
//    FAudio2FaceEmotion EmotionParameters, UAudio2FaceParameters* Audio2FaceParameters)
//{
//    if (!SoundWave || !Consumer)
//    {
//        UE_LOG(LogTemp, Error, TEXT("SoundWave or Consumer is null."));
//        return false;
//    }
//
//    const int32 NumChannels = SoundWave->NumChannels;
//    const int32 SampleRate = SoundWave->GetSampleRateForCurrentPlatform();
//
//    if (NumChannels <= 0 || SampleRate <= 0)
//    {
//        UE_LOG(LogTemp, Error, TEXT("Invalid SoundWave properties: NumChannels = %d, SampleRate = %d"), NumChannels, SampleRate);
//        return false;
//    }
//
//    TArray<float> AudioSamples;
//
//    if (!SoundWave->GetResourceData(AudioSamples))
//    {
//        UE_LOG(LogTemp, Error, TEXT("Failed to retrieve audio samples from SoundWave."));
//        return false;
//    }
//
//    return FACERuntimeModule::Get().AnimateFromAudioSamples(Consumer, TArrayView<const float>(AudioSamples), NumChannels,
//        SampleRate, true, EmotionParameters, Audio2FaceParameters);
//}
