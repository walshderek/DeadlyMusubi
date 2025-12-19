@echo off

setlocal enabledelayedexpansion

set "WAN=C:\AI\musubi-tuner"
set "CFG=C:\AI\musubi-tuner\files\tomls\baseline-wan2.2.toml"
set "DIT_LOW=A:\Models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors"
set "DIT_HIGH=A:\Models\diffusion_models\Wan\wan2.2_t2v_high_noise_14B_fp16.safetensors"
set "VAE=A:\Models\VAE\Wan\Wan2.1_VAE.pth"
set "T5=A:\Models\clip\models_t5_umt5-xxl-enc-bf16.pth"
set "OUT=C:\AI\musubi-tuner\outputs\baseline-wan2.2"
set "OUTNAME=baseline-wan2.2"
set "LOGDIR=C:\AI\musubi-tuner\logs"

cd /d "%WAN%"
call venv\scripts\activate

accelerate launch --num_processes 1 "wan_train_network.py" ^
  --dataset_config "%CFG%" ^
  --discrete_flow_shift 3 ^
  --dit "%DIT_LOW%" ^
  --dit_high_noise "%DIT_HIGH%" ^
  --fp8_base ^
  --fp8_scaled ^
  --fp8_t5 ^
  --gradient_accumulation_steps 1 ^
  --gradient_checkpointing ^
  --img_in_txt_in_offloading ^
  --learning_rate 0.0001 ^
  --log_with tensorboard ^
  --logging_dir "%LOGDIR%" ^
  --lr_scheduler cosine ^
  --lr_warmup_steps 100 ^
  --max_data_loader_n_workers 4 ^
  --max_timestep 1000 ^
  --max_train_epochs 35 ^
  --min_timestep 0 ^
  --mixed_precision fp16 ^
  --network_alpha 16 ^
  --network_args "verbose=True" "exclude_patterns=[]" ^
  --network_dim 16 ^
  --network_module networks.lora_wan ^
  --offload_inactive_dit ^
  --optimizer_type AdamW8bit ^
  --output_dir "%OUT%" ^
  --output_name "%OUTNAME%" ^
  --persistent_data_loader_workers ^
  --save_every_n_epochs 5 ^
  --seed 42 ^
  --t5 "%T5%" ^
  --task t2v-A14B ^
  --timestep_boundary 875 ^
  --timestep_sampling logsnr ^
  --vae "%VAE%" ^
  --vae_cache_cpu ^
  --vae_dtype float16 ^
  --sdpa

pause
