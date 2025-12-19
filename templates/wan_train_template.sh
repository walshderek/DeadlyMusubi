#!/bin/bash
# WAN 2.2 TRAINING TEMPLATE (Linux/WSL)
# Usage: ./train_wan.sh [PROJECT_NAME]
# Note: Paths converted from C:\AI to /mnt/c/AI

# --- CONFIG ---
PROJECT_NAME="${1:-my_project}"
TRIGGER_WORD="ohwx" # Default trigger, can be overridden
WSL_MODEL_ROOT="/mnt/c/AI/models"
WSL_APP_ROOT="/home/seanf/workspace/deadlygraphics/ai/apps/musubi-tuner"

# --- MODEL PATHS (Wan 2.2 Standard) ---
# Note: Wan 2.2 paths confirmed from original batch file
DIT_LOW="${WSL_MODEL_ROOT}/diffusion_models/Wan/Wan2.2/14B/Wan_2_2_T2V/fp16/wan2.2_t2v_low_noise_14B_fp16.safetensors"
DIT_HIGH="${WSL_MODEL_ROOT}/diffusion_models/Wan/Wan2.2/14B/Wan_2_2_T2V/fp16/wan2.2_t2v_high_noise_14B_fp16.safetensors"
VAE="${WSL_MODEL_ROOT}/vae/WAN/wan_2.1_vae.pth"
T5="${WSL_MODEL_ROOT}/clip/models_t5_umt5-xxl-enc-bf16.pth"

# --- COMMAND ---
accelerate launch --num_processes 1 "${WSL_APP_ROOT}/wan_train_network.py" \
  --dataset_config "${WSL_MODEL_ROOT}/files/tomls/${PROJECT_NAME}.toml" \
  --dit "${DIT_LOW}" \
  --dit_high_noise "${DIT_HIGH}" \
  --t5 "${T5}" \
  --vae "${VAE}" \
  --output_dir "${WSL_MODEL_ROOT}/outputs/${PROJECT_NAME}" \
  --output_name "${PROJECT_NAME}" \
  --fp8_base --fp8_scaled --fp8_t5 \
  --optimizer_type AdamW8bit \
  --learning_rate 0.0001
