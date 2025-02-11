# Copyright Epic Games, Inc. All Rights Reserved.

import unreal
import argparse
import sys


def create_performance_asset(path_to_identity : str, path_to_capture_data : str, save_performance_location : str) -> unreal.MetaHumanPerformance:
    """
    Returns a newly craeted MetaHuman Performance asset based on the input identity and capture data. 
    
    Args
        path_to_identity: content path to an existing MH Identity asset that is going to be used by the performance
        path_to_capture_data: content path to the capture data used to do the processing in performance
        save_performance_location: content path to store the new performance
    """
    capture_data_asset = unreal.load_asset(path_to_capture_data)
    identity_asset = unreal.load_asset(path_to_identity)
    performance_asset_name = "{0}_Performance".format(capture_data_asset.get_name())

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    performance_asset = asset_tools.create_asset(asset_name=performance_asset_name, package_path=save_performance_location, 
                                                 asset_class=unreal.MetaHumanPerformance, factory=unreal.MetaHumanPerformanceFactoryNew())

    # Use this style as set_editor_property doesn't trigger the PostEditChangeProperty required to setup the Performance asset
    performance_asset.set_editor_property("identity", identity_asset)
    performance_asset.set_editor_property("footage_capture_data", capture_data_asset)

    return performance_asset


def process_shot(performance_asset : unreal.MetaHumanPerformance, export_level_sequence : bool, export_sequence_location : str,
                 path_to_meta_human_target : str, start_frame : int = None, end_frame : int = None):
    """
    Process the input performance and optionally export the processed range of frames as an AnimSequence asset.

    Args
        performance_asset: the performance to process
        export_level_sequence: whether to export the processed shot
        export_sequence_location: content path for the exported animation sequence
        path_to_meta_human_target: content path for the MetaHuman SkelMesh to 
        start_frame, end_frame: set start/end frame property to change the processing range, the default range is set to entire shot
                                when modifying the range make sure start and end frames are vaild and not overlaping
                                upper limit frame will not be processed, so for limit of 10, frames 1-9 will be processed 
    """
    if start_frame is not None:
        performance_asset.set_editor_property("start_frame_to_process", start_frame)

    if end_frame is not None:
        performance_asset.set_editor_property("end_frame_to_process", end_frame)

    #Setting process to blocking will make sure the action is executed on the main thread, blocking it until processing is finished
    process_blocking = True
    performance_asset.set_blocking_processing(process_blocking)

    # Register a callback that is called after the shot was processed
    def shot_processing_finished():
        unreal.log("Finished processing shot for Performance '{0}'".format(performance_asset.get_name()))
        performance_asset.on_processing_finished_dynamic.remove_callable(shot_processing_finished)

        if export_level_sequence is True:
            run_level_sequence_export(performance_asset, export_sequence_location, path_to_meta_human_target)

    # Register a callback for when the pipeline finishes running
    performance_asset.on_processing_finished_dynamic.add_callable(shot_processing_finished)

    unreal.log("Starting MH pipeline for '{0}'".format(performance_asset.get_name()))
    startPipelineError = performance_asset.start_pipeline()
    if startPipelineError is unreal.StartPipelineErrorType.NONE:
        unreal.log("Finished MH pipeline for '{0}'".format(performance_asset.get_name()))
    elif startPipelineError is unreal.StartPipelineErrorType.TOO_MANY_FRAMES:
        unreal.log("Too many frames when starting MH pipeline for '{0}'".format(performance_asset.get_name()))
    else:
        unreal.log("Unknown error starting MH pipeline for '{0}'".format(performance_asset.get_name()))


def run_level_sequence_export(performance_asset : unreal.MetaHumanPerformance, export_sequence_location : str, path_to_target_meta_human : str = ''):
    """
    Creates an Anim Sequence asset from the processed range of the input performance.
    Returns the newly created asset.
    NOTE: Export Level Sequence is currently not supported in unattended mode.

    Args
        performance_asset: performance with a processed range of frames to generate the sequence from
        export_sequence_location: content path for the new sequence asset
        path_to_target_meta_human: content path to MetaHuman SkelMesh to apply the anim sequence
    """
    performance_asset_name = performance_asset.get_name()
    unreal.log("Exporting animation sequence for Performance '{0}'".format(performance_asset_name))

    export_settings = unreal.MetaHumanPerformanceExportAnimationSettings()
    # Enable to export the head rotation as curve data
    export_settings.enable_head_movement = True
    # This hides the dialog where the user can select the path to write the anim sequence
    export_settings.show_export_dialog = False
    # Use name_prefix to set a prefix to be added to the anim sequence name
    # Use export_range to select the whole sequence or only the processing range
    export_settings.export_range = unreal.PerformanceExportRange.PROCESSING_RANGE
    # Export the animation sequence from the performance using the given settings
    anim_sequence: unreal.AnimSequence = unreal.MetaHumanPerformanceExportUtils.export_animation_sequence(performance_asset, export_settings)
    unreal.log("Exported Anim Sequence {0}".format(anim_sequence.get_name()))

    unreal.log("Exporting level sequence for performance '{0}'".format(performance_asset_name))
    level_sequence_export_settings = unreal.MetaHumanPerformanceExportLevelSequenceSettings()
    level_sequence_export_settings.show_export_dialog = False
    # if the path and name are not set, will use the performance as a base name
    level_sequence_export_settings.package_path = export_sequence_location
    level_sequence_export_settings.asset_name = "LevelSequence_{0}".format(performance_asset_name)

    # customize various export settings
    level_sequence_export_settings.export_video_track = True
    level_sequence_export_settings.export_depth_track = False
    level_sequence_export_settings.export_audio_track = True
    level_sequence_export_settings.export_image_plane = True
    level_sequence_export_settings.export_camera = True
    level_sequence_export_settings.export_identity = True
    level_sequence_export_settings.enable_meta_human_head_movement = True
    level_sequence_export_settings.export_control_rig_track = True
    level_sequence_export_settings.export_transform_track = False
    level_sequence_export_settings.export_range = unreal.PerformanceExportRange.WHOLE_SEQUENCE
    level_sequence_export_settings.enable_meta_human_head_movement = True

    # Set a MetaHuman blueprint to target when exporting the Level Sequence
    if len(path_to_target_meta_human) != 0 :
        target_MetaHuman_BP_asset: unreal.Blueprint = unreal.load_asset(path_to_target_meta_human)
        level_sequence_export_settings.target_meta_human_class = target_MetaHuman_BP_asset.generated_class()

    exported_level_sequence: unreal.LevelSequence = unreal.MetaHumanPerformanceExportUtils.export_level_sequence(performance=performance_asset, export_settings=level_sequence_export_settings)
    unreal.log("Exported Level Sequence {0}".format(exported_level_sequence.get_name()))

    return exported_level_sequence


def run():
    """Main function to run for this module"""
    parser = argparse.ArgumentParser(prog=sys.argv[0], description=
        'This scirpt is used to create a MetaHuman Performance asset and process a shot '
        'level sequence export is currently not supported in headless mode and in oredr for this '
        'script to work, valid capture data asset and an identity that has been prepared for '
        'Performance have to be provided')
    parser.add_argument("--identity-path", type=str, required=True, help="Content path to identity asset to be used by the performance one")
    parser.add_argument("--capture-data-path", type=str, required=True, help="Content path to capture data asset to be used by the performance one")
    parser.add_argument("--storage-path", type=str, default='/Game/', help="Content path where the assets should be stored, e.g. /Game/MHA-Data/")

    # Optional command line arguments for exporting the processed animation 
    parser.add_argument("--export-level-sequence", action="store_true", default=False, required=False, help="An optional parameter to enable level sequence export")
    parser.add_argument("--target-MetaHuman-path", type=str, required=False, help="An optional path to MetaHuman BP asset to target during the level sequence export")
    parser.add_argument("--start-frame", type=int, required=False, help="Set starting frame for performance processing")
    parser.add_argument("--end-frame", type=int, required=False, help="Set ending frame up to which the performance will be processed. Note Processing range is N-1")

    args = parser.parse_args()

    # the following params need to extra handling for default values
    target_meta_human_path = '' if args.target_MetaHuman_path is None else args.target_MetaHuman_path
    processing_start_frame = None
    processing_end_frame = None
    if args.start_frame is not None:
        processing_start_frame = args.start_frame
    if args.end_frame is not None:
        processing_end_frame = args.end_frame

    performance_asset = create_performance_asset(
        path_to_identity=args.identity_path,
        path_to_capture_data=args.capture_data_path,
        save_performance_location=args.storage_path)
    process_shot(
        performance_asset=performance_asset,
        export_level_sequence=args.export_level_sequence,
        export_sequence_location=args.storage_path,
        path_to_meta_human_target=target_meta_human_path,
        start_frame=processing_start_frame,
        end_frame=processing_end_frame)


if __name__ == "__main__":
    run()
