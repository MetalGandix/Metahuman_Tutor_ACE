// Copyright Epic Games, Inc. All Rights Reserved.

using System.IO;
using UnrealBuildTool;

public class MetaHumanPerformance : ModuleRules
{
	protected bool BuildForDevelopment
	{
		get
		{
			// Check if source is available
			string SourceFilesPath = Path.Combine(ModuleDirectory, "Private");
			return Directory.Exists(SourceFilesPath) &&
				   Directory.GetFiles(SourceFilesPath).Length > 0;
		}
	}

	public MetaHumanPerformance(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PrivateDefinitions.AddRange(new string[]
		{
			// We depend on OpenCVHelpers but don't actually use functions that depend on OpenCV itself so
			// this needs to be defined as OpenCVHelper depends on this definition to compile
			"WITH_OPENCV=0"
		});

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"Engine",
			"MetaHumanCaptureData",
			"MetaHumanPipeline",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"CoreUObject",
			"UnrealEd",
			"Slate",
			"SlateCore",
			"InputCore",
			"EditorFramework",
			"MovieSceneTools",
			"MediaCompositing",
			"MediaCompositingEditor",
			"CinematicCamera",
			"MediaAssets",
			"AnimationCore",
			"Sequencer",
			"LevelSequence",
			"LevelSequenceEditor",
			"MovieScene",
			"MovieSceneTracks",
			"ImgMedia",
			"ToolMenus",
			"ControlRig",
			"ControlRigDeveloper",
			"ControlRigEditor",
			"RigLogicModule",
			"RigVM",
			"RigVMDeveloper",
			"Projects",
			"PropertyEditor",
			"NNE",
			"InteractiveToolsFramework",
			"EditorInteractiveToolsFramework",
			"AdvancedPreviewScene",
			"AssetDefinition",
			"OpenCVHelper",
			"CameraCalibrationCore",
			"MetaHumanCore",
			"MetaHumanCoreEditor",
			"MetaHumanImageViewer",
			"MetaHumanIdentity",
			"MetaHumanIdentityEditor",
			"MetaHumanMeshTracker",
			"MetaHumanSequencer",
			"MetaHumanToolkit",
			"MetaHumanFaceContourTracker",
			"MetaHumanFaceAnimationSolver",
			"MetaHumanCaptureDataEditor",
		});
	}
}