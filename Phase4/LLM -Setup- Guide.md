# LLM Server Setup and Model Deployment Guide

This document records the complete setup process for running a local LLM on the university GPU server, including VM provisioning, system configuration, NVIDIA driver and CUDA installation, Python environment setup, GPU-enabled `llama-cpp-python` installation, and model deployment.

---

# 1. VM Setup and GPU Environment

## 1.1 VM Overview

A dedicated VM was created on the university SVC5/CloudStack infrastructure for GPU-based LLM inference.

**VM specifications:**

* **OS:** Ubuntu 22.04.2 LTS
* **GPU:** NVIDIA A100 SXM4 80GB
* **vCPU:** 32
* **RAM:** ~117 GiB
* **System disk:** ~80 GB
* **Data disk:** ~150 GB
* **Internal IP:** `172.30.35.75`

The university FortiClient VPN is required to access the internal VM network.

---

## 1.2 Initial SSH Access

The VM was initially accessed using the root account:

```bash
ssh root@172.30.35.75
```

Basic system information was checked:

```bash
whoami
hostname
lsb_release -a
uname -a
lscpu | head -20
free -h
df -h
```

A separate sudo user was then created for regular administration:

```bash
adduser user
adduser user sudo
id user
```

The new account was verified:

```bash
su - user
whoami
sudo -v
```

---

# 2. Network and System Configuration

## 2.1 Ubuntu Package Mirror

The default Ubuntu mirror was replaced because of package/network access problems.

```bash
sudo sed -i 's/nl3.archive.ubuntu.com/mirror.arvancloud.ir/g' /etc/apt/sources.list
```

The configured mirror was checked with:

```bash
grep -R "mirror.arvancloud.ir" /etc/apt/sources.list
```

---

## 2.2 DNS Configuration

`systemd-resolved` was disabled and the resolver configuration was replaced with the accessible DNS servers:

```bash
sudo systemctl disable systemd-resolved.service
sudo rm -rf /etc/resolv.conf
```

A new resolver configuration was created:

```bash
sudo tee /etc/resolv.conf > /dev/null <<EOF
nameserver 194.225.228.4
nameserver 194.225.228.5
search cs2cloud.internal
EOF
```

DNS resolution was checked:

```bash
cat /etc/resolv.conf
getent hosts archive.ubuntu.com
```

---

## 2.3 Disable IPv6

IPv6 was disabled to avoid network-related issues during the setup:

```bash
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOF
```

The configuration was applied:

```bash
sudo sysctl -p
```

---

## 2.4 System Update and Required Packages

The system packages were updated:

```bash
sudo apt update
sudo apt upgrade -y
```

Basic build and Python packages were installed:

```bash
sudo apt install -y build-essential git cmake python3 python3-venv python3-pip
```

The NVIDIA driver detection utility was also installed:

```bash
sudo apt install -y ubuntu-drivers-common
```

---

# 3. NVIDIA GPU and Driver Setup

## 3.1 GPU Detection

Detect the installed GPU:

```bash
lshw -C display
lspci | grep -i nvidia
```

Check available NVIDIA drivers:

```bash
ubuntu-drivers devices
```

The detected GPU was:

```text
NVIDIA A100 SXM4 80GB
```

## 3.2 Initial Driver Installation Attempt

The mentor initially recommended:

```bash
sudo apt-get install -y cuda-drivers-550
```

Fallback:

```bash
sudo apt-get install -y cuda-drivers
```

Because the NVIDIA repository was not directly accessible from the VM, the local repository installation path was used instead.

## 3.3 NVIDIA Driver Installation

The required CUDA 12.4 local repository package was transferred to the VM.

The package used was:

```text
cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
```

Install the local repository package:

```bash
sudo dpkg -i cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
```

Install the repository key:

```bash
sudo cp /var/cuda-repo-ubuntu2204-12-4-local/cuda-87AE4CD8-keyring.gpg \
  /usr/share/keyrings/
```

Update package lists:

```bash
sudo apt update
```

Install the NVIDIA 550 driver:

```bash
sudo apt install -y cuda-drivers-550
```

Reboot the VM:

```bash
sudo reboot
```

After reconnecting, verify the driver:

```bash
nvidia-smi
```

Final driver:

```text
NVIDIA Driver 550.54.14
```

---

# 4. CUDA Toolkit Setup

## 4.1 Initial CUDA Installation Attempt

The mentor initially recommended CUDA Toolkit 12.3:

```bash
sudo apt install -y cuda-toolkit-12-3
```

Due to repository/package access issues, CUDA 12.4 was installed instead.

## 4.2 CUDA Repository Package

The CUDA repository package was first downloaded on the local Ubuntu machine:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
```

It was then transferred to the VM:

```bash
scp cuda-keyring_1.1-1_all.deb user@172.30.35.75:~/
```

On the VM, install it:

```bash
sudo dpkg -i ~/cuda-keyring_1.1-1_all.deb
```

Update the package lists:

```bash
sudo apt update
```

## 4.3 CUDA Toolkit 12.4

Install CUDA Toolkit 12.4:

```bash
sudo apt install -y cuda-toolkit-12-4
```

Verify the CUDA compiler:

```bash
nvcc --version
```

If necessary, verify the compiler location:

```bash
ls -l /usr/local/cuda-12.4/bin/nvcc
```

The final CUDA Toolkit version was **12.4**.

## 4.4 CUDA Environment Variables

Add CUDA 12.4 to `PATH`:

```bash
echo 'export PATH=/usr/local/cuda-12.4/bin:$PATH' >> ~/.bashrc
```

Add CUDA libraries:

```bash
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
```

Reload the environment:

```bash
source ~/.bashrc
```

Verify:

```bash
which nvcc
nvcc --version
```

---

# 5. Python LLM Environment

Create a dedicated virtual environment:

```bash
python3 -m venv ~/llm-env
```

Activate it:

```bash
source ~/llm-env/bin/activate
```

Check Python and pip:

```bash
python --version
pip --version
```

Upgrade pip:

```bash
pip install --upgrade pip
```

---

# 6. GPU-Enabled llama.cpp Python Runtime

The mentor initially provided:

```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 \
python -m pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
```

The command actually used for the final installation was:

```bash
CMAKE_ARGS="-DGGML_CUDA=ON" FORCE_CMAKE=1 \
python -m pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
```

Verify the installation:

```bash
pip show llama-cpp-python
```

Installed version:

```text
0.3.35
```

`GGML_CUDA=ON` enables CUDA support so `llama-cpp-python` can use the A100 GPU for inference.

---

# 7. Model Deployment

## 7.1 Qwen3.8-27B Model

The Qwen3.8-27B GGUF model was downloaded from Hugging Face.

The model was stored in:

```text
/data/Qwen3.8-27B-BF16/BF16/
```

Download the BF16 model files:

```bash
hf download unsloth/Qwen3.8-27B-GGUF \
  --include "BF16/*" \
  --local-dir /data/Qwen3.8-27B-BF16
```

The model consists of two GGUF shards:

```text
Qwen3.8-27B-BF16-00001-of-00002.gguf
Qwen3.8-27B-BF16-00002-of-00002.gguf
```

Verify the downloaded files:

```bash
ls -lh /data/Qwen3.8-27B-BF16/BF16/
```

# 8. Inference Script Adaptation and Model Run

## 8.1 Adapting `run_inference.py` for Qwen3.8-27B

The original `run_inference.py` v8.0 was designed for **Qwen3-Coder-Next**. The script was adapted for **Qwen3.8-27B** and the updated triage input.

The main changes were:

* Updated the model path from Qwen3-Coder-Next to the Qwen3.8-27B BF16 model.
* Updated the input file to `llm_triage_batches_with_cwe.json`.
* Updated the output file to `llm_triage_results_Pilot_Qwen3.8.json`.
* Added **CWE information** to the prompt as additional static-analysis context.
* Added an instruction that CWE information must not be treated as proof of exploitability.
* Added fallback field names in `build_prompt()` to support both the original and alternative JSON field naming conventions.
* Updated the model initialization message to identify Qwen3.8-27B.
* The existing inference logic was retained, including:

  * 3-vote majority voting
  * hallucination checks
  * human-review flags
  * deterministic overrides
  * full source code
  * RAG context
  * semantic profile
  * local code snippets

### Main Configuration

```python
MODEL_PATH = "/data/Qwen3.8-27B-BF16/BF16/Qwen3.8-27B-BF16-00001-of-00002.gguf"
INPUT_JSON = "/home/user/llm_triage_batches_with_cwe.json"
OUTPUT_JSON = "/home/user/llm_triage_results_Pilot_Qwen3.8.json"
NUM_VOTES = 3
```

The inference runtime continued to use GPU offloading and a large context window:

```python
n_gpu_layers = -1
n_ctx = 98304
n_batch = 8192
use_mlock = True
flash_attn = True
```

## 8.2 Running the Inference

Because the inference was expected to run for many hours, it was executed inside a **`tmux` session** on the university GPU VM. This allowed the process to continue running after disconnecting from the SSH session.

Create and enter a `tmux` session:

```bash
tmux new -s llm-inference
```

Activate the Python environment:

```bash
source ~/llm-env/bin/activate
```

Run the inference script:

```bash
python /home/user/run_inferencev9.py
```

To detach from the session while keeping the process running:

```text
Ctrl+B
D
```

To reattach to the running session:

```bash
tmux attach -t llm-inference
```

Active `tmux` sessions can be listed with:

```bash
tmux ls
```

## 8.3 Qwen3.8-27B Inference Run

The Qwen3.8-27B inference was run on the **NVIDIA A100 80GB GPU VM** using the `llm-env` Python environment and the GPU-enabled `llama-cpp-python` runtime.

The run processed **140 batches** before being stopped. The total runtime was approximately **21 hours and 30 minutes**.

The run was stopped at that point because continuing through the remaining batches would require an impractically long amount of time.

The main factors contributing to the long runtime were:

* **Low decoding throughput** relative to the size of the workload.
* **Long model-generated reasoning**, which resulted in thousands of generated tokens for individual votes.
* **Three inference votes per finding**, which effectively multiplied the inference cost.
* **Large-context inputs** containing source code, RAG context, semantic information, and finding details.

During the run, decoding throughput was approximately **26 tokens/second**. For example, one finding required three votes with the following generation times:

| Vote      | Generated Tokens |                    Time |
| --------- | ---------------: | ----------------------: |
| Vote 1    |           10,349 |                 531.4 s |
| Vote 2    |            3,823 |                 189.3 s |
| Vote 3    |            4,839 |                 232.9 s |
| **Total** |       **19,011** | **953.7 s (~15.9 min)** |

This illustrates why the complete dataset required substantial processing time: each finding could involve three relatively long generations, while the prompt itself also contained a large amount of contextual information.

---
# 9. Second Model and Full Inference Run

## 9.1 Downloading and Preparing the Second Model

As a second model, **Qwen3.6-35B-A3B** was tested. It uses a **Sparse Mixture-of-Experts (MoE)** architecture with approximately **35B total parameters and 3B active parameters per token**.

For inference, the **UD-Q8_K_XL quantized GGUF** version was used. Quantization reduces memory requirements while allowing the model to be run locally using the GPU-enabled `llama-cpp-python` runtime.

The model was downloaded from the Unsloth Hugging Face repository:

```bash
hf download unsloth/Qwen3.6-35B-A3B-GGUF \
  --include "Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf" \
  --local-dir /data/Qwen3.6-35B-A3B-Q8
```

The resulting model file was stored under:

```text
/data/Qwen3.6-35B-A3B-Q8/
```

## 9.2 Full Inference Run

The **same inference commands and `tmux` setup described in the previous section** were used to run the second model. No changes were made to the execution procedure.

Unlike the previous Qwen3.8-27B run, where processing was stopped after 140 batches, this run completed the **entire dataset of 226 batches**.

| Metric            |                Result |
| ----------------- | --------------------: |
| Total batches     |               **226** |
| Completed batches |               **226** |
| Completion        |              **100%** |
| Total runtime     |       **482 minutes** |
| Approx. runtime   | **8 hours 2 minutes** |

The complete set of **226 batches** was successfully processed in approximately **482 minutes (8 hours and 2 minutes)**.

---

# 10. Qwen3.6 Result Analysis

After completing the Qwen3.6 inference run, the generated results were analyzed using the following scripts:

* [analyze_qwen36.py](analyze_qwen36.py) — performs the full statistical analysis of the Qwen3.6 results.
* [compare_models.py](compare_models.py) — compares Qwen3.6 and Qwen3.8 on the common, consistently mapped batch range.

### Batch Configuration and Result Selection

The final dataset contains **226 batches**, with one finding per batch.

Before generating the final dataset, smaller pilot configurations were used:

* **Qwen3.8-27B:** an initial pilot was generated with `MAX_TEST_FINDINGS = 10`.
* **Qwen3.6-35B-A3B:** an initial pilot was generated with `MAX_TEST_FINDINGS = 5`.
* The batch builder was then regenerated for the final **226-finding dataset**.

The batch builder first selects the requested number of findings and then groups them by source file before assigning `batch_id` values. As a result, changing `MAX_TEST_FINDINGS` can change the final ordering and numbering of batches. Therefore, an earlier pilot `batch_id` cannot be assumed to represent the same finding as the same `batch_id` in the final 226-batch dataset.

For this reason, the earlier pilot batch numbers were not used directly when selecting the final analysis range. Instead, the final analysis was performed using the results associated with the final dataset.

For the current analysis:

* Qwen3.6 analysis covers **batches 6–226 = 221 analyzed findings**.
* Qwen3.8 analysis excludes its initial pilot results from the final statistical analysis.
* The direct Qwen3.6 vs. Qwen3.8 comparison uses **batches 11–140 = 130 findings**, because this is the range for which results from both models were available and consistently mapped.

---

## 10.1 Qwen3.6 Full Statistical Analysis

The full Qwen3.6 analysis was performed using:

```text
analyze_qwen36.py
```

The script reads:

```text
llm_triage_results_Pilot_Qwen3.6.json
```

and, when available, uses:

```text
/home/nazanin/Projects/bird-2.17.1/reports/llm_triage/llm_triage_batches_with_cwe.json
```

to recover metadata such as finding severity.

The analysis uses the result stored in:

```text
verdict_array[0]
```

and extracts the main verdict, confidence, pattern name, vote details, and model-generated reliability/hallucination metadata.

The complete analysis output was:

```text
========================================================================
QWEN3.6 — FULL ANALYSIS
========================================================================
Input results      : llm_triage_results_Pilot_Qwen3.6.json
Batch input        : /home/nazanin/Projects/bird-2.17.1/reports/llm_triage/llm_triage_batches_with_cwe.json
Ignored batches    : 1-5
Analyzed batches   : 6-226
Analyzed findings  : 221

========================================================================
VERDICT DISTRIBUTION
========================================================================
VULN    :    3 (  1.4%)
SMELL   :   47 ( 21.3%)
FP      :  169 ( 76.5%)
UNKNOWN :    2 (  0.9%)

========================================================================
CONFIDENCE
Confidence scale: 1-10
========================================================================
Average : 8.661/10
Minimum : 1.0/10
Maximum : 10.0/10

Confidence distribution:
1-3   :    2 (  0.9%)
4-6   :   10 (  4.5%)
7-8   :   56 ( 25.3%)
9-10  :  153 ( 69.2%)

========================================================================
CONFIDENCE BY VERDICT
========================================================================
VULN    :    3 findings | average confidence = 9.000/10
SMELL   :   47 findings | average confidence = 7.574/10
FP      :  169 findings | average confidence = 9.047/10
UNKNOWN :    2 findings | average confidence = 1.000/10

========================================================================
3-VOTE CONSISTENCY
========================================================================
Findings     : 221
Consistent   : 174
Inconsistent : 47
Consistency  : 78.7%

========================================================================
3-VOTE PATTERNS
========================================================================
 150  FP / FP / FP
  22  SMELL / SMELL / SMELL
  12  SMELL / FP / SMELL
  10  FP / FP / SMELL
   9  FP / SMELL / SMELL
   6  SMELL / FP / FP
   3  FP / SMELL / FP
   3  SMELL / SMELL / FP
   2  VULN / VULN / VULN
   1  SMELL / VULN / SMELL
   1  SMELL / VULN / VULN

========================================================================
VERDICT DISTRIBUTION BY TOOL
========================================================================

SonarQube
----------------------------------------
Total: 50
  VULN    :    0 (  0.0%)
  SMELL   :   10 ( 20.0%)
  FP      :   38 ( 76.0%)
  UNKNOWN :    2 (  4.0%)

CodeQL
----------------------------------------
Total: 70
  VULN    :    2 (  2.9%)
  SMELL   :   10 ( 14.3%)
  FP      :   58 ( 82.9%)
  UNKNOWN :    0 (  0.0%)

Cppcheck
----------------------------------------
Total: 59
  VULN    :    1 (  1.7%)
  SMELL   :   25 ( 42.4%)
  FP      :   33 ( 55.9%)
  UNKNOWN :    0 (  0.0%)

Semgrep
----------------------------------------
Total: 42
  VULN    :    0 (  0.0%)
  SMELL   :    2 (  4.8%)
  FP      :   40 ( 95.2%)
  UNKNOWN :    0 (  0.0%)

========================================================================
VERDICT DISTRIBUTION BY SEVERITY
========================================================================

Severity: BLOCKER
Total   : 22
  VULN    :    0 (  0.0%)
  SMELL   :    6 ( 27.3%)
  FP      :   15 ( 68.2%)
  UNKNOWN :    1 (  4.5%)

Severity: CRITICAL
Total   : 25
  VULN    :    0 (  0.0%)
  SMELL   :    1 (  4.0%)
  FP      :   24 ( 96.0%)
  UNKNOWN :    0 (  0.0%)

Severity: MAJOR
Total   : 174
  VULN    :    3 (  1.7%)
  SMELL   :   40 ( 23.0%)
  FP      :  130 ( 74.7%)
  UNKNOWN :    1 (  0.6%)

========================================================================
TOP RULES BY NUMBER OF FINDINGS
========================================================================
  42  external_Semgrep:c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn  [SMELL=2, FP=40, VULN=0, UNKNOWN=0]
  24  external_CodeQL:cpp/type-confusion  [SMELL=0, FP=24, VULN=0, UNKNOWN=0]
  18  external_Cppcheck:ignoredReturnValue  [SMELL=11, FP=7, VULN=0, UNKNOWN=0]
  18  c:S2259  [SMELL=3, FP=14, VULN=0, UNKNOWN=1]
  17  external_Cppcheck:allocaCalled  [SMELL=12, FP=4, VULN=1, UNKNOWN=0]
  17  external_Cppcheck:uninitvar  [SMELL=0, FP=17, VULN=0, UNKNOWN=0]
  15  c:S3519  [SMELL=3, FP=11, VULN=0, UNKNOWN=1]
  12  external_CodeQL:cpp/multiplication-overflow-in-alloc  [SMELL=1, FP=11, VULN=0, UNKNOWN=0]
  12  external_CodeQL:cpp/suspicious-pointer-scaling-void  [SMELL=0, FP=12, VULN=0, UNKNOWN=0]
   5  external_CodeQL:cpp/alloca-in-loop  [SMELL=3, FP=0, VULN=2, UNKNOWN=0]
   4  external_CodeQL:cpp/unbounded-write  [SMELL=1, FP=3, VULN=0, UNKNOWN=0]
   3  c:S6069  [SMELL=0, FP=3, VULN=0, UNKNOWN=0]
   3  c:S836  [SMELL=0, FP=3, VULN=0, UNKNOWN=0]
   3  c:S946  [SMELL=0, FP=3, VULN=0, UNKNOWN=0]
   3  external_CodeQL:cpp/suspicious-allocation-size  [SMELL=0, FP=3, VULN=0, UNKNOWN=0]
   3  c:S5000  [SMELL=3, FP=0, VULN=0, UNKNOWN=0]
   2  external_CodeQL:cpp/sign-conversion-pointer-arithmetic  [SMELL=0, FP=2, VULN=0, UNKNOWN=0]
   2  external_Cppcheck:nullPointerRedundantCheck  [SMELL=0, FP=2, VULN=0, UNKNOWN=0]
   2  external_Cppcheck:nullPointer  [SMELL=0, FP=2, VULN=0, UNKNOWN=0]
   2  external_CodeQL:cpp/suspicious-pointer-scaling  [SMELL=0, FP=2, VULN=0, UNKNOWN=0]

========================================================================
RULES WITH MOST SMELL CLASSIFICATIONS
========================================================================
  12 SMELL /   17 total  external_Cppcheck:allocaCalled
  11 SMELL /   18 total  external_Cppcheck:ignoredReturnValue
   3 SMELL /   18 total  c:S2259
   3 SMELL /   15 total  c:S3519
   3 SMELL /    3 total  c:S5000
   3 SMELL /    5 total  external_CodeQL:cpp/alloca-in-loop
   2 SMELL /   42 total  external_Semgrep:c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn
   2 SMELL /    2 total  external_CodeQL:cpp/memory-unsafe-function-scan
   1 SMELL /    1 total  external_Cppcheck:nullPointerArithmeticRedundantCheck
   1 SMELL /    4 total  external_CodeQL:cpp/unbounded-write
   1 SMELL /   12 total  external_CodeQL:cpp/multiplication-overflow-in-alloc
   1 SMELL /    1 total  external_Cppcheck:selfAssignment
   1 SMELL /    1 total  external_CodeQL:cpp/integer-multiplication-cast-to-long
   1 SMELL /    1 total  external_CodeQL:cpp/world-writable-file-creation
   1 SMELL /    1 total  external_CodeQL:cpp/path-injection
   1 SMELL /    1 total  c:S2612

========================================================================
RELIABILITY / HALLUCINATION METADATA
========================================================================
Analyzed findings : 221

HUMAN REVIEW REQUIRED
----------------------------------------
True           :   14 (  6.3%)
False          :  207 ( 93.7%)

HALLUCINATION SUSPECT
----------------------------------------
True           :    6 (  2.7%)
False          :  215 ( 97.3%)

HALLUCINATION FLAGS
----------------------------------------
Findings with flags :    6 (  2.7%)
Total flags         : 8

Flag types:
     3  Function 'NODE_NEXT' in evidence not found in source
     1  FP verdict but evidence contains only vulnerability-language keywords
     1  Invented line number 713 (file has 491 lines)
     1  Function 'NODE_VALID' in evidence not found in source
     1  Function 'STACK_BUFFER_INIT' in evidence not found in source
     1  Function 'while' in evidence not found in source

========================================================================
UNKNOWN FINDINGS
========================================================================
Total UNKNOWN: 2
Batch 136 | Rule: c:S2259 | Confidence: 1.0
Batch 160 | Rule: c:S3519 | Confidence: 1.0

========================================================================
LOW-CONFIDENCE FINDINGS (confidence <= 6)
========================================================================
Total: 12
Batch 136 | UNKNOWN | confidence=1.0 | SonarQube  | c:S2259
Batch 160 | UNKNOWN | confidence=1.0 | SonarQube  | c:S3519
Batch  42 | SMELL   | confidence=5.0 | SonarQube  | c:S2259
Batch  43 | SMELL   | confidence=5.0 | SonarQube  | c:S2259
Batch  44 | FP      | confidence=5.0 | SonarQube  | c:S836
Batch  45 | SMELL   | confidence=5.0 | SonarQube  | c:S3519
Batch  66 | FP      | confidence=5.0 | SonarQube  | c:S3519
Batch  99 | SMELL   | confidence=5.0 | SonarQube  | c:S2259
Batch  48 | SMELL   | confidence=6.0 | SonarQube  | c:S3519
Batch  49 | SMELL   | confidence=6.0 | SonarQube  | c:S3519
Batch  70 | SMELL   | confidence=6.0 | CodeQL     | external_CodeQL:cpp/multiplication-overflow-in-alloc
Batch 102 | SMELL   | confidence=6.0 | Cppcheck   | external_Cppcheck:allocaCalled

========================================================================
SUMMARY
========================================================================
Qwen3.6 findings analyzed : 221
Ignored batches            : 1-5
Analyzed batches           : 6-226

VULN    : 3
SMELL   : 47
FP      : 169
UNKNOWN : 2
Average confidence        : 8.661/10
Vote consistency          : 78.7%
Low-confidence findings   : 12

Low-confidence CSV        : qwen36_analysis_low_confidence.csv

Analysis complete.
```

### Interpretation of Qwen3.6 Analysis

The analysis covered **221 findings** from the final batch configuration. The model classified 169 findings as `FP`, 47 as `SMELL`, 3 as `VULN`, and 2 as `UNKNOWN`.

The average confidence was **8.661/10**, with 69.2% of findings receiving a confidence score between 9 and 10.

The three-vote process produced consistent verdicts for **174 findings (78.7%)**, while 47 findings had disagreement between the three votes.

The reliability metadata identified:

* 14 findings requiring human review.
* 6 findings marked as potentially containing hallucinated evidence.
* 6 findings containing non-empty hallucination flags.
* 8 hallucination flags in total.

These hallucination and human-review fields are **model-generated indicators**, not independently verified ground-truth labels. They should therefore be treated as signals for further inspection rather than definitive evidence of incorrect reasoning.

The generated low-confidence findings were also exported to:

```text
qwen36_analysis_low_confidence.csv
```

---

## 10.2 Qwen3.6 vs Qwen3.8 Comparison

The two models were compared using:

```text
compare_models.py
```

Because the first 10 Qwen3.8 batches and first 5 Qwen3.6 batches were generated under different earlier batch configurations, the comparison uses the shared final configuration:

```text
Batch 11–140
```

This produces **130 common findings** for direct comparison.

The comparison is based on the fields available in the model outputs and aligns the corresponding findings across the two model runs.

The complete comparison output was:

```text
========================================================================
QWEN3.6 vs QWEN3.8 — STATISTICAL COMPARISON
========================================================================
Comparison range : Batch 11-140
Qwen3.6 findings : 130
Qwen3.8 findings : 130
Common findings  : 130

========================================================================
Qwen3.6
========================================================================
Total findings: 130

VULN     :   0 (  0.0%)
SMELL    :  25 ( 19.2%)
FP       : 104 ( 80.0%)
UNKNOWN  :   1 (  0.8%)

Confidence (scale 1-10)
Average : 8.685
Minimum : 1.0
Maximum : 10.0

Confidence distribution:
1-3    :   1 (  0.8%)
4-6    :  10 (  7.7%)
7-8    :  24 ( 18.5%)
9-10   :  95 ( 73.1%)

========================================================================
Qwen3.8
========================================================================
Total findings: 130

VULN     :   0 (  0.0%)
SMELL    :  47 ( 36.2%)
FP       :  79 ( 60.8%)
UNKNOWN  :   4 (  3.1%)

Confidence (scale 1-10)
Average : 7.315
Minimum : 1.0
Maximum : 9.0

Confidence distribution:
1-3    :   4 (  3.1%)
4-6    :  34 ( 26.2%)
7-8    :  54 ( 41.5%)
9-10   :  38 ( 29.2%)

========================================================================
DIRECT AGREEMENT
========================================================================
Common findings : 130
Same verdict    : 90 (69.2%)
Different       : 40 (30.8%)

========================================================================
VERDICT AGREEMENT MATRIX
Rows    = Qwen3.6 verdict
Columns = Qwen3.8 verdict
========================================================================
Qwen3.6 / Qwen3.8   VULN      SMELL     FP        UNKNOWN   
VULN                 0         0         0         0
SMELL                0        18         6         1
FP                   0        29        72         3
UNKNOWN              0         0         1         0

========================================================================
DISAGREEMENT DIRECTIONS
Format: Qwen3.6 verdict -> Qwen3.8 verdict
========================================================================
FP -> SMELL          :  29 ( 72.5%)
SMELL -> FP          :   6 ( 15.0%)
FP -> UNKNOWN        :   3 (  7.5%)
SMELL -> UNKNOWN     :   1 (  2.5%)
UNKNOWN -> FP        :   1 (  2.5%)

========================================================================
DISAGREEMENTS BY TOOL
Counts refer to findings where Qwen3.6 and Qwen3.8 disagreed.
========================================================================
SonarQube    :  13 ( 32.5%)
CodeQL       :  11 ( 27.5%)
Cppcheck     :  11 ( 27.5%)
Semgrep      :   5 ( 12.5%)

========================================================================
DISAGREEMENTS BY TOOL AND DIRECTION
Direction: Qwen3.6 verdict -> Qwen3.8 verdict
========================================================================
CodeQL       | FP -> SMELL          : 10
SonarQube    | FP -> SMELL          : 9
Cppcheck     | SMELL -> FP          : 6
Cppcheck     | FP -> SMELL          : 5
Semgrep      | FP -> SMELL          : 5
SonarQube    | FP -> UNKNOWN        : 3
CodeQL       | SMELL -> UNKNOWN     : 1
SonarQube    | UNKNOWN -> FP        : 1

========================================================================
TOP RULES WITH MOST DISAGREEMENTS
========================================================================
  8  external_CodeQL:cpp/multiplication-overflow-in-alloc
  5  external_Semgrep:c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn
  5  c:S3519
  4  external_Cppcheck:ignoredReturnValue
  3  external_Cppcheck:allocaCalled
  3  c:S2259
  2  external_CodeQL:cpp/sign-conversion-pointer-arithmetic
  2  c:S836
  2  external_Cppcheck:nullPointer
  2  c:S946
  1  external_Cppcheck:nullPointerRedundantCheck
  1  c:S3949
  1  external_Cppcheck:selfAssignment
  1  external_CodeQL:cpp/integer-multiplication-cast-to-long

========================================================================
CONFIDENCE COMPARISON
Confidence scale: 1-10
========================================================================
Paired findings : 130
Qwen3.6 average confidence : 8.685/10
Qwen3.8 average confidence : 7.315/10
Difference (Qwen3.6 - Qwen3.8): +1.369

========================================================================
CONFIDENCE ON DISAGREEMENTS
Only findings where the two models produced different verdicts.
========================================================================
Qwen3.6 average confidence : 8.300/10
Qwen3.8 average confidence : 5.875/10
Difference (Qwen3.6 - Qwen3.8): +2.425

========================================================================
Qwen3.6 VOTE CONSISTENCY
========================================================================
Findings     : 130
Consistent   : 130
Inconsistent : 0
Consistency  : 100.0%

========================================================================
Qwen3.8 VOTE CONSISTENCY
========================================================================
Findings     : 130
Consistent   : 130
Inconsistent : 0
Consistency  : 100.0%

========================================================================
SUMMARY
========================================================================
Shared findings       : 130
Agreement              : 90 (69.2%)
Disagreement           : 40 (30.8%)
Disagreement CSV       : model_disagreements_11_140.csv

Analysis complete.
```

The disagreement cases were additionally exported to:

```text
model_disagreements_11_140.csv
```

### Comparison Notes

The direct comparison shows that the two models produced the same verdict for **90 of 130 shared findings (69.2%)** and different verdicts for **40 findings (30.8%)**.

Among the 40 disagreements, the most common direction was:

```text
Qwen3.6 FP → Qwen3.8 SMELL : 29 findings
```

followed by:

```text
Qwen3.6 SMELL → Qwen3.8 FP : 6 findings
```

The largest number of disagreements occurred in CodeQL, SonarQube, and Cppcheck findings.

The comparison also records different confidence distributions between the two runs. For the 130 shared findings, the reported average confidence values were **8.685/10 for Qwen3.6** and **7.315/10 for Qwen3.8**.

These statistics describe differences in model behavior and confidence. They do **not**, by themselves, establish which model produces more correct vulnerability classifications. Establishing correctness requires manual review or an independently verified ground-truth dataset.

> **Note:** The vote-consistency values reported by `compare_models.py` are specific to the comparison script and its paired subset. The full Qwen3.6 analysis above uses the complete result structure and reports the overall Qwen3.6 three-vote consistency as **78.7%** across 221 findings. Therefore, the comparison output's 100% consistency values should not be interpreted as the overall consistency of either model's full run.
