# Training Architecture

## Overview
Fine-tune a base LLM (default: Qwen3-7B) using LoRA adapters on DGX Spark (NVIDIA GB10, 119GB unified memory).

## Components

### LoRA Configuration
- Rank: 16 (configurable)
- Alpha: 32
- Target modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- Dropout: 0.05

### Quantization
- 4-bit QLoRA via bitsandbytes (NF4)
- Compute dtype: bfloat16
- Double quantization enabled

### Training Loop
1. Load base model with QLoRA
2. Apply LoRA adapters
3. For each skill:
   a. Load synthetic dataset
   b. Compute rewards via rubric evaluator
   c. Run GRPO optimization step
4. Merge and save adapter

### Memory Budget (GB10 119GB)
- Base model (4-bit): ~4GB for 7B params
- LoRA adapters: ~50MB
- Activations + gradients: ~8GB with gradient checkpointing
- Total: ~12-15GB, well within 119GB budget

## Framework Stack
- `transformers` — Model loading, tokenization
- `peft` — LoRA/QLoRA adapter management
- `trl` — GRPO/DPO trainers
- `bitsandbytes` — 4-bit quantization
- `accelerate` — Device placement
