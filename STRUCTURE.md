# Directory Structure Guide

This document outlines the expected directory structure for Wan 2.2 training with DeadlyMusubi configs.

## Model Storage Structure

Models should be organized under `/mnt/c/AI/models/` (Windows path: `C:\AI\models\`):

```
/mnt/c/AI/models/
├── diffusion_models/
│   └── Wan/
│       └── Wan2.2/
│           └── 14B/
│               └── Wan_2_2_T2V/
│                   └── fp16/
│                       ├── wan2.2_t2v_low_noise_14B_fp16.safetensors
│                       └── wan2.2_t2v_high_noise_14B_fp16.safetensors
├── vae/
│   └── WAN/
│       └── wan_2.1_vae.pth
├── clip/
│   └── models_t5_umt5-xxl-enc-bf16.pth
├── files/
│   └── tomls/              # TOML configs (can also use configs/ in this repo)
└── outputs/                # Training outputs
    └── [project_name]/
        └── [project_name]_*.safetensors
```

## Training Data Structure

Training data should be organized per project:

```
/mnt/c/AI/training_data/
└── [project_name]/
    └── images/
        ├── frame001.png
        ├── frame001.txt    # Caption file
        ├── frame002.png
        ├── frame002.txt
        └── ...
```

## Caption Format

Each image should have a corresponding `.txt` file with the same base name:

**Example: `frame001.txt`**
```
ohwx character walking in the forest, natural lighting, cinematic
```

**Caption Guidelines:**
- Start with your trigger word (default: `ohwx`)
- Be descriptive but concise
- Include important details: action, setting, lighting, style
- Avoid contradictory descriptions

## Project Workspace

This DeadlyMusubi repository structure:

```
DeadlyMusubi/
├── templates/              # Template files (committed)
│   ├── wan_train_template.sh
│   └── dataset_config_template.toml
├── scripts/               # Helper scripts (committed)
│   └── generate_config.sh
├── configs/               # Generated configs (gitignored)
│   ├── project1.toml
│   ├── project1_train.sh
│   ├── project2.toml
│   └── project2_train.sh
└── README.md
```

## Integration with Musubi Tuner

Musubi Tuner should be installed at:
```
/home/seanf/workspace/deadlygraphics/ai/apps/musubi-tuner/
```

This path is referenced in the training scripts. Adjust if your installation differs.

## Outputs

Training outputs will be saved to:
```
/mnt/c/AI/models/outputs/[project_name]/
```

Each training run produces:
- `[project_name]_*.safetensors` - LoRA checkpoint files
- Training logs and metrics
