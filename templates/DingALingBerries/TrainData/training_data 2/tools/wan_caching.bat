@echo off

cd C:\AI\musubi-tuner

call venv\scripts\activate

python C:\AI\musubi-tuner\src\musubi_tuner\wan_cache_text_encoder_outputs.py --dataset_config "C:\AI\musubi-tuner\files\tomls\lmy-lora-wan2.2.toml"  --device cuda --num_workers 4 --t5 A:\Models\clip\models_t5_umt5-xxl-enc-bf16.pth --batch_size 4 --fp8_t5

python C:\AI\musubi-tuner\src\musubi_tuner\wan_cache_latents.py --dataset_config "C:\AI\musubi-tuner\files\tomls\my-lora-wan2.2.toml" --device cuda --num_workers 4 --vae A:\Models\VAE\Wan\Wan2.1_VAE.pth --batch_size 4 --vae_cache_cpu

pause

