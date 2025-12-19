@echo off

cd C:\AI\musubi-tuner

call venv\scripts\activate

python src/musubi_tuner/convert_lora.py --input C:\AI\musubi-tuner\outputs\my-lora-wan2.2\my-lora-wan2.2.safetensors --output C:\AI\musubi-tuner\outputs\my-lora-wan2.2\my-lora-wan2.2_converted.safetensors --target other

pause
