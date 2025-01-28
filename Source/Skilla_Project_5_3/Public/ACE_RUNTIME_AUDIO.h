//#pragma once
//
//#include "CoreMinimal.h"
//#include "ACERuntimeModule.h"
//#include "ACE_RUNTIME_AUDIO.generated.h"
//
//class IACEAnimDataConsumer;
//class UAudio2FaceParameters;
//class USoundWave;
//struct FAudio2FaceEmotion;
//
//UCLASS(Blueprintable, ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
//class SKILLA_PROJECT_5_3_API UACE_RUNTIME_AUDIO : public UObject
//{
//    GENERATED_BODY()
//
//public:
//    UACE_RUNTIME_AUDIO();
//    virtual ~UACE_RUNTIME_AUDIO();
//
//    // API to animate from float audio samples
//    UFUNCTION(BlueprintCallable, Category = "ACE|Audio Animation")
//    bool AnimateFromAudioSamplesFloat(IACEAnimDataConsumer* Consumer, TArray<float> SamplesFloat, int32 NumChannels,
//        int32 SampleRate, bool bEndOfSamples, FAudio2FaceEmotion EmotionParameters, UAudio2FaceParameters* Audio2FaceParameters);
//
//    // API to animate from int16 PCM audio samples
//    UFUNCTION(BlueprintCallable, Category = "ACE|Audio Animation")
//    bool AnimateFromAudioSamplesInt16(IACEAnimDataConsumer* Consumer, TArray<int16> SamplesInt16, int32 NumChannels,
//        int32 SampleRate, bool bEndOfSamples, FAudio2FaceEmotion EmotionParameters, UAudio2FaceParameters* Audio2FaceParameters);
//
//    // API to indicate the end of an audio stream
//    UFUNCTION(BlueprintCallable, Category = "ACE|Audio Animation")
//    bool EndAudioSamples(IACEAnimDataConsumer* Consumer);
//
//    // API to animate from a Sound Wave
//    UFUNCTION(BlueprintCallable, Category = "ACE|Audio Animation")
//    bool AnimateFromSoundWave(IACEAnimDataConsumer* Consumer, USoundWave* SoundWave, FAudio2FaceEmotion EmotionParameters, UAudio2FaceParameters* Audio2FaceParameters);
//};
