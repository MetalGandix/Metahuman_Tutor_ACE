// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class MetaHumanMeshTracker : ModuleRules
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

	public MetaHumanMeshTracker(ReadOnlyTargetRules Target) : base(Target)
	{
		bUsePrecompiled = !BuildForDevelopment;
		IWYUSupport = IWYUSupport.None;
		bEnableUndefinedIdentifierWarnings = false;
		ShadowVariableWarningLevel = WarningLevel.Warning;
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		bUseUnity = false;
		PrivatePCHHeaderFile = "Private/MetaHumanMeshTrackerPrivatePCH.h";

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
			"Vulkan",
			"Eigen",
			"RigLogicLib",
			"RigLogicModule"
		});


		PrivateDependencyModuleNames.AddRange(new string[] {
			"MetaHumanCore",
		});

		if (Target.Type == TargetType.Editor)
		{
			PrivateDependencyModuleNames.Add("UnrealEd");
		}

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true

		PrivateIncludePaths.AddRange(new string[]
		{
			Path.Combine(ModuleDirectory, "../ThirdParty/dlib/Include"),
			Path.Combine(ModuleDirectory, "Private/carbon/include"),
			Path.Combine(ModuleDirectory, "Private/nls/include"),
			Path.Combine(ModuleDirectory, "Private/nrr/include"),
			Path.Combine(ModuleDirectory, "Private/reconstruction/include"),
			Path.Combine(ModuleDirectory, "Private/tracking/include"),
			Path.Combine(ModuleDirectory, "Private/vulkantools/include"),
			Path.Combine(ModuleDirectory, "Private/Thirdparty/optflow/include"),
			Path.Combine(ModuleDirectory, "Private/conformer/include"),
			Path.Combine(ModuleDirectory, "Private/ThirdParty/dlib_modifications"),
			Path.Combine(ModuleDirectory, "Private/predictivesolver/include"),
			Path.Combine(ModuleDirectory, "Private/rigmorpher/include"),
			Path.Combine(ModuleDirectory, "Private/api"),
			Path.Combine(ModuleDirectory, "Private/rlibv/include"),
			Path.Combine(ModuleDirectory, "Private/rlibv/include/ThirdParty/dlib")
		});

		// cpp17 for tracking code
		CppStandard = CppStandardVersion.Cpp17;
		MinCpuArchX64 = MinimumCpuArchitectureX64.AVX;
		PrivateDefinitions.Add("TITAN_DYNAMIC_API");
		PrivateDefinitions.Add("LOG_INTEGRATION");
		PrivateDefinitions.Add("WITH_VMA");

		if (Target.Platform == UnrealTargetPlatform.Win64 ||
			Target.Platform == UnrealTargetPlatform.Linux ||
			Target.Platform == UnrealTargetPlatform.Mac)
		{
			PrivateDefinitions.Add("CARBON_ENABLE_SSE=1");
			PrivateDefinitions.Add("CARBON_ENABLE_AVX=1");
		}

		// This module uses exceptions in the core tech libs, so they must be enabled here
		bEnableExceptions = true;

		PublicAdditionalLibraries.AddRange(new string[]
		{
			"$(ModuleDir)/../ThirdParty/dlib/Lib/Win64/Release/dlib19.23.0_release_64bit_msvc1929.lib"
		});
		// Need to disable unity builds for this module to avoid clang compilation issues with the TEXT macro
		//bUseUnity = false;
	}
}
