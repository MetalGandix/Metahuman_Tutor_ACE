// Copyright Epic Games, Inc. All Rights Reserved.

using System.IO;
using UnrealBuildTool;

public class MetaHumanImageViewer : ModuleRules
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

	public MetaHumanImageViewer(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PrivateDefinitions.AddRange(new string[]
		{
			// We depend on OpenCVHelpers but don't actually use functions that depend on OpenCV itself so
			// this needs to be defined as OpenCVHelper depends on this definition to compile
			"WITH_OPENCV=0"
		});

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"EditorStyle",
			"SlateCore",
			"MediaAssets",
			"ProceduralMeshComponent",

			"MetaHumanCore",
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
			"CoreUObject",
			"Engine",
			"Slate",
			"InputCore",
			"EditorStyle",
			"UnrealEd",
			"OpenCVHelper",

			"MetaHumanCoreEditor",
			"MetaHumanMeshTracker",
		});
	}
}