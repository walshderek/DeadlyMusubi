If you want to replicate my results with my data and settings, you need to use the musubi repo from Aug. 15th, before some changes that made things bork.

So...

-------------------------------------------------------

git clone https://github.com/kohya-ss/musubi-tuner.git

cd musubi-tuner

git fetch --all

git checkout e7adb86

python -m venv venv

venv\scripts\activate

pip install -e .

pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

python versioncheck.py

-------------------------------------------------------

That should be all you need.