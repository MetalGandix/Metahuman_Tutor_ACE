// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class MetaHumanCore : ModuleRules
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

	public MetaHumanCore(ReadOnlyTargetRules Target) : base(Target)
	{
		// Imposta il modulo per essere precompilato per qualsiasi target
		PrecompileForTargets = PrecompileTargetsType.Any;

		bUsePrecompiled = true;

		// Specifica l'uso dei PCH
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// Dipendenze pubbliche
		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"LiveLinkInterface",
			"RigLogicLib",
			"RigLogicModule",
		});

		// Dipendenze private
		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Slate",
			"SlateCore",
			"Projects",
			"ImgMedia",
			"Json",
			"JsonUtilities",
			"OpenCVHelper",
			"CameraCalibrationCore",
			"RHI",
		});

		// Definizioni private
		PrivateDefinitions.Add("CORE_BUILD_SHARED");
		PrivateDefinitions.Add("WITH_OPENCV=0");
	}
}
