from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model: str = "Qwen/Qwen3-7B"
    adapter: str = "lora"
    lora_rank: int = 16
    lora_alpha: int = 32
    quant_bits: int = 4
    batch_size: int = 4
    max_seq_len: int = 4096
    gradient_checkpointing: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    redis_url: str = "redis://localhost:6379"
    judge_model: str = ""
    skills_dir: str = "./skills"

    model_config = {"env_prefix": "SKILL_ADAPTER_"}


settings = Settings()
