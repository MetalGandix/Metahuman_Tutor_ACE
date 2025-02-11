// Copyright Epic Games, Inc. All Rights Reserved.

using System.IO;
using UnrealBuildTool;

public class MetaHumanFootageIngest : ModuleRules
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

	public MetaHumanFootageIngest(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"LiveLink",
			"LiveLinkInterface"
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Slate",
			"SlateCore",
			"CoreUObject",
			"Engine",
			"UnrealEd",
			"InputCore",
			"MetaHumanCore",
			"ToolMenus",
			"ToolWidgets",
			"EditorStyle",
			"Projects",
			"PropertyEditor",
			"ImgMedia",
			"Json",
			"Sockets",
			"Networking",
			"GeometryCore",
			"GeometryFramework",
			"MeshDescription",
			"StaticMeshDescription",
			"OSC",
			"MetaHumanCaptureSource",
			"MetaHumanCaptureData",
			"WorkspaceMenuStructure"
		});
	}
}