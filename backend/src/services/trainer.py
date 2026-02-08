"""LoRA training service using TRL and bitsandbytes."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, PeftModel
from trl import GRPOConfig, GRPOTrainer
import torch

from src.models.config import settings


class SkillTrainer:
    """Trainer for skill adapters using LoRA and GRPO."""
    
    def __init__(
        self,
        model_name: str = settings.model,
        lora_rank: int = settings.lora_rank,
        lora_alpha: int = settings.lora_alpha,
        quant_bits: int = settings.quant_bits,
    ):
        self.model_name = model_name
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.quant_bits = quant_bits
        self.model = None
        self.tokenizer = None
    
    def setup_model(self) -> None:
        """Initialize model with QLoRA configuration."""
        # Configure quantization
        if self.quant_bits == 4:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        else:
            bnb_config = None
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
    
    def train(
        self,
        train_data: list[dict[str, Any]],
        output_dir: str,
        num_epochs: int = 1,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
    ) -> dict[str, Any]:
        """
        Train the model using GRPO.
        
        Args:
            train_data: List of {"prompt": str, "response": str} dicts
            output_dir: Directory to save adapter
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
        
        Returns:
            Training metrics
        """
        if self.model is None or self.tokenizer is None:
            self.setup_model()
        
        # Prepare dataset
        def tokenize_fn(examples):
            prompts = [ex["prompt"] for ex in examples]
            responses = [ex["response"] for ex in examples]
            full_texts = [p + " " + r for p, r in zip(prompts, responses)]
            
            tokenized = self.tokenizer(
                full_texts,
                truncation=True,
                max_length=settings.max_seq_len,
                padding="max_length",
                return_tensors="pt",
            )
            return tokenized
        
        # Configure GRPO training
        grpo_config = GRPOConfig(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            gradient_checkpointing=settings.gradient_checkpointing,
            save_strategy="epoch",
            logging_steps=10,
            remove_unused_columns=False,
        )
        
        # Note: GRPO requires a reward model, which is a simplified placeholder here
        # In production, you would implement a proper reward function based on rubrics
        def reward_fn(prompts, responses):
            """Simple reward based on response length (placeholder)."""
            return [len(r.split()) / 100.0 for r in responses]
        
        # Create trainer
        trainer = GRPOTrainer(
            model=self.model,
            config=grpo_config,
            tokenizer=self.tokenizer,
            reward_fn=reward_fn,
        )
        
        # Train
        result = trainer.train()
        
        # Save adapter
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        return {
            "loss": result.training_loss if hasattr(result, "training_loss") else 0.0,
            "epochs": num_epochs,
            "adapter_path": output_dir,
        }
    
    def load_adapter(self, adapter_path: str) -> None:
        """Load a trained adapter."""
        if self.model is None:
            # Load base model first
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                trust_remote_code=True,
            )
        
        # Load adapter
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(
                adapter_path,
                trust_remote_code=True,
            )
    
    def generate(self, prompt: str, max_length: int = 512) -> str:
        """Generate text using the model."""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not initialized. Call setup_model() or load_adapter() first.")
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the prompt from output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
