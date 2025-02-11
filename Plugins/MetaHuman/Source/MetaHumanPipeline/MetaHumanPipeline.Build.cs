// Copyright Epic Games, Inc. All Rights Reserved.

using System.IO;
using UnrealBuildTool;

public class MetaHumanPipeline : ModuleRules
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

	public MetaHumanPipeline(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"Eigen",
			"MetaHumanCore",
			"MetaHumanSpeech2Face",
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
			"CoreUObject",
			"ModelingOperators",
			"NNE",
			"Engine",
			"Json",
			"MetaHumanMeshTracker",
			"GeometryCore",
			"Projects",
			"D3D12RHI",
			"DX12",
			"RHI",
			"RenderCore",
			"MetaHumanConfig",
			"MetaHumanFaceAnimationSolver",
		});
	}
}
