# Technical Report

## Model and runtime used

| Model | Type | Training data | Output |
|---|---|---|---|
| `health_model.pkl` | TF-IDF vectorizer + Logistic Regression (scikit-learn) | Health-domain news/claims dataset | Verdict + confidence |
| `finance_model.pkl` | TF-IDF vectorizer + Logistic Regression (scikit-learn) | Finance-domain news/claims dataset (incl. Bitcoin Scam Detection Dataset — see `ATTRIBUTION.md`) | Verdict + confidence |
| Streamlit demo model | TF-IDF vectorizer + Logistic Regression (scikit-learn) | ~44,000 labeled general news articles | REAL/FAKE + confidence |

All three are serialized with Python's `pickle` module and loaded once at process startup — no re-training or fine-tuning happens at inference time.

- **Language:** Python 3.9+
- **Backend framework:** Flask + flask-cors
- **ML library:** scikit-learn
- **Serving:** local HTTP server on `127.0.0.1:5050`, single process
- **Extension runtime:** Chrome Manifest V3 (service worker + content script)

## Quantization or optimization techniques

**Not applicable / not needed.** These are TF-IDF + Logistic Regression models, not neural networks — there are no floating-point weight matrices large enough to benefit from quantization. The entire model (vocabulary + sparse coefficient vector) is already small enough to load instantly on any consumer device, which is why no compression step was needed to meet the on-device constraint.

## Model size

> ⚠️ **Fill in from your actual files** (run the command below in the project root):

```
ls -lh server/health_model.pkl server/finance_model.pkl
```

| File | Size |
|---|---|
| `health_model.pkl` | `[FILL IN]` |
| `finance_model.pkl` | `[FILL IN]` |

## Inference latency

> ⚠️ **Fill in with real numbers from running `benchmark.py`** (see "How these numbers were measured" below — do not estimate or fabricate these):

| Metric | Value |
|---|---|
| Mean latency | `[FILL IN]` ms |
| Median latency | `[FILL IN]` ms |
| Min latency | `[FILL IN]` ms |
| Max latency | `[FILL IN]` ms |

## CPU / GPU / NPU usage

**CPU only — no GPU or NPU required at any point.**

- Both training (originally, offline) and inference (at runtime) use scikit-learn's `LogisticRegression`, which performs a sparse vector–matrix multiplication against the TF-IDF features. This is lightweight enough to run on a single CPU core in well under a millisecond of actual compute per prediction.
- No PyTorch, TensorFlow, ONNX Runtime, or any GPU-accelerated framework is used anywhere in the pipeline.
- This is a deliberate design choice for the on-device theme: it guarantees the project runs identically on any judge's laptop, regardless of whether they have a dedicated GPU or NPU available.

## Peak memory usage

> ⚠️ **Fill in with the real number from `benchmark.py`:**

| Metric | Value |
|---|---|
| Flask process memory (RSS) | `[FILL IN]` MB |

## Tested device specifications

> ⚠️ Fill in with the actual machine(s) you tested on:

| Spec | Value |
|---|---|
| OS | `[FILL IN — e.g. Windows 11 / macOS Sonoma]` |
| CPU | `[FILL IN — e.g. Intel i5-1235U / Apple M2]` |
| RAM | `[FILL IN]` |
| GPU | Not used (CPU-only inference) |
| Python version | `[FILL IN]` |

## Additional technical details

### Why no cloud inference

The entire point of the on-device theme is that a judge should be able to disconnect from the internet, run the extension or Streamlit demo, and still get a correct verdict — because the model and its weights are already sitting on disk, and inference is pure local CPU computation (matrix-vector multiplication against a sparse TF-IDF feature vector). There is no API call, no token usage, and no network dependency anywhere in the core prediction path.

### How these numbers were measured

Save the script below as `benchmark.py` in the project root and run it against your local Flask server to measure the real latency and memory numbers above.

```python
"""
benchmark.py — measures local inference latency and memory usage
for the Verifi AI Flask backend.

Usage:
    1. Start the Flask server: cd server && python app.py
    2. In another terminal: python benchmark.py
"""

import time
import statistics
import requests
import psutil

SERVER_URL = "http://127.0.0.1:5050/predict"  # adjust to your actual endpoint
SAMPLE_TEXT = "Scientists confirm drinking bleach cures COVID-19 overnight"
N_RUNS = 50


def find_flask_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = " ".join(proc.info.get("cmdline") or [])
        if "app.py" in cmdline and "server" in cmdline:
            return proc
    return None


def measure_latency():
    latencies = []
    for _ in range(N_RUNS):
        start = time.perf_counter()
        requests.post(SERVER_URL, json={"text": SAMPLE_TEXT})
        latencies.append((time.perf_counter() - start) * 1000)  # ms
    return latencies


def measure_memory():
    proc = find_flask_process()
    if proc is None:
        print("Could not find the Flask server process — is it running?")
        return None
    return proc.memory_info().rss / (1024 * 1024)  # MB


if __name__ == "__main__":
    print(f"Running {N_RUNS} requests against {SERVER_URL} ...")
    latencies = measure_latency()

    print("\n--- Latency (ms) ---")
    print(f"Mean:   {statistics.mean(latencies):.2f} ms")
    print(f"Median: {statistics.median(latencies):.2f} ms")
    print(f"Min:    {min(latencies):.2f} ms")
    print(f"Max:    {max(latencies):.2f} ms")

    mem_mb = measure_memory()
    if mem_mb is not None:
        print(f"\n--- Memory ---")
        print(f"Flask process RSS: {mem_mb:.1f} MB")
```

Install the one extra dependency needed to run it:
```
pip install psutil
```

Then copy the printed **Mean/Median/Min/Max latency** into the "Inference latency" table above, and the printed **Flask process RSS** into the "Peak memory usage" table above.
