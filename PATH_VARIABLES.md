# Path Variables Reference

This document defines the standard path variables used across different environments and organizations for adapting DingALingBerries scripts to DeadlyGraphics in both Unix and Windows environments.

## Path Format Types

There are **4 path format scenarios** used in this project:

| Format | Description | Separator | Drive Format |
|--------|-------------|-----------|--------------|
| **Windows** | Standard Windows batch files | `\` (backslash) | `C:\`, `A:\` |
| **Unix** | Linux/WSL shell scripts | `/` (forward slash) | `/mnt/c/`, `/mnt/a/` |
| **MusubiToml (Win)** | Musubi Windows TOML configs | `/` (forward slash) | `C:/`, `A:/` |
| **MusubiToml (Unix)** | Musubi Linux TOML configs | `/` (forward slash) | `/mnt/c/`, `/mnt/a/` |

## Conversion Rules

### Windows ↔ Unix
- Drive letter: `C:` → `/mnt/c/`
- Drive letter: `A:` → `/mnt/a/`
- Separator: `\` → `/`

### Windows ↔ MusubiToml (Win)
- Drive letter: unchanged
- Separator: `\` → `/`

### Unix ↔ MusubiToml (Unix)
- Drive letter: same (`/mnt/x/`)
- Separator: same (`/`)

---

## Organization-Specific Paths

### **DingALingBerries**

#### WAN (Musubi Installation)
| Format | Path |
|--------|------|
| Windows | `C:\AI\musubi-tuner` |
| Unix | `/mnt/c/AI/musubi-tuner` |
| MusubiToml (Win) | `C:/AI/musubi-tuner` |
| MusubiToml (Unix) | `/mnt/c/AI/musubi-tuner` |

#### T5 Model
| Format | Path |
|--------|------|
| Windows | `A:\Models\clip\models_t5_umt5-xxl-enc-bf16.pth` |
| Unix | `/mnt/a/Models/clip/models_t5_umt5-xxl-enc-bf16.pth` |
| MusubiToml (Win) | `A:/Models/clip/models_t5_umt5-xxl-enc-bf16.pth` |
| MusubiToml (Unix) | `/mnt/a/Models/clip/models_t5_umt5-xxl-enc-bf16.pth` |

#### DIT_LOW
| Format | Path |
|--------|------|
| Windows | `A:\Models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| Unix | `/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| MusubiToml (Win) | `A:/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| MusubiToml (Unix) | `/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors` |

#### DIT_HIGH
| Format | Path |
|--------|------|
| Windows | `A:\Models\diffusion_models\Wan\wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| Unix | `/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| MusubiToml (Win) | `A:/Models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| MusubiToml (Unix) | `/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |

#### VAE
| Format | Path |
|--------|------|
| Windows | `A:\Models\VAE\Wan\Wan2.1_VAE.pth` |
| Unix | `/mnt/a/Models/VAE/Wan/Wan2.1_VAE.pth` |
| MusubiToml (Win) | `A:/Models/VAE/Wan/Wan2.1_VAE.pth` |
| MusubiToml (Unix) | `/mnt/a/Models/VAE/Wan/Wan2.1_VAE.pth` |

#### LOGDIR
| Format | Path |
|--------|------|
| Windows | `C:\AI\musubi-tuner\logs` |
| Unix | `/mnt/c/AI/musubi-tuner/logs` |
| MusubiToml (Win) | `C:/AI/musubi-tuner/logs` |
| MusubiToml (Unix) | `/mnt/c/AI/musubi-tuner/logs` |

#### Source Data (Training Data)
| Format | Path Pattern |
|--------|--------------|
| Windows | `C:\AI\musubi-tuner\source_data\{name}\[photos|videos|images]` |
| Unix | `/mnt/c/AI/musubi-tuner/source_data/{name}/[photos|videos|images]` |
| MusubiToml (Win) | `C:/AI/musubi-tuner/source_data/{name}/[photos|videos|images]` |
| MusubiToml (Unix) | `/mnt/c/AI/musubi-tuner/source_data/{name}/[photos|videos|images]` |

**Cache Directory Pattern:**
- Windows: `C:\AI\musubi-tuner\source_data\{name}\[photos|videos|images]\cache`
- MusubiToml: `C:/AI/musubi-tuner/source_data/{name}/[photos|videos|images]/cache`

---

### **DeadlyGraphics**

#### WAN (Musubi Installation)
| Format | Path |
|--------|------|
| Windows | `C:\AI\apps\musubi-tuner` |
| Unix | `/mnt/c/AI/apps/musubi-tuner` |
| MusubiToml (Win) | `C:/AI/apps/musubi-tuner` |
| MusubiToml (Unix) | `/mnt/c/AI/apps/musubi-tuner` |

#### T5 Model
| Format | Path |
|--------|------|
| Windows | `C:\AI\models\clip\models_t5_umt5-xxl-enc-bf16.pth` |
| Unix | `/mnt/c/AI/models/clip/models_t5_umt5-xxl-enc-bf16.pth` |
| MusubiToml (Win) | `C:/AI/models/clip/models_t5_umt5-xxl-enc-bf16.pth` |
| MusubiToml (Unix) | `/mnt/c/AI/models/clip/models_t5_umt5-xxl-enc-bf16.pth` |

#### DIT_LOW
| Format | Path |
|--------|------|
| Windows | `C:\AI\models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| Unix | `/mnt/c/AI/models/diffusion_models/Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| MusubiToml (Win) | `C:/AI/models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors` |
| MusubiToml (Unix) | `/mnt/c/AI/models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors` |

#### DIT_HIGH
| Format | Path |
|--------|------|
| Windows | `C:\AI\models\diffusion_models\Wan\wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| Unix | `/mnt/c/AI/models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| MusubiToml (Win) | `C:/AI/models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |
| MusubiToml (Unix) | `/mnt/c/AI/models/diffusion_models/Wan/wan2.2_t2v_high_noise_14B_fp16.safetensors` |

#### VAE
| Format | Path |
|--------|------|
| Windows | `C:\AI\models\VAE\Wan\Wan2.1_VAE.pth` |
#### Source Data (Training Data)
| Format | Path Pattern |
|--------|--------------|
| Windows | `C:\AI\apps\musubi-tuner\source_data\{name}\[photos|videos|images]` |
| Unix | `/mnt/c/AI/apps/musubi-tuner/source_data/{name}/[photos|videos|images]` |
| MusubiToml (Win) | `C:/AI/apps/musubi-tuner/source_data/{name}/[photos|videos|images]` |
| MusubiToml (Unix) | `/mnt/c/AI/apps/musubi-tuner/source_data/{name}/[photos|videos|images]` |

**Cache Directory Pattern:**
- Windows: `C:\AI\apps\musubi-tuner\source_data\{name}\[photos|videos|images]\cache`
- MusubiToml: `C:/AI/apps/musubi-tuner/source_data/{name}/[photos|videos|images]/cache`

| Unix | `/mnt/c/AI/models/VAE/Wan/Wan2.1_VAE.pth` |
| MusubiToml (Win) | `C:/AI/models/VAE/Wan/Wan2.1_VAE.pth` |
| MusubiToml (Unix) | `/mnt/c/AI/models/VAE/Wan/Wan2.1_VAE.pth` |

#### LOGDIR
| Format | Path |
|--------|------|
| Windows | `C:\AI\apps\musubi-tuner\logs` |
| Unix | `/mnt/c/AI/apps/musubi-tuner/logs` |
| MusubiToml (Win) | `C:/AI/apps/musubi-tuner/logs` |
| MusubiToml (Unix) | `/mnt/c/AI/apps/musubi-tuner/logs` |

---

## Key Organizational Differences

### Path Differences

| Variable | DingALingBerries | DeadlyGraphics |
|----------|------------------|----------------|
| **Musubi Base** | `C:\AI\musubi-tuner` | `C:\AI\apps\musubi-tuner` |
| **Models Drive** | `A:\Models\...` | `C:\AI\models\...` |
| **Models Case** | `Models` (uppercase M) | `models` (lowercase m) |
| **Same Drive?** | No (C: and A:) | Yes (all on C:) |

### Naming Convention Differences

#### OUTNAME & CFG Patterns:

| Parameter | Range | Description |
|-----------|-------|-------------|
| `CFG` | See naming conventions above | Dataset config filename (organization-specific format) |
| `OUT` | `outputs/{OUTNAME}` | Output directory (uses OUTNAME pattern) |
| `OUTNAME` | See naming conventions above | Output filename (organization-specific format)
- **Model Format:** Dots allowed (`wan2.2`)

**DeadlyGraphics Pattern:** `(char)_(model)_(version)`
- **Example OUTNAME:** `shrek_Wan2_2_v0007`
- **Example CFG:** `shrek_Wan2_2_v0007.toml`
- **Separator:** `_` (underscore)
- **Version Padding:** 4 digits (`v0007`)
- **Model Format:** Underscores only (`Wan2_2`)

#### Conversion Examples

| DingALingBerries | DeadlyGrap - DingALingBerries)
```batch
set "WAN=C:\AI\musubi-tuner"
set "CFG=C:\AI\musubi-tuner\files\tomls\shrek-v7-wan2.2.toml"
set "DIT_LOW=A:\Models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors"
set "OUT=C:\AI\musubi-tuner\outputs\shrek-v7-wan2.2"
set "OUTNAME=shrek-v7-wan2.2"
```

### Batch File Example (Windows - DeadlyGraphics)
```batch
set "WAN=C:\AI\apps\musubi-tuner"
set "CFG=C:\AI\apps\musubi-tuner\files\tomls\shrek_Wan2_2_v0007.toml"
set "DIT_LOW=C:\AI\models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors"
set "OUT=C:\AI\apps\musubi-tuner\outputs\shrek_Wan2_2_v0007"
set "OUTNAME=shrek_Wan2_2_v0007"
```

### Shell Script Example (Unix - DingALingBerries)
```bash
WAN="/mnt/c/AI/musubi-tuner"
CFG="/mnt/c/AI/musubi-tuner/files/tomls/shrek-v7-wan2.2.toml"
DIT_LOW="/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
OUT="/mnt/c/AI/musubi-tuner/outputs/shrek-v7-wan2.2"
OUTNAME="shrek-v7-wan2.2"
```

### Shell Script Example (Unix - DeadlyGraphics)
```bash
WAN="/mnt/c/AI/apps/musubi-tuner"
CFG="/mnt/c/AI/apps/musubi-tuner/files/tomls/shrek_Wan2_2_v0007.toml"
DIT_LOW="/mnt/c/AI/models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
OUT="/mnt/c/AI/apps/musubi-tuner/outputs/shrek_Wan2_2_v0007"
OUTNAME="shrek_Wan2_2_v0007"
```

### MusubiToml Example (Win - DingALingBerries)
```toml
dit_low = "A:/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
```

### MusubiToml Example (Unix - DeadlyGraphics)
4. **Source Data:** Add `/apps` → `C:\AI\musubi-tuner\source_data\` → `C:\AI\apps\musubi-tuner\source_data\`
```toml
dit_low = "/mnt/c/AI/models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
```

---

## Quick Reference: Adapting DingALingBerries → DeadlyGraphics

### Path Changes
1. **WAN:** Add `/apps` → `C:\AI\musubi-tuner` → `C:\AI\apps\musubi-tuner`
2. **Models:** Change drive and case → `A:\Models\` → `C:\AI\models\`
3. **LOGDIR:** Add `/apps` → `C:\AI\musubi-tuner\logs` → `C:\AI\apps\musubi-tuner\logs`

### Naming Changes
1. **Reorder:** `(char)-(version)-(model)` → `(char)_(model)_(version)`
2. **Separator:** Replace `-` with `_`
3. **Model:** Replace `.` with `_` and capitalize → `wan2.2` → `Wan2_2`
4. **Version:** Pad to 4 digits → `v7` → `v0007`

### Example Complete Conversion
**DingALingBerries:** `shrek-v7-wan2.2`  
**DeadlyGraphics:** `shrek_Wan2_2_v0007e following parameters vary per training configuration (not path-related):

| Parameter | Range | Description |
|-----------|-------|-------------|
| `CFG` | `{name}-wan2.2.toml` | Dataset config filename |
| `OUT` | `outputs/{name}-wan2.2` | Output directory |
| `OUTNAME` | `{name}-wan2.2` | Output filename |
| `learning_rate` | 0.0001 - 0.0003 | Training learning rate |
| `network_alpha` | 4, 8, 16 | Network alpha dimension |
| `network_dim` | 4, 8, 16 | Network dimension |
| `max_data_loader_n_workers` | 4 - 16 | Data loader workers |
| `max_train_epochs` | 30 - 40 | Training epochs |
| `gradient_accumulation_steps` | 1 - 2 | Gradient accumulation |

---

## Usage in Scripts

### Batch File Example (Windows)
```batch
set "WAN=C:\AI\musubi-tuner"
set "DIT_LOW=A:\Models\diffusion_models\Wan\wan2.2_t2v_low_noise_14B_fp16.safetensors"
```

### Shell Script Example (Unix)
```bash
WAN="/mnt/c/AI/musubi-tuner"
DIT_LOW="/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
```

### TOML Example (WinToml)
```toml
dit_low = "A:/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
```

### TOML Example (UnixToml)
```toml
dit_low = "/mnt/a/Models/diffusion_models/Wan/wan2.2_t2v_low_noise_14B_fp16.safetensors"
```
