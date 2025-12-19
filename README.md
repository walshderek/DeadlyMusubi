# DeadlyMusubi

**Musubi Tuner configurations for Wan 2.2 dual-mode video model training**

This repository contains standardized templates and scripts for training custom LoRAs using the Musubi Tuner framework with Wan 2.2 models. Part of the [Deadly Graphics](https://github.com/walshderek/deadlygraphics) AI production pipeline.

> **Note**: All musubi configurations imported from deadlygraphics repository and ready to use!

## 📋 Overview

Wan 2.2 is a dual-noise video generation model that requires specialized training configurations. This repo provides:

- **Training Templates**: Pre-configured shell scripts for Wan 2.2 training
- **Dataset Configs**: TOML templates for dataset configuration
- **Helper Scripts**: Automation tools for generating project-specific configs

## 🚀 Quick Start

### Prerequisites

- Musubi Tuner installed (from [deadlygraphics](https://github.com/walshderek/deadlygraphics) setup)
- Wan 2.2 models downloaded to `/mnt/c/AI/models/diffusion_models/Wan/Wan2.2/`
- Training data prepared with images and caption files

### Generate a Training Configuration

```bash
# Generate config for a new project
./scripts/generate_config.sh my_character ohwx

# This creates:
# - configs/my_character.toml (dataset configuration)
# - configs/my_character_train.sh (training script)
```

### Prepare Training Data

1. Create your project directory:
   ```bash
   mkdir -p /mnt/c/AI/training_data/my_character/images
   ```

2. Add your training images and create corresponding `.txt` caption files:
   ```
   /mnt/c/AI/training_data/my_character/images/
   ├── image001.png
   ├── image001.txt  # Caption: "ohwx character standing"
   ├── image002.png
   └── image002.txt  # Caption: "ohwx character sitting"
   ```

### Run Training

```bash
# Execute the generated training script
./configs/my_character_train.sh
```

## 📁 Repository Structure

```
DeadlyMusubi/
├── templates/
│   ├── wan_train_template.sh          # Base training script template
│   └── dataset_config_template.toml   # Base TOML configuration
├── scripts/
│   └── generate_config.sh             # Config generation helper
├── configs/                           # Generated configs (gitignored)
└── README.md
```

## ⚙️ Configuration Details

### Wan 2.2 Model Paths

The training script expects Wan 2.2 models at these locations:
- **Low Noise DiT**: `/mnt/c/AI/models/diffusion_models/Wan/Wan2.2/14B/Wan_2_2_T2V/fp16/wan2.2_t2v_low_noise_14B_fp16.safetensors`
- **High Noise DiT**: `/mnt/c/AI/models/diffusion_models/Wan/Wan2.2/14B/Wan_2_2_T2V/fp16/wan2.2_t2v_high_noise_14B_fp16.safetensors`
- **VAE**: `/mnt/c/AI/models/vae/WAN/wan_2.1_vae.pth`
- **T5 Text Encoder**: `/mnt/c/AI/models/clip/models_t5_umt5-xxl-enc-bf16.pth`

### Training Parameters

Default training configuration:
- **Resolution**: 832x480 (Wan 2.2 standard)
- **Batch Size**: 1
- **Optimizer**: AdamW8bit
- **Learning Rate**: 0.0001
- **Precision**: FP8 (base, scaled, and T5)
- **Repeats**: 10

Modify these in the generated TOML or training script as needed.

## 🔧 Manual Configuration

If you prefer to create configs manually:

1. Copy the template:
   ```bash
   cp templates/dataset_config_template.toml configs/my_project.toml
   ```

2. Edit the TOML file:
   - Replace `[PROJECT_NAME]` with your project name
   - Replace `[TRIGGER_WORD]` with your trigger word
   - Adjust resolution, batch size, and other parameters

3. Copy and customize the training script:
   ```bash
   cp templates/wan_train_template.sh configs/my_project_train.sh
   chmod +x configs/my_project_train.sh
   ```

## 📚 Related Documentation

- [Deadly Graphics Main Repo](https://github.com/walshderek/deadlygraphics)
- [Musubi Tuner](https://github.com/kohya-ss/musubi-tuner)
- Wan 2.2 Model Documentation (see deadlygraphics docs)

## 📄 License

Part of the Deadly Graphics ecosystem. See main repository for license details.
