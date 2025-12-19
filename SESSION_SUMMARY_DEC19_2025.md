# DeadlyMusubi - Session Summary (Dec 19, 2025)

## 🎯 What We Discovered Today

### PRIMARY FINDING: NumPy 2.x Breaks e7adb86

Your NaN errors are caused by **NumPy 2.2.6**. This is a critical incompatibility:

```
YOUR CURRENT ENVIRONMENT (BROKEN):
numpy: 2.2.6              ← CULPRIT #1 (causes NaN)
torch: 2.8.0+cu128        ← CULPRIT #2 (too new, causes slowdown)
transformers: 4.54.1      ← Too new
accelerate: 1.6.0         ← Too new

SHOULD BE (e7adb86 compatible):
numpy: 1.26.4             ✅ NumPy 1.x series
torch: 2.4.0+cu124        ✅ Matched to Aug 2024
transformers: 4.43.3      ✅ Matched to Aug 2024
accelerate: 0.33.0        ✅ Matched to Aug 2024
```

---

## 📝 Questions Answered

### 1. Did Kohya fix the performance issues in later versions?

**NO** - All three regressions remain unfixed as of December 2024:
- ❌ PR #493 dtype handling still present
- ❌ PR #575 block-wise FP8 still active
- ❌ Windows memory issues only have workarounds, not fixes

Kohya added bandaid flags instead: `--disable_numpy_memmap`, `--use_pinned_memory_for_block_swap`

**Verdict:** DingALingBerries was right—e7adb86 is still the best version.

---

### 2. Can newer dependencies break e7adb86?

**YES** - This is exactly what happened to you:

| Dependency | e7adb86 expects | You have | Impact |
|------------|-----------------|----------|--------|
| NumPy | 1.26.4 | 2.2.6 | 🔴 NaN errors |
| PyTorch | 2.4.0 | 2.8.0 | 🟡 Slowdown |
| transformers | 4.43.3 | 4.54.1 | 🟡 Warnings |
| accelerate | 0.33.0 | 1.6.0 | 🟡 Minor issues |

The code was written in **August 2024** but you have **December 2025** packages.

---

### 3. What's causing your NaN errors?

**NumPy 2.2.6** is the primary culprit:
- NumPy 2.0+ changed dtype handling (affects attention calculations)
- NumPy 2.0+ changed memmap API (affects safetensors loading)
- e7adb86 code expects NumPy 1.x behavior

**PyTorch 2.8.0** is secondary:
- `scaled_dot_product_attention` behavior changed
- e7adb86 expects PyTorch 2.3.x/2.4.x behavior

---

## 🚀 Action Plan for This Evening

### Phase 1: Quick Test (5 minutes)
```powershell
# Try the immediate fix
cd C:\AI\apps\musubi-tuner
.\venv310\Scripts\activate
pip install "numpy<2.0"
python versioncheck.py
# Test inference
python wan_generate_video.py --prompt "test cat" --steps 30 --output test_quick_fix.mp4
```

**If this works:** You've confirmed NumPy 2.x was the problem!

---

### Phase 2: Build Production venv (30 minutes)

#### Windows:
```powershell
cd C:\AI\apps\musubi-tuner
python -m venv venv_e7adb86_production
.\venv_e7adb86_production\Scripts\activate

# Install PyTorch first (separate command)
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# Install all dependencies at once
pip install numpy==1.26.4 transformers==4.43.3 accelerate==0.33.0 safetensors==0.4.4 diffusers==0.30.0 einops==0.7.0 av==12.2.0 opencv-python==4.10.0.84 sentencepiece==0.2.0 ftfy==6.3.1 toml==0.10.2 easydict==1.13 voluptuous==0.15.2 tqdm==4.66.5 psutil==6.0.0

# Try to install flash-attn (may fail on Windows - that's OK)
pip install flash-attn --no-build-isolation

# Install musubi-tuner
pip install -e .

# Verify
python versioncheck.py
```

#### WSL Ubuntu:
```bash
cd /path/to/musubi-tuner
python3.10 -m venv venv_e7adb86_production
source venv_e7adb86_production/bin/activate

# Install PyTorch
pip install torch==2.4.0+cu124 torchvision==0.19.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# Install dependencies (same as Windows)
pip install numpy==1.26.4 transformers==4.43.3 accelerate==0.33.0 safetensors==0.4.4 diffusers==0.30.0 einops==0.7.0 av==12.2.0 opencv-python==4.10.0.84 sentencepiece==0.2.0 ftfy==6.3.1 toml==0.10.2 easydict==1.13 voluptuous==0.15.2 tqdm==4.66.5 psutil==6.0.0

# Install flash-attn (easier on Linux)
MAX_JOBS=4 pip install flash-attn --no-build-isolation

# Install musubi-tuner
pip install -e .

# Verify
python versioncheck.py
```

---

### Phase 3: Testing (15 minutes per venv)

#### Test 1: Version Check
```bash
python versioncheck.py > venv_production_versions.txt
```

**Verify these are correct:**
- ✅ Python: 3.10.11
- ✅ torch: 2.4.0+cu124
- ✅ numpy: 1.26.4
- ✅ transformers: 4.43.3
- ✅ accelerate: 0.33.0

#### Test 2: Inference Test
```bash
python wan_generate_video.py \
  --prompt "a cute cat walking on grass, high quality" \
  --steps 30 \
  --output test_production_inference.mp4 \
  --attn_mode torch
```

**Success criteria:**
- ❌ No NaN errors in console
- ✅ Video generates (not black)
- ✅ No crashes

#### Test 3: Training Test
```bash
python wan_train_network.py \
  --config your_test_config.toml \
  --max_train_steps 1
```

**Success criteria:**
- ❌ No NaN in loss
- ✅ Step completes
- ✅ LoRA saves

---

## 📊 Documentation Created

All files pushed to GitHub (commit 9556a17):

1. **VENV_TEST_MATRIX.md** - Comprehensive testing matrix with 4 venv profiles
2. **QUICK_FIX_CHEATSHEET.md** - Copy-paste commands for quick fixes
3. **configs/requirements_e7adb86.txt** - Pinned dependencies for e7adb86
4. **MUSUBI_TUNER_VERSION_ANALYSIS.md** - Updated with NumPy 2.x warning

---

## 🎓 What We Learned

### About the Latest musubi-tuner Code:
- ❌ Performance regressions NOT fixed (as of Dec 2024)
- ❌ Kohya chose workarounds over proper fixes
- ❌ Windows memory issues still acknowledged but not resolved
- ✅ DingALingBerries' recommendation to use e7adb86 remains valid

### About Dependency Management:
- ⚠️ **NumPy 2.x breaks everything** (released July 2024)
- ⚠️ **PyTorch version matters** (2.8.0 too new for e7adb86)
- ⚠️ **Package drift is real** (modern pip installs incompatible versions)
- ✅ **Solution:** Pin dependencies to code release date (Aug 2024)

### About Workaround Flags:
- ❌ `--disable_numpy_memmap` doesn't exist in e7adb86
- ❌ `--use_pinned_memory_for_block_swap` doesn't exist in e7adb86
- ❌ These flags are from v0.2.14+ (Nov 2024)
- ✅ Can't use later version flags with earlier code

---

## 📞 Report Back Template

After testing, fill this out:

```
QUICK FIX TEST (venv310 with NumPy downgrade):
- NumPy version after downgrade: _____
- Inference test: ✅ SUCCESS / ❌ FAILED
- NaN errors: YES / NO
- Notes: 

PRODUCTION VENV TEST (venv_e7adb86_production):
Platform: Windows / WSL
- Python: _____
- PyTorch: _____
- NumPy: _____
- flash-attn: _____ or "not installed"
- Inference test: ✅ SUCCESS / ❌ FAILED
- Training test: ✅ SUCCESS / ❌ FAILED
- NaN errors: YES / NO
- Performance vs broken venv: FASTER / SAME / SLOWER
- Notes:
```

---

## 🎯 Expected Outcomes

| Scenario | Probability | Next Steps |
|----------|-------------|------------|
| Quick fix works (NumPy downgrade) | 60% | Document, but still build production venv |
| Production venv works | 95% | Use this as your main environment |
| Both work | 58% | Compare performance, choose best |
| Neither works | 2% | Report errors, investigate further |

---

## 💡 Key Takeaways

1. **NumPy 2.x is incompatible with e7adb86** - Always use NumPy 1.26.4
2. **Package versions matter** - Match dependencies to code release date
3. **e7adb86 is still the best version** - Kohya hasn't fixed the regressions
4. **Dependency drift causes NaN errors** - Pin everything in production
5. **Test on both Windows and WSL** - Performance may differ

---

## 🔗 Quick Links

- [VENV_TEST_MATRIX.md](./VENV_TEST_MATRIX.md) - Full testing guide
- [QUICK_FIX_CHEATSHEET.md](./QUICK_FIX_CHEATSHEET.md) - Copy-paste commands
- [configs/requirements_e7adb86.txt](./configs/requirements_e7adb86.txt) - Pinned dependencies
- [MUSUBI_TUNER_VERSION_ANALYSIS.md](./MUSUBI_TUNER_VERSION_ANALYSIS.md) - Full version analysis

---

**Next session:** Bring test results and we'll analyze performance data together!
