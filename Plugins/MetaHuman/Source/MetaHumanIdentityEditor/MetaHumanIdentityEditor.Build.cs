// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class MetaHumanIdentityEditor : ModuleRules
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

	public MetaHumanIdentityEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{

		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"UnrealEd",
			"Projects",
			"Sequencer",
			"MediaAssets",
			"ImgMedia",
			"DesktopPlatform",
			"Slate",
			"SlateCore",
			"ToolMenus",
			"ToolWidgets",
			"MovieScene",
			"GeometryFramework",
			"AdvancedPreviewScene",
			"InputCore",
			"ControlRigDeveloper",
			"RigVMDeveloper",
			"RigLogicModule",
			"AnimGraph",
			"ControlRig",
			"AssetDefinition",
			"NNE",
			"ImageCore",
			"MetaHumanCore",
			"MetaHumanCoreEditor",
			"MetaHumanFaceContourTracker",
			"MetaHumanFaceFittingSolver",
			"MetaHumanMeshTracker",
			"MetaHumanImageViewer",
			"MetaHumanCaptureData",
			"MetaHumanCaptureDataEditor",
			"MetaHumanPipeline",
			"MetaHumanSequencer",
			"MetaHumanIdentity",
			"MetaHumanToolkit",
		});
	}
}