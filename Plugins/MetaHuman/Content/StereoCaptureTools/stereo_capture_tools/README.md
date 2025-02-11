# Stereo Capture Tools
A collection of scripts to convert captured stereo data into a format suitable for the MetaHuman ingest process.

## Setup
These scripts require `python 3.6+` and that `ffmpeg` is installed and available on your `$PATH`.

### Install ffmpeg
If you're on Windows:
1. Go to https://www.gyan.dev/ffmpeg/builds/ and download `ffmpeg-git-full.7z`. If that URL is unavailable for
any reason then you can also get ffmpeg from https://github.com/BtbN/FFmpeg-Builds/releases but the filename is a little
different (`ffmpeg-master-latest-win64-gpl-shared.zip`).
2. Unpack this zip file somewhere that makes sense for you.
3. Open the start menu and type "Edit the System Environment Variables"
4. Click on the corresponding entry.
5. Click the "Environment Variables..." button near the bottom right of this new window.
6. Find "Path" in the upper section of the resulting window and click "Edit".
7. Add the location of the `bin` directory of the ffmpeg you extracted in step 2 to the "Path".
8. Make sure you open a fresh powershell (or pycharm etc.) window once you've made this change, so that it takes effect
for that program.

If you are not presented with a list to edit in step 7, you can achieve the same thing by adding a semicolon between the
entries, for example: `C:\some\path;C:\some\other\path;D:\path\to\my\ffmpeg\bin`

### Install Python Dependencies
Create a virtual environment before installing dependencies to avoid polluting your system library. For simplicity, we
execute these commands from the directory where you have the stereo capture tools unpacked.

In powershell:
```PowerShell
# The path containing the requirements.txt:
cd path\to\stereo_capture_tools
python -m venv venv
.\venv\Scripts\activate.ps1
pip install -r requirements.txt
```
Or alternatively in cmd:
```Batchfile
:: The path containing the requirements.txt:
cd path\to\stereo_capture_tools
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Converting Stereo HMC Data

To convert stereo HMC footage into a format suitable for MetaHuman ingest, you must run the mh_ingest_convert.py script.
A few examples are given below, but for a full list of the available options just run the script with the `--help` flag.
To print the script version run the script with the `--version` flag.

### Examples

For simplicity, in the following examples we assume you are running the script from the same directory which houses the
requirements.txt file.

> **Note**
> If you're using a virtual environment, make sure you've called the activate.ps1 (powershell) or activate.bat (cmd)
> to set up that environment for the current shell, before you run the following commands. You have to do this each time
> you open a new terminal window.

A simple conversion (this works with either powershell or cmd):
```PowerShell
python stereo_capture_tools\mh_ingest_convert.py bot "C:\path\to\bot.mp4" top "C:\path\to\top.mp4" png_gray "C:\path\to\output"
```

A more complex conversion which makes use of several additional (optional) parameters. Here we also make use of the
powershell line continuation character (\`), just to make the command a little easier to read.

In powershell:
```PowerShell
python stereo_capture_tools\mh_ingest_convert.py `
    bot "C:\path\to\bot.mp4" `
    top "C:\path\to\top.mp4" `
    png_gray `
    "C:\path\to\output" `
    --calibration-path "C:\path\to\calib.json" `
    --audio-path "C:\path\to\audio.wav" `
    --audio-timecode "12:34:56:78" `
    --slate-name "My Slate Name" `
    --overwrite
```


