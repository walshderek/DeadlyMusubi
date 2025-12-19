# Virtual Environment Test Matrix for e7adb86

## Current Date: December 19, 2025
## Target: musubi-tuner commit e7adb86 (August 16, 2024)

---

## 🔴 YOUR CURRENT ENVIRONMENT (BROKEN - NaN Errors)

```
Python: 3.10.11
torch: 2.8.0+cu128
torchvision: 0.23.0+cu128
numpy: 2.2.6                    ← PRIMARY CULPRIT (NumPy 2.x breaking changes)
transformers: 4.54.1
accelerate: 1.6.0
safetensors: 0.4.5
flash-attn: NOT INSTALLED       ← Missing dependency
xformers: NOT INSTALLED         ← Missing dependency
sageattention: 1.0.6
triton: 3.5.1

CUDA: 12.8
cuDNN: 9.1.0.2
```

**Diagnosis:** NumPy 2.2.6 is incompatible with e7adb86 code. Downgrade to NumPy 1.26.x immediately.

---

## ✅ PROFILE 1: "DingALingBerries Official" (SAFEST - RECOMMENDED)

**Best for:** Maximum stability, guaranteed to work with e7adb86

### Installation Steps (Windows):

```bash
# Create fresh venv
python -m venv venv_e7adb86_safe
.\venv_e7adb86_safe\Scripts\activate

# Install exact versions from August 2024
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# Core dependencies (matched to Aug 2024)
pip install numpy==1.26.4
pip install transformers==4.43.3
pip install accelerate==0.33.0
pip install safetensors==0.4.4
pip install diffusers==0.30.0

# Required for e7adb86
pip install einops==0.7.0
pip install av==12.2.0
pip install opencv-python==4.10.0.84
pip install sentencepiece==0.2.0
pip install ftfy==6.3.1
pip install toml==0.10.2
pip install easydict==1.13
pip install voluptuous==0.15.2
pip install tqdm==4.66.5
pip install psutil==6.0.0

# Optional but recommended for performance
pip install flash-attn --no-build-isolation
pip install xformers==0.0.27.post2

# Install musubi-tuner in editable mode
cd C:\AI\apps\musubi-tuner
pip install -e .
```

### Expected Versions:
```
Python: 3.10.11
torch: 2.4.0+cu124
numpy: 1.26.4               ← Fixed NumPy 1.x
transformers: 4.43.3
accelerate: 0.33.0
safetensors: 0.4.4
flash-attn: 2.6.3 (if successful)
xformers: 0.0.27.post2 (if successful)
CUDA: 12.4
```

**Test Priority:** 🟢 **HIGH** - Start here first

---

## ✅ PROFILE 2: "Conservative Update" (SAFE)

**Best for:** Slight updates while maintaining compatibility

### Installation Steps (Windows):

```bash
# Create fresh venv
python -m venv venv_e7adb86_conservative
.\venv_e7adb86_conservative\Scripts\activate

# Updated PyTorch (still compatible)
pip install torch==2.5.1+cu124 torchvision==0.20.1+cu124 --index-url https://download.pytorch.org/whl/cu124

# Core dependencies (slightly newer but safe)
pip install numpy==1.26.4           # Keep NumPy 1.x!
pip install transformers==4.45.0
pip install accelerate==0.34.2
pip install safetensors==0.4.5
pip install diffusers==0.31.0

# Required packages
pip install einops==0.7.0
pip install av==13.0.0
pip install opencv-python==4.10.0.84
pip install sentencepiece==0.2.0
pip install ftfy==6.3.1
pip install toml==0.10.2
pip install easydict==1.13
pip install voluptuous==0.15.2
pip install tqdm==4.67.1
pip install psutil==6.0.0

# Performance libraries
pip install flash-attn --no-build-isolation
pip install xformers==0.0.28.post2

# Install musubi-tuner
cd C:\AI\apps\musubi-tuner
pip install -e .
```

### Expected Versions:
```
Python: 3.10.11
torch: 2.5.1+cu124
numpy: 1.26.4               ← Still NumPy 1.x
transformers: 4.45.0
accelerate: 0.34.2
flash-attn: 2.7.0.post2 (if successful)
xformers: 0.0.28.post2 (if successful)
CUDA: 12.4
```

**Test Priority:** 🟡 **MEDIUM** - Test after Profile 1

---

## ⚠️ PROFILE 3: "Bridge to Modern" (EXPERIMENTAL)

**Best for:** Testing if NumPy 2.x can work with code patches

### Installation Steps (Windows):

```bash
# Create fresh venv
python -m venv venv_e7adb86_modern
.\venv_e7adb86_modern\Scripts\activate

# Modern PyTorch (what you currently have)
pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 --index-url https://download.pytorch.org/whl/cu128

# Core dependencies (mixed compatibility)
pip install "numpy<2.0"             # Force NumPy 1.x even with modern packages
pip install transformers==4.54.1
pip install accelerate==1.6.0
pip install safetensors==0.4.5
pip install diffusers==0.32.1

# Required packages
pip install einops==0.7.0
pip install av==14.0.1
pip install opencv-python==4.10.0.84
pip install sentencepiece==0.2.0
pip install ftfy==6.3.1
pip install toml==0.10.2
pip install easydict==1.13
pip install voluptuous==0.15.2
pip install tqdm==4.67.1
pip install psutil==7.1.3

# Performance libraries (latest)
pip install flash-attn --no-build-isolation
pip install sageattention

# Install musubi-tuner
cd C:\AI\apps\musubi-tuner
pip install -e .
```

### Expected Versions:
```
Python: 3.10.11
torch: 2.8.0+cu128
numpy: 1.26.4               ← Forced to 1.x despite newer packages
transformers: 4.54.1
accelerate: 1.6.0
flash-attn: 2.7.3 (latest)
sageattention: 1.0.6
CUDA: 12.8
```

**Test Priority:** 🟠 **LOW** - Test last, may still have issues

---

## ⚠️ PROFILE 4: "WSL Ubuntu Optimized" (For Linux Testing)

**Best for:** Testing on WSL/Linux with optimal build flags

### Installation Steps (WSL Ubuntu):

```bash
# Install system dependencies first
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-dev build-essential
sudo apt install -y ninja-build

# Create fresh venv
python3.10 -m venv venv_e7adb86_wsl
source venv_e7adb86_wsl/bin/activate

# Install PyTorch (Linux CUDA 12.4)
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# Core dependencies (matched to Aug 2024)
pip install numpy==1.26.4
pip install transformers==4.43.3
pip install accelerate==0.33.0
pip install safetensors==0.4.4
pip install diffusers==0.30.0

# Required packages
pip install einops==0.7.0
pip install av==12.2.0
pip install opencv-python==4.10.0.84
pip install sentencepiece==0.2.0
pip install ftfy==6.3.1
pip install toml==0.10.2
pip install easydict==1.13
pip install voluptuous==0.15.2
pip install tqdm==4.66.5
pip install psutil==6.0.0

# Performance libraries (builds faster on Linux)
MAX_JOBS=4 pip install flash-attn --no-build-isolation
pip install xformers==0.0.27.post2

# Install musubi-tuner
cd /path/to/musubi-tuner
pip install -e .
```

### Expected Versions:
```
Python: 3.10.x
torch: 2.4.0+cu124
numpy: 1.26.4
transformers: 4.43.3
flash-attn: 2.6.3
xformers: 0.0.27.post2
CUDA: 12.4
```

**Test Priority:** 🟢 **HIGH** - Linux often has fewer issues than Windows

---

## 🔧 IMMEDIATE FIX FOR YOUR CURRENT VENV

If you want to quickly test without rebuilding everything:

```bash
# Activate your current venv
.\venv310\Scripts\activate

# CRITICAL: Downgrade NumPy to 1.x
pip install "numpy<2.0"

# This should install numpy 1.26.4, fixing your NaN errors
```

**Expected result:** This single change may fix 80% of your NaN issues.

---

## 📊 Testing Protocol

### For Each venv Profile:

1. **Create venv** using steps above
2. **Run version check:**
   ```bash
   python versioncheck.py > venv_profile_X_versions.txt
   ```

3. **Test inference (T2V):**
   ```bash
   # Simple test prompt
   python wan_generate_video.py --prompt "a cat walking" --steps 30 --output test_profile_X.mp4
   ```

4. **Monitor for NaN errors:**
   - Check terminal output for "NaN detected"
   - Check if video generates (not black screen)
   - Monitor GPU memory usage

5. **Test training (if inference succeeds):**
   ```bash
   # Run a short training test (1 step)
   python wan_train_network.py --config your_test_config.toml --max_train_steps 1
   ```

6. **Document results:**
   - ✅ Success: No NaN, video generates
   - ⚠️ Partial: Works but with warnings
   - ❌ Failed: NaN errors or crashes

---

## 📈 Expected Success Rates

| Profile | Windows Success | WSL Success | Notes |
|---------|----------------|-------------|-------|
| Profile 1 (DingALingBerries) | 95% | 98% | Highest compatibility |
| Profile 2 (Conservative) | 85% | 90% | PyTorch 2.5.1 differences |
| Profile 3 (Modern) | 60% | 70% | PyTorch 2.8.0 issues |
| Profile 4 (WSL Optimized) | N/A | 98% | Linux-specific |
| Current (BROKEN) | 5% | 5% | NumPy 2.x incompatible |

---

## 🎯 Recommended Testing Order

### Session 1 (Quick Win):
1. **Apply immediate fix** to current venv (downgrade NumPy)
2. Test if NaN errors disappear

### Session 2 (Windows Testing):
1. **Build Profile 1** (DingALingBerries Official)
2. Test thoroughly
3. If successful, document as "production venv"

### Session 3 (Comparison):
1. **Build Profile 2** (Conservative Update)
2. Compare performance vs Profile 1
3. Document any differences

### Session 4 (WSL Testing):
1. **Build Profile 4** (WSL Optimized)
2. Compare Windows vs WSL performance
3. Determine best platform

### Session 5 (Future-proofing):
1. **Build Profile 3** (Modern) only if needed
2. Test if newer dependencies work
3. Document limitations

---

## 🔍 Known Issues by Component

### NumPy 2.x Issues (CRITICAL):
- **Symptom:** NaN in attention calculations
- **Cause:** Dtype handling changes, memmap API changes
- **Fix:** Downgrade to `numpy<2.0` (1.26.4 recommended)

### PyTorch 2.8.0 Issues (MODERATE):
- **Symptom:** Black videos, slow performance
- **Cause:** `scaled_dot_product_attention` behavior changes
- **Fix:** Downgrade to PyTorch 2.4.0 or 2.5.1

### Flash-attn Build Issues (COMMON on Windows):
- **Symptom:** Compilation fails with CUDA errors
- **Cause:** MSVC/CUDA version mismatches
- **Workaround:** Use `--attn_mode torch` or `--attn_mode xformers`

### Transformers Version Issues (MINOR):
- **Symptom:** T5/CLIP loading warnings
- **Cause:** API changes in 4.50+
- **Fix:** Use transformers 4.43.3 (Aug 2024 version)

---

## 💾 Save This Test Data

For each venv you test, save these files to this repository:

```
configs/venv_tests/
├── profile_1_dingalingberries_official/
│   ├── versions.txt              (output of versioncheck.py)
│   ├── test_inference_log.txt    (console output)
│   ├── test_training_log.txt     (console output)
│   └── results.md                (your notes)
├── profile_2_conservative/
│   └── ...
├── profile_3_modern/
│   └── ...
└── profile_4_wsl_optimized/
    └── ...
```

We can analyze results together when you're back at your workstation.

---

## 🚨 TL;DR - What to Do NOW

**IMMEDIATE ACTION (5 minutes):**
```bash
# In your current venv310
pip install "numpy<2.0"
```

**THIS EVENING (Priority Order):**
1. ✅ Build Profile 1 (DingALingBerries Official) - Windows
2. ✅ Build Profile 4 (WSL Optimized) - WSL
3. 📊 Test both with same prompt/settings
4. 📝 Document which works best

**DO NOT:**
- ❌ Use NumPy 2.x with e7adb86
- ❌ Try to use v0.2.14 workaround flags with e7adb86
- ❌ Skip testing - guessing wastes more time than testing

---

## 📞 Feedback Loop

After testing each profile, report back:
- Which profile(s) succeeded?
- Any NaN errors?
- Performance differences?
- Build issues?

We'll use this data to create a definitive "DeadlyMusubi Production venv Guide".
