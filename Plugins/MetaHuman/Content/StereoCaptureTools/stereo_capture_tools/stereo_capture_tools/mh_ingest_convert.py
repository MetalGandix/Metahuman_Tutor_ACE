import argparse
import enum
import json
import math
import os
import re
import shutil
import subprocess
import sys
import uuid
from json import JSONDecodeError
from pathlib import Path
from typing import NamedTuple, List, Optional, Dict

import dateutil.parser as date_parser
# noinspection PyPackageRequirements
import ffmpeg
from pymediainfo import MediaInfo
from wavinfo import WavInfoReader

# We replicate the bundle version of the stereo capture tools here so that this script can be easily relocated by users
__version__ = '0.2.3'

# This just helps us distinguish our own messages from those of ffmpeg
_MSG_PREFIX = '>>>'

_FILE_SPEC = '%5d'
_MAX_HELP_WIDTH = 80
_TIMECODE_REGEX = re.compile(r'\d{2}:\d{2}:\d{2}:\d+')
_MANDATORY_VIDEO1_USER_ID = 'bot'
_MANDATORY_VIDEO2_USER_ID = 'top'

# Manually formatted and wrapped at 80 chars
DESCRIPTION = """
Description
===========

This tool is used to convert stereo HMC data into a format which is suitable for
the MetaHuman ingest process. It does this by taking two videos from the stereo
cameras and extracts the frames they contain into a pair of image sequences. It
also takes care of the audio and some other required data.

The method you choose for the image extraction can have a significant impact on
the resulting disk space required for the image sequence. So we've attempted to
summarize the available options below:

Mjpeg video:

    If you have an mjpeg encoded video, then you can achieve the optimal file
    size and quality by simply copying the (already jpeg encoded) frames to the
    disk. To achieve this you can use the 'jpg_copy' method.

Other video:

    In this case the 'jpg_copy' method will not work, as the frames in the video
    are unlikely to be encoded in such a way that we can simply copy the frames,
    we must re-encode them. To achieve the best quality, you can use either
    'png_gray' or 'png_rgb24', depending on whether the video contains gray or
    color data. 'png_gray' will use the least amount of space on disk out of
    those two options. For the time being, all data is assumed to be 8-bits per
    channel.

    If you wish to reduce the disk space required by the output images, and are
    willing to accept some reduction in quality to do so, then you can encode
    the frames as jpg, by using the 'jpg_lossy' method. This will encode the
    images as jpg with the highest quality (least compression) we have
    available. We do not offer multiple levels of jpg compression currently, as
    there likely isn't much to be gained in pushing the compression any further,
    the trade-off between file size and quality becomes increasingly difficult
    to make.

Also note: the calibration file specified on the command line will not get
copied into the output directory automatically, if you want this to happen, you
must do so manually.
"""

# Manually formatted and wrapped at 80 chars
EPILOG = '''
Examples
========

Grayscale video (mjpeg encoded):
    mh_ingest_convert.py bot camera1.mov top camera2.mov jpg_copy output_dir

Grayscale video (not mjpeg encoded):
    mh_ingest_convert.py bot camera1.mp4 top camera2.mp4 png_gray output_dir

Supplying extra audio and slate information (new lines added for clarity):
    mh_ingest_convert.py
        bot "C:\\path\\to\\bot.mov"
        top "C:\\path\\to\\top.mov"
        jpg_copy
        "C:\\path\\to\\output"
        --calibration-path "C:\\path\\to\\calib.json"
        --audio-path "C:\\path\\to\\audio.wav"
        --audio-timecode "12:34:56:78"
        --slate-name "My Slate Name"
        --overwrite
'''


class ConversionError(Exception):
    pass


class TakeInfo(NamedTuple):
    take_id: str
    number: int
    slate: str
    local_date_time: str


class DeviceInfo(NamedTuple):
    model: str
    device_type: str
    device_id: str


class VideoInput(NamedTuple):
    file_path: str
    user_id: str
    timecode: Optional[str]


class VideoInfo(NamedTuple):
    user_id: str
    file_path: str
    frame_rate: float
    frame_count: int
    start_timecode: str
    local_date_time: str


class ProcessedVideo(NamedTuple):
    input_info: VideoInfo
    output_dir: str


class AudioInfo(NamedTuple):
    user_id: str
    file_path: str
    timecode_frame_rate: float
    start_timecode: str


class ProcessedAudio(NamedTuple):
    input_info: AudioInfo
    output_path: str


class ExtractionMethod(enum.Enum):
    PNG_GRAY = 0
    PNG_RGB24 = 1
    JPG_COPY = 2
    JPG_LOSSY = 3


class ConversionOptions(NamedTuple):
    device_info: DeviceInfo
    video_infos: List[VideoInfo]
    output_dir: str
    calibration_path: str
    take_id: str
    slate: str
    take_number: int
    take_local_date_time: str
    extraction_method: ExtractionMethod
    audio_info: Optional[AudioInfo] = None


def _print_msg(msg):
    print(_MSG_PREFIX, msg)


def _timestamp_to_iso(timestamp: str) -> str:
    return date_parser.parse(timestamp).isoformat()


def _sanitize_path(output_dir, p) -> str:
    # We attempt to translate any paths inside the output directory into relative paths in the take json. This allows
    # users to move the output directory around. If that's not possible, we must use an absolute path instead, which
    # means if someone moves those files around then the ingest process will fail. Ideally all paths would end up as
    # relative paths inside the output directory.

    is_inside_output_dir = (
        os.path.abspath(output_dir) == os.path.commonpath([os.path.abspath(p), os.path.abspath(output_dir)])
    )

    if is_inside_output_dir:
        sanitised_path = os.path.relpath(os.path.abspath(p), os.path.abspath(output_dir))
    else:
        sanitised_path = os.path.abspath(p)

    return sanitised_path


def _try_get_reliable_frame_count(file_path: str):
    # This appears to be the simplest, fastest and most general mechanism for figuring out the frame count reliably. We
    # basically spool through the video and use ffmpeg's output to figure out how many frames there were.
    _, err = ffmpeg.input(
        file_path, vsync='passthrough'
    ).output(
        '-', format='null', map="0:v:0", vcodec='copy'
    ).run(
        quiet=True
    )

    err_lines = err.decode('utf8').splitlines()
    frame_count = None

    for err_line in err_lines:
        # This will match multiple times, but we're only interested in the last match
        m = re.match(r'frame=\s*(\d+).*', err_line)
        if m:
            frame_count = int(m.group(1))

    return frame_count


def _timecode_from_media_info(
    video_input: VideoInput,
    media_info: MediaInfo,
    video_timecode_options_by_id: Dict[str, str]
) -> str:
    if len(media_info.other_tracks) > 0:
        timecode = media_info.other_tracks[0].time_code_of_first_frame
        if timecode is not None:
            return timecode

    if len(media_info.video_tracks) > 0:
        timecode = media_info.video_tracks[0].time_code_of_first_frame
        if timecode is not None:
            return timecode

    # Use the video's user ID to find the appropriate command line option. We do this to be as informative as we can be.
    # Since we have all this information available to us, we can tell the user exactly which option they need to use.
    raise ConversionError(
        'Failed to extract video timecode (You can use {} to provide this manually): {}'.format(
            video_timecode_options_by_id[video_input.user_id],
            video_input.file_path
        )
    )


def read_video_info(video_input: VideoInput, video_timecode_options_by_id: Dict[str, str]) -> VideoInfo:
    assert video_input.user_id is not None
    assert video_input.file_path is not None

    media_info = MediaInfo.parse(video_input.file_path)

    if len(media_info.video_tracks) < 1:
        raise ConversionError("Expected at least one 'video' track: {}".format(video_input.file_path))

    if len(media_info.general_tracks) < 1:
        raise ConversionError("Expected at least one 'general' track: {}".format(video_input.file_path))

    video_track = media_info.video_tracks[0]
    general_track = media_info.general_tracks[0]

    if video_track.frame_rate is None:
        raise ConversionError("Missing 'video' track attribute 'frame_rate': {}".format(video_input.file_path))

    # Take json file requires that the frame rate be a float
    frame_rate = float(video_track.frame_rate)

    if general_track.file_creation_date__local is None:
        raise ConversionError(
            "Missing 'general' track attribute 'file_creation_date__local': {}".format(
                video_input.file_path
            )
        )

    local_date_time = _timestamp_to_iso(general_track.file_creation_date__local)

    if video_input.timecode is not None:
        start_timecode = video_input.timecode
    else:
        start_timecode = _timecode_from_media_info(video_input, media_info, video_timecode_options_by_id)

    frame_count = _try_get_reliable_frame_count(video_input.file_path)

    if frame_count is None:
        _print_msg('Could not determine a truly reliable frame count, falling back to inspecting metadata')

        # If there's a source_frame_count value then it's an indicator that frame_count will include duplicate frames
        # which will get stripped out when we run ffmpeg with vsync=passthrough below. So to get an accurate frame count
        # we take the source_frame_count if it is available.
        if video_track.source_frame_count is not None:
            _print_msg('Found source_frame_count attribute: {}'.format(video_track.source_frame_count))
            frame_count = int(video_track.source_frame_count)
        elif video_track.frame_count is not None:
            _print_msg(
                'No source_frame_count attribute, falling back to frame_count: {}'.format(
                    video_track.frame_count
                )
            )
            frame_count = int(video_track.frame_count)
        else:
            raise ConversionError('Could not extract frame count from video: {}'.format(video_input.file_path))

    # All information should be populated at this point
    assert frame_rate is not None
    assert frame_count is not None
    assert local_date_time is not None
    assert start_timecode is not None

    return VideoInfo(
        user_id=video_input.user_id,
        file_path=video_input.file_path,
        frame_rate=frame_rate,
        frame_count=frame_count,
        local_date_time=local_date_time,
        start_timecode=start_timecode
    )


def create_thumbnail(opts: ConversionOptions) -> str:
    assert len(opts.video_infos) > 0

    thumbnail_path = os.path.join(opts.output_dir, 'thumbnail.jpg')
    video_path = opts.video_infos[0].file_path

    stream = ffmpeg.input(
        video_path, vsync='passthrough'
    ).filter(
        # Just in case the input video has a sample aspect ratio which is not 1:1 (pixel aspect ratio)
        'scale', 'iw*sar', 'ih'
    )

    if opts.extraction_method == ExtractionMethod.PNG_GRAY:
        # Desaturate the image, to make sure the thumbnail matches the images in terms of color/grayscale
        stream = stream.filter('hue', s=0)

    stream = stream.filter(
        # Resize to thumbnail
        'scale', 90, -1
    ).output(
        # We use a "decent" quality factor for the image (-q:v)
        thumbnail_path, **{'q:v': 2, 'frames:v': 1}
    )

    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)

    return thumbnail_path


def _video_is_mjpeg(file_path: str):
    info = ffmpeg.probe(file_path, **{'select_streams': 'v:0'})

    if 'streams' not in info:
        raise ConversionError("No 'streams' entry found in ffprobe output for {}".format(file_path))

    num_streams = len(info['streams'])

    if num_streams == 0:
        raise ConversionError('No video streams found for {}'.format(file_path))

    if num_streams > 1:
        raise ConversionError(
            'Multiple video streams, we can not determine the appropriate encoding for {}'.format(
                file_path
            )
        )

    stream = info['streams'][0]

    if 'codec_type' not in stream:
        raise ConversionError('Failed to determine codec type for {}'.format(file_path))

    codec_type = stream['codec_type']

    if codec_type != 'video':
        raise ConversionError("Video codec type '{}' is not 'video' for {}".format(codec_type, file_path))

    if 'codec_name' not in stream:
        raise ConversionError('Failed to determine video codec name for {}'.format(file_path))

    return stream['codec_name'] == 'mjpeg'


def _split_png(info: VideoInfo, output_dir: str, pix_fmt: str) -> ProcessedVideo:
    file_path_spec = os.path.join(output_dir, '{}.png'.format(_FILE_SPEC))

    stream = ffmpeg.input(
        info.file_path, vsync='passthrough'
    ).filter(
        # Just in case the input video has a sample aspect ratio which is not 1:1 (pixel aspect ratio)
        'scale', 'iw*sar', 'ih'
    ).output(
        file_path_spec, start_number=1, pix_fmt=pix_fmt, **{'c:v': 'png'}
    ).overwrite_output()

    ffmpeg.run(stream)

    processed_video = ProcessedVideo(input_info=info, output_dir=output_dir)
    _check_frame_count(processed_video, '.png')
    return processed_video


def _split_jpeg_copy(info: VideoInfo, output_dir) -> ProcessedVideo:
    file_path_spec = os.path.join(output_dir, '{}.jpg'.format(_FILE_SPEC))

    stream = ffmpeg.input(
        info.file_path, vsync='passthrough'
    ).output(
        file_path_spec, start_number=1, **{'c:v': 'copy'}
    ).overwrite_output()

    ffmpeg.run(stream)

    processed_video = ProcessedVideo(input_info=info, output_dir=output_dir)
    _check_frame_count(processed_video, '.jpg')
    return processed_video


def _split_jpeg_lossy(info: VideoInfo, output_dir) -> ProcessedVideo:
    # For the time being, there is no real benefit to pushing the compression level higher and degrading the quality for
    # only a relatively small file size reduction
    compression_level = 1
    file_path_spec = os.path.join(output_dir, '{}.jpg'.format(_FILE_SPEC))

    stream = ffmpeg.input(
        info.file_path, vsync='passthrough'
    ).filter(
        # Just in case the input video has a sample aspect ratio which is not 1:1 (pixel aspect ratio)
        'scale', 'iw*sar', 'ih'
    ).output(
        file_path_spec,
        start_number=1,
        qmin=compression_level,
        qmax=compression_level,
        **{'c:v': 'mjpeg', 'q:v': compression_level},
    ).overwrite_output()

    ffmpeg.run(stream)

    processed_video = ProcessedVideo(input_info=info, output_dir=output_dir)
    _check_frame_count(processed_video, '.jpg')
    return processed_video


def process_video(info: VideoInfo, opts: ConversionOptions) -> ProcessedVideo:
    video_output_dir = os.path.join(opts.output_dir, info.user_id)
    os.makedirs(video_output_dir, exist_ok=True)

    if opts.extraction_method == ExtractionMethod.JPG_COPY:
        if _video_is_mjpeg(info.file_path):
            return _split_jpeg_copy(info, video_output_dir)
        else:
            raise ConversionError('Jpg copy extraction was requested but the video is not mjpeg encoded')

    elif opts.extraction_method == ExtractionMethod.JPG_LOSSY:
        return _split_jpeg_lossy(info, video_output_dir)

    elif opts.extraction_method == ExtractionMethod.PNG_RGB24:
        return _split_png(info, video_output_dir, 'rgb24')

    elif opts.extraction_method == ExtractionMethod.PNG_GRAY:
        return _split_png(info, video_output_dir, 'gray')

    else:
        raise ConversionError('Extraction method not implemented: {}'.format(opts.extraction_method))


def process_videos(opts: ConversionOptions):
    processed_videos = []

    for video_info in opts.video_infos:
        _print_msg('Processing {}...'.format(video_info.file_path))
        processed_video = process_video(video_info, opts)
        processed_videos.append(processed_video)

    return processed_videos


def read_audio_info(
    user_id: str,
    file_path: str,
    timecode_frame_rate: float,
    *,
    start_timecode: str = None,
) -> AudioInfo:
    media_info = MediaInfo.parse(file_path)

    # This check isn't strictly needed here if we aren't extracting timecode, but it helps to prevent someone passing in
    # a non-audio file by mistake
    if len(media_info.audio_tracks) < 1:
        raise ConversionError("Expected at least one 'audio' track: {}".format(file_path))

    # We will try to extract the timecode from the audio file if you don't supply a start_timecode but in that case you
    # must also provide a timecode_frame_rate.
    if start_timecode is None and timecode_frame_rate is not None:
        audio_track = media_info.audio_tracks[0]

        wav_info = WavInfoReader(file_path)
        bext = wav_info.bext

        if audio_track and bext:
            time_reference = bext.time_reference
            sampling_rate = audio_track.sampling_rate

            if time_reference and sampling_rate:
                frames = (time_reference / sampling_rate) * timecode_frame_rate
                start_timecode = '{0:02d}:{1:02d}:{2:02d}:{3:02d}'.format(
                    int(frames / (3600 * timecode_frame_rate)),
                    int(frames / (60 * timecode_frame_rate) % 60),
                    int(frames / timecode_frame_rate % 60),
                    int(round(frames % timecode_frame_rate))
                )

    if start_timecode is None:
        # We could not extract a start timecode for the audio and the user did not supply one. Simply leave it as an
        # empty string for the take json
        start_timecode = ''

    # All information should be populated at this point
    assert user_id is not None
    assert file_path is not None
    assert timecode_frame_rate is not None
    assert start_timecode is not None

    return AudioInfo(
        user_id=user_id,
        file_path=file_path,
        timecode_frame_rate=timecode_frame_rate,
        start_timecode=start_timecode
    )


def process_audio(opts: ConversionOptions) -> ProcessedAudio:
    output_path = os.path.join(opts.output_dir, opts.audio_info.user_id + '.wav')
    shutil.copy(opts.audio_info.file_path, output_path)

    return ProcessedAudio(input_info=opts.audio_info, output_path=output_path)


def write_take_json(
    take_info: TakeInfo,
    processed_videos: List[ProcessedVideo],
    processed_audios: List[ProcessedAudio],
    thumbnail_path: str,
    opts: ConversionOptions
):
    output_path = os.path.join(opts.output_dir, 'take.json')

    # Note: UserIDs in the take metadata file must have a corresponding value in the calibration file. We can't enforce
    # this here as there is no requirement that the calibration file exists at the time this script is run.

    audio_metadata = []
    for audio in processed_audios:
        audio_metadata.append(
            {
                'UserID': audio.input_info.user_id,
                'StreamPath': _sanitize_path(opts.output_dir, audio.output_path),
                'TimecodeRate': audio.input_info.timecode_frame_rate,
                'StartTimecode': audio.input_info.start_timecode
            }
        )

    video_metadata = []
    for video in processed_videos:
        video_metadata.append(
            {
                'UserID': video.input_info.user_id,
                'FrameRange': [
                    1,
                    video.input_info.frame_count
                ],
                'FrameRate': video.input_info.frame_rate,
                'FramesPath': _sanitize_path(opts.output_dir, video.output_dir),
                'StartTimecode': video.input_info.start_timecode
            }
        )

    take_metadata = {
        'Version': 1,
        'Id': take_info.take_id,
        'Take': take_info.number,
        'Slate': take_info.slate,
        'Thumbnail': _sanitize_path(opts.output_dir, thumbnail_path),
        'LocalDateTime': take_info.local_date_time,
        'DeviceInfo': {
            'Model': opts.device_info.model,
            'Type': opts.device_info.device_type,
            'Id': opts.device_info.device_id
        },
        'CalibrationInfo': _sanitize_path(opts.output_dir, opts.calibration_path),
        'Cameras': video_metadata,
        'Audio': audio_metadata
    }

    with open(output_path, 'w', encoding='utf8') as outfile:
        json.dump(take_metadata, outfile, indent=4)


def _check_frame_count(processed_video: ProcessedVideo, file_extension: str):
    file_count = 0

    for root_dir, dir_list, file_list in os.walk(processed_video.output_dir):
        for file_name in file_list:
            if file_name.endswith(file_extension):
                file_count += 1

    if file_count != processed_video.input_info.frame_count:
        raise ConversionError(
            'Number of images extracted from video ({}) does not match the metadata frame count ({}): {}'.format(
                file_count,
                processed_video.input_info.frame_count,
                processed_video.input_info.file_path
            )
        )


def convert(opts: ConversionOptions):
    processed_videos = process_videos(opts)
    processed_audios = []

    if opts.audio_info is not None:
        processed_audio = process_audio(opts)
        processed_audios.append(processed_audio)

    _print_msg('Creating thumbnail...')
    thumbnail_path = create_thumbnail(opts)

    _print_msg('Creating take json...')
    take_info = TakeInfo(
        take_id=opts.take_id,
        number=opts.take_number,
        slate=opts.slate,
        local_date_time=opts.take_local_date_time
    )

    write_take_json(
        take_info,
        processed_videos,
        processed_audios,
        thumbnail_path,
        opts
    )


def _ffmpeg_found():
    try:
        p = subprocess.run(['ffmpeg', '-version'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        return p.returncode == 0
    except subprocess.SubprocessError:
        return False
    except FileNotFoundError:
        return False


def _sanity_check():
    # The sanity check can take a second or so sometimes, so make sure we let the user know we're not just hanging
    sys.stdout.write(_MSG_PREFIX + ' Sanity check... ')
    sys.stdout.flush()

    if not _ffmpeg_found():
        sys.stdout.write('FAILED\n')
        sys.stdout.write(_MSG_PREFIX + " Error: ffmpeg not found, please install it and make sure it's on the PATH\n")
        sys.stdout.flush()
        sys.exit(1)

    sys.stdout.write('passed\n')
    sys.stdout.flush()


def _read_videos(video_inputs: List[VideoInput], video_timecode_options_by_id: Dict[str, str]) -> List[VideoInfo]:
    infos = []

    for video_input in video_inputs:
        video_info = read_video_info(video_input, video_timecode_options_by_id)
        infos.append(video_info)

    return infos


def _is_uuid4(s: str) -> bool:
    try:
        uuid.UUID(s, version=4)
        return True
    except ValueError:
        return False


def _check_file(file_path):
    if not os.path.isfile(file_path):
        raise ConversionError("File does not exist or is not a regular file: {}".format(file_path))


def _check_calibration_format(calibration_path):
    try:
        # A very basic sanity check to ensure the file is what we expect. We do not verify the internal format at the
        # moment, as it is a little unclear how significant the various pieces of information are or the importance of
        # their relative ordering etc. We leave formal validation to the ingest process for the time being.
        with open(calibration_path, 'r') as f:
            json.load(f)

    except JSONDecodeError as ex:
        raise ConversionError('Failed to read calibration file, invalid JSON: {}'.format(ex))

    except UnicodeDecodeError:
        raise ConversionError("Failed to read calibration file, it doesn't look like a text file")


def _check_timecode_str(timecode: str, asset_name: str):
    if not re.match(_TIMECODE_REGEX, timecode):
        raise ConversionError(
            "{} timecode doesn't have the expected format (HH:MM:SS:FRAMES): {}".format(
                asset_name,
                timecode
            )
        )


def run_conversion():
    # Restrict the maximum width of the help text, it makes it easier to read
    help_width = min(_MAX_HELP_WIDTH, shutil.get_terminal_size().columns - 2)

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        add_help=False,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, width=help_width),
        epilog=EPILOG
    )

    extraction_methods_by_name = {}

    for extraction_method in ExtractionMethod:
        method_name = extraction_method.name.lower()
        extraction_methods_by_name[method_name] = extraction_method

    video1_timecode_option = '--video1-timecode'
    video2_timecode_option = '--video2-timecode'

    parser.add_argument('video1_user_id', type=str, help='User ID for the bottom video of the stereo pair')
    parser.add_argument('video1_path', type=str, help='Path to the bottom video of the stereo pair')
    parser.add_argument('video2_user_id', type=str, help='User ID for the top video of the stereo pair')
    parser.add_argument('video2_path', type=str, help='Path to the top video of the stereo pair')
    parser.add_argument(
        'extraction_method_name',
        # metavar needed to display the help message correctly for some reason
        metavar='image_extraction_method',
        type=str,
        help='Image extraction method to use (Choose from: %(choices)s, see main description for more details)',
        choices=tuple(extraction_methods_by_name.keys())
    )
    parser.add_argument('output_path', type=str, help='Output directory for the converted data')

    parser.add_argument('--take-number', type=int, default=1,
                        help='Override default take number (Default: %(default)s)')
    parser.add_argument('--slate-name', type=str,
                        help='Override default slate name (Default: Name of the root folder for the first video file)')
    parser.add_argument('--take-uuid', type=str,
                        help='Override the auto-generated take ID (Must be a UUID4 compliant string)')
    parser.add_argument('--calibration-path', type=str,
                        help='Override default calibration path (Default: <output_path>/calib.json)')
    parser.add_argument('--audio-path', type=str, help='Audio file path')
    parser.add_argument('--audio-timecode', type=str,
                        help='Override audio start timecode (Default: Try to read it from the audio file)')
    parser.add_argument('--audio-timecode-rate', type=float,
                        help='Override audio timecode rate (Default: Use the frame rate of the first video)')
    parser.add_argument(video1_timecode_option, type=str,
                        help='Override video1 start timecode (Default: Try to read it from the video file')
    parser.add_argument(video2_timecode_option, type=str,
                        help='Override video2 start timecode (Default: Try to read it from the video file')
    parser.add_argument('--skip-sanity-check', '-s', action='store_true', help='Skip the sanity check')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite data in the output directory')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__),
                        help="Show the program's version number and exit")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit')
    args = parser.parse_args()

    # Always print this out, so we don't have to ask for it if we receive console output from users.
    _print_msg('Script version: {}'.format(__version__))

    video_timecode_options_by_id = {
        args.video1_user_id: video1_timecode_option,
        args.video2_user_id: video2_timecode_option
    }

    if not args.skip_sanity_check:
        _sanity_check()

    if os.path.exists(args.output_path):
        if not args.overwrite:
            raise ConversionError(
                'Output path already exists, use --overwrite to replace the existing data'.format(args.output_path)
            )
        if not os.path.isdir(args.output_path):
            raise ConversionError('Output path is not a directory, refusing to overwrite')

    _check_file(args.video1_path)
    _check_file(args.video2_path)

    # Guard against common copy-paste errors on the command line
    if args.video1_path == args.video2_path:
        raise ConversionError('Videos paths are the same')

    if args.audio_path is not None:
        # Guard against common copy-paste errors on the command line
        if args.audio_path == args.video1_path or args.audio_path == args.video2_path:
            raise ConversionError('Audio path is the same as one of the videos')

        _check_file(args.audio_path)

    # We need to restrict the allowed user IDs and the order they are passed in for the moment
    if args.video1_user_id != _MANDATORY_VIDEO1_USER_ID:
        raise ConversionError(
            "First video user ID must be '{}', it was set to '{}'".format(
                _MANDATORY_VIDEO1_USER_ID,
                args.video1_user_id
            )
        )

    if args.video2_user_id != _MANDATORY_VIDEO2_USER_ID:
        raise ConversionError(
            "Second video user ID must be '{}', it was set to '{}'".format(
                _MANDATORY_VIDEO2_USER_ID,
                args.video2_user_id
            )
        )

    if args.video1_timecode is not None:
        _check_timecode_str(args.video1_timecode, 'First video')

    if args.video2_timecode is not None:
        _check_timecode_str(args.video2_timecode, 'Second video')

    # We isolate the reading of metadata from the processing operations as this means we can avoid making any changes to
    # the filesystem if we encounter any errors while doing so.

    video_inputs = [
        VideoInput(
            file_path=args.video1_path,
            user_id=args.video1_user_id,
            timecode=args.video1_timecode
        ),
        VideoInput(
            file_path=args.video2_path,
            user_id=args.video2_user_id,
            timecode=args.video2_timecode
        )
    ]

    video_infos = _read_videos(video_inputs, video_timecode_options_by_id)
    assert len(video_infos) == 2

    if args.audio_timecode_rate is None:
        fallback_timecode_rate = video_infos[0].frame_rate
        video_frame_rates_match = all([math.isclose(x.frame_rate, fallback_timecode_rate) for x in video_infos])

        if not video_frame_rates_match:
            raise ConversionError("Videos have different frame rates, we can't infer the audio timecode frame rate")

        args.audio_timecode_rate = fallback_timecode_rate

    # This range is arbitrary, it's intended to catch user input errors rather than to enforce a hard limit. The upper
    # limit has been set this way just to prevent someone intending to type 24 fps from accidentally using 240, 241 etc.
    rate_limits = (1., 220.)
    if not (rate_limits[0] <= args.audio_timecode_rate <= rate_limits[1]):
        raise ConversionError(
            'Audio timecode rate is out of range {}: {}'.format(rate_limits, args.audio_timecode_rate)
        )

    audio_info = None

    if args.audio_timecode is not None:
        _check_timecode_str(args.audio_timecode, 'Audio')

    if args.audio_path is not None:
        audio_info = read_audio_info(
            'primary',
            args.audio_path,
            args.audio_timecode_rate,
            start_timecode=args.audio_timecode
        )

    if args.take_uuid is not None:
        if not _is_uuid4(args.take_uuid):
            raise ConversionError('Take UUID must be a UUID4 string')
    else:
        args.take_uuid = str(uuid.uuid4())

    if args.take_number < 1:
        raise ConversionError('Take number must be greater than zero')

    if args.slate_name is None:
        path_parents = Path(video_infos[0].file_path).parents

        if len(path_parents) > 1:
            args.slate_name = path_parents[1].name
        else:
            raise ConversionError(
                'Could not automatically determine the slate name from the video path, '
                'not enough parent directories, use --slate-name instead'
            )

    if args.calibration_path is None:
        args.calibration_path = os.path.join(args.output_path, 'calib.json')

    if os.path.exists(args.calibration_path):
        if not os.path.isfile(args.calibration_path):
            raise ConversionError('Calibration path exists but it is not a regular file')
        _check_calibration_format(args.calibration_path)

    # This should always be true if the enum members are used to generate the choices for the command line
    assert args.extraction_method_name in extraction_methods_by_name
    extraction_method = extraction_methods_by_name[args.extraction_method_name]

    take_local_date_time = video_infos[0].local_date_time
    device_info = DeviceInfo(model='StereoHMC', device_type='HMC', device_id='')

    # Basic sanity check that the necessary information is available for the conversion
    assert args.output_path is not None
    assert args.take_uuid is not None
    assert args.slate_name is not None
    assert args.take_number is not None
    assert args.calibration_path is not None
    assert take_local_date_time is not None
    assert device_info.model is not None
    assert device_info.device_type is not None
    assert device_info.device_id is not None

    # Convert args into an immutable, type-hinted object. It just makes it a bit easier to work with
    opts = ConversionOptions(
        device_info=device_info,
        video_infos=video_infos,
        output_dir=args.output_path,
        take_id=args.take_uuid,
        slate=args.slate_name,
        take_number=args.take_number,
        take_local_date_time=take_local_date_time,
        calibration_path=args.calibration_path,
        audio_info=audio_info,
        extraction_method=extraction_method
    )

    _print_msg('Take ID: {}'.format(opts.take_id))
    _print_msg('Take number: {}'.format(opts.take_number))
    _print_msg('Slate: {}'.format(opts.slate))
    _print_msg('Calibration path: {}'.format(opts.calibration_path))
    _print_msg('Take Local Date Time: {}'.format(opts.take_local_date_time))

    # Do as many sanity checks as we can BEFORE we actually do anything on the filesystem

    os.makedirs(args.output_path, exist_ok=True)
    convert(opts)


def main():
    try:
        run_conversion()

    except ffmpeg.Error as ex:
        _print_msg('Error (ffmpeg): {}\n  stdout={}\n  stderr={}'.format(ex, ex.stdout, ex.stderr))
        sys.exit(1)

    except ConversionError as ex:
        _print_msg('Error: ' + str(ex))
        sys.exit(1)

    except KeyboardInterrupt:
        # Don't print the stack trace on ctrl-c, it's somewhat alarming for users
        _print_msg('Interrupted')
        sys.exit(1)


if __name__ == '__main__':
    main()
