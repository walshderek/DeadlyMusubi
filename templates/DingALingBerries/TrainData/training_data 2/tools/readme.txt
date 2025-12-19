You need only these:

     pip install pillow safetensors torch

and you should be able to run all of these...

- The captioner.bat is simple and fast... replace the path to your files and your trigger in quotes into the .bat file and save it, then double-click it.  All files will be captioned and ready for caching.  It runs captioner_v2.py.  It is recursive, so all files in subfolders will also be captioned.

- The wan_caching.bat is likewise super simple.  Paste your paths and save it, then double-click it.  Adjust the batch and number of workers for your CPU - start with half your threads for each.

- The convert_lora.bat *was* to enable use of your trained loras in comfyui - raw files previously did not work, though a couple of quick tests seems to show they do work now without conversion.  Just adjust the paths and double-click.  This is using offical musubi scripts.  Might be necessary for compatibility with older inference scripts.

- The image_culler_cropper.py script is a GUI image cropper tool.  View a directory of images as thumbs, adjust thumb size, draw crops on a big preview, press a button to crop, press a button to save.  Very fast and efficient image prep script I vibe-coded and can't live without now.  Trim the fat, don't train on negative space and noise.  Crop hard.

- The lora_metadata_gui.py script does what it says, it opens a GUI, you select a safetensors file, and it diplays the metadata, allowing you to edit and save the file with new metadata.  Useful for checking your learning rate and such.

- The media_compressor.py is a script that opens a GUI and allows you to compress audio or video to a set size, with adjustments for dimensions and framerate.  Size is the overriding parameter.  Meant to compress videos for sharing on discord or session or any other service with a file size limit.  Compresses audio to mp3 and compresses any video format to mp4 using ffmpeg.  Will probably choke on animated webp as it does not use image-io.  You will need ffmpeg in the path or in your PATH.

- versioncheck.py is a common script that logs a bunch of useful info to the console for you.  I tend to run it once after a fresh install of anything into a venv to check everything in one go.  Will tell you about your venv and your system, including python, torch, and cuda versions, as well as installed packages and any dependency conflicts.  I run it as a last step in my installs via muscle memory now.

- Video16FPS_Converter.py is a GUI for converting the framerate of video files.  I no longer use it regularly, but you might find it useful. Uses a configurable queue, has a nice detailed log, allows you to set FPS, encoder, device, and quality.  Not polished.  Check out ShareX instead and screencap directly at 16fps for Wan training.

- AI_stripper.py strips metadata.  A bit janky and unpolished but works just fine.  Double-click, select a folder with media to strip, bam.

- png_search_engine.py is a tool to search a directory of AI outputs in .png format for strings in the metadata.  If your prompt used the word "shrek" you can double-click this script, select a folder and input the string, and it will search recursively through the root for any file with that string anywhere it can see.  Creates folders in the source directory named for the string and copies files there.  Simple, slow, dumb, and effective.