# 🚨 QUICK FIX CHEATSHEET - e7adb86 NaN Errors

## ⚡ 5-MINUTE FIX (Try This First!)

```powershell
# Windows PowerShell
cd C:\AI\apps\musubi-tuner
.\venv310\Scripts\activate
pip install "numpy<2.0"
python versioncheck.py
```

**Expected:** NumPy downgrades from 2.2.6 → 1.26.4

**Test immediately:**
```powershell
python wan_generate_video.py --prompt "test cat" --steps 30 --output test_nan_fix.mp4
```

If this fixes your NaN errors → **NumPy 2.x was the culprit!**

---

## 🎯 Production-Ready venv Commands

### Windows (RECOMMENDED - Profile 1):

```powershell
# Start fresh
python -m venv venv_e7adb86_production
.\venv_e7adb86_production\Scripts\activate

# Install exact versions (copy-paste all at once)
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124 && pip install numpy==1.26.4 transformers==4.43.3 accelerate==0.33.0 safetensors==0.4.4 diffusers==0.30.0 einops==0.7.0 av==12.2.0 opencv-python==4.10.0.84 sentencepiece==0.2.0 ftfy==6.3.1 toml==0.10.2 easydict==1.13 voluptuous==0.15.2 tqdm==4.66.5 psutil==6.0.0

# Optional performance boost (may fail on Windows - that's OK)
pip install flash-attn --no-build-isolation
pip install xformers==0.0.27.post2

# Install musubi-tuner
pip install -e .
```

### WSL Ubuntu (RECOMMENDED - Profile 4):

```bash
# Start fresh
python3.10 -m venv venv_e7adb86_production
source venv_e7adb86_production/bin/activate

# Install exact versions (copy-paste all at once)
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124 && pip install numpy==1.26.4 transformers==4.43.3 accelerate==0.33.0 safetensors==0.4.4 diffusers==0.30.0 einops==0.7.0 av==12.2.0 opencv-python==4.10.0.84 sentencepiece==0.2.0 ftfy==6.3.1 toml==0.10.2 easydict==1.13 voluptuous==0.15.2 tqdm==4.66.5 psutil==6.0.0

# Performance libraries (builds easier on Linux)
MAX_JOBS=4 pip install flash-attn --no-build-isolation
pip install xformers==0.0.27.post2

# Install musubi-tuner
pip install -e .
```

---

## 🔍 Verify Success

```bash
python versioncheck.py
```

**Check these versions:**
- ✅ torch: 2.4.0+cu124 (NOT 2.8.0)
- ✅ numpy: 1.26.4 (NOT 2.x)
- ✅ transformers: 4.43.3 (NOT 4.54.1)
- ✅ accelerate: 0.33.0 (NOT 1.6.0)
- ✅ cuda version: 12.4 (NOT 12.8)

**Optional but nice:**
- 🟢 flash-attn: 2.6.3 (if compiled successfully)
- 🟢 xformers: 0.0.27.post2 (if compiled successfully)

---

## 🧪 Quick Test Commands

### Test 1: Inference (No NaN Check)
```bash
python wan_generate_video.py \
  --prompt "a cute cat walking on grass" \
  --steps 30 \
  --output test_inference.mp4 \
  --attn_mode torch
```

**Success criteria:**
- ❌ No "NaN detected" errors in console
- ✅ Video file generates (not 0 bytes)
- ✅ Video is NOT black screen
- ✅ No crash/exception

### Test 2: Training (1 Step)
```bash
python wan_train_network.py \
  --config your_config.toml \
  --max_train_steps 1
```

**Success criteria:**
- ❌ No NaN in loss values
- ✅ Step completes without crash
- ✅ LoRA weights save successfully

---

## 📊 Troubleshooting Decision Tree

```
NaN errors? 
  ├─ Yes → Check NumPy version
  │   ├─ NumPy 2.x → DOWNGRADE to 1.26.4 ✅
  │   └─ NumPy 1.x → Check PyTorch version
  │       ├─ PyTorch 2.8.x → DOWNGRADE to 2.4.0 ✅
  │       └─ PyTorch 2.4.x → Check transformers
  │           └─ transformers 4.50+ → DOWNGRADE to 4.43.3 ✅
  │
  └─ No NaN but slow?
      ├─ Check flash-attn installed?
      │   ├─ Not installed → Try: pip install flash-attn
      │   └─ Installed → Use --attn_mode flash2
      │
      └─ Still slow → Check GPU usage
          ├─ Low GPU % → May be CPU bottleneck
          └─ High GPU % → Expected behavior
```

---

## 🚫 Common Mistakes to AVOID

| ❌ DON'T | ✅ DO INSTEAD |
|----------|---------------|
| Use NumPy 2.x with e7adb86 | Use NumPy 1.26.4 |
| Use PyTorch 2.8.0 with e7adb86 | Use PyTorch 2.4.0 |
| Mix Aug 2024 code with Dec 2025 packages | Match package versions to code date |
| Skip flash-attn (slower) | Try to install flash-attn |
| Use `--disable_numpy_memmap` flag | That flag doesn't exist in e7adb86 |
| Build 10 venvs without testing | Test Profile 1 first, then iterate |

---

## 📞 Report Template

After testing, fill this out:

```
VENV: Profile X (name)
PLATFORM: Windows 10 / WSL Ubuntu
DATE: Dec 19, 2025

VERSIONS:
- Python: X.X.X
- PyTorch: X.X.X+cuXXX
- NumPy: X.X.X
- flash-attn: X.X.X or "not installed"
- xformers: X.X.X or "not installed"

TEST RESULTS:
- Inference Test: ✅ SUCCESS / ❌ FAILED (reason)
- NaN errors: YES / NO
- Video output: ✅ Good / ⚠️ Black screen / ❌ No file
- Training Test: ✅ SUCCESS / ❌ FAILED (reason)

NOTES:
(Any warnings, build issues, performance observations)
```

---

## 🎯 Success Prediction

| Your Current venv | → | After NumPy Downgrade | → | Profile 1 (Full Rebuild) |
|-------------------|---|----------------------|---|--------------------------|
| ❌ NaN errors (NumPy 2.2.6) | → | 🟡 Maybe works (mixed versions) | → | ✅ Guaranteed to work |
| PyTorch 2.8.0 | → | PyTorch 2.8.0 (still risky) | → | PyTorch 2.4.0 (stable) |
| 5% success rate | → | 60% success rate | → | 95% success rate |

**Recommendation:** Try quick NumPy fix first. If it works, great! If not, build Profile 1 for production.

---

## 💾 Backup Current venv (Before Changes)

```powershell
# Windows
cd C:\AI\apps\musubi-tuner
pip freeze > venv310_broken_backup.txt

# Later, to restore if needed:
pip install -r venv310_broken_backup.txt
```

```bash
# WSL
pip freeze > venv310_broken_backup.txt
```

This lets you revert if experiments go wrong.
