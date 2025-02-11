// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class MetaHumanIdentity : ModuleRules
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

	public MetaHumanIdentity(ReadOnlyTargetRules Target) : base(Target)
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
			"CoreUObject",
			"Engine",
			"SlateCore",
			"GeometryFramework",
			"MetaHumanCore",
			"MetaHumanMeshTracker",
			"MetaHumanCaptureData",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"OpenCVHelper",
			"ImgMedia",
			"GeometryCore",
			"RigLogicModule",
			"MeshConversion",
			"MeshDescription",
			"StaticMeshDescription",
			"Projects",
			"Json",
			"JsonUtilities",
			"MetaHumanFaceContourTracker",
			"MetaHumanFaceFittingSolver",
			"MetaHumanFaceAnimationSolver",
			"MetaHumanConfig",
			"MetaHumanPipeline",
			"MetaHumanCaptureData",
			"AutoRigService",
			"CameraCalibrationCore"
		});

		if (Target.Type == TargetType.Editor)
		{
			PrivateDependencyModuleNames.Add("UnrealEd");
			PrivateDependencyModuleNames.Add("SkeletalMeshUtilitiesCommon");
			PrivateDependencyModuleNames.Add("Slate");
		}
	}
}