# DGX Spark Setup Guide

This guide covers SSH access, tool installation, and environment configuration for the DGX Spark server.

## SSH Access

Connect to the DGX Spark server:

```bash
ssh jondyer3@spark-b0f2.local
```

## System Specifications

- **GPU**: GB10 GPU
- **CUDA Version**: 13.0
- **RAM**: 125GB

Verify GPU availability:

```bash
nvidia-smi
```

## Tool Installation

The DGX Spark environment has the following tools pre-installed:

### Python Environment Manager (uv)

`uv` is installed for Python dependency management and virtual environments.

```bash
# Verify installation
uv --version
```

### Node.js

Node.js v22.22.0 is installed via nvm.

```bash
# Verify installation
node --version  # Should show v22.22.0
npm --version
```

### Helm

Helm v3.20 is installed for Kubernetes package management.

```bash
# Verify installation
helm version  # Should show v3.20
```

### GitHub CLI

The GitHub CLI is installed and authenticated as `dyerinnovation`.

```bash
# Verify installation
gh --version

# Check authentication status
gh auth status
```

HTTPS push has been configured via `gh auth setup-git`.

## PATH Configuration

The following PATH is configured in the shell environment:

```bash
export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v22.22.0/bin:$PATH"
```

This ensures:
- Local Python tools (uv) are available at `$HOME/.local/bin`
- Node.js binaries are available from the nvm installation
- System binaries remain accessible

## Git Configuration

Git is configured with the following credentials:

```bash
git config --global user.name "Jonathan Dyer"
git config --global user.email "jon@dyerinnovation.com"
```

## Project Location

The Agent Skill Adapter project is located at:

```bash
~/agent-skill-adapter
```

Navigate to the project:

```bash
cd ~/agent-skill-adapter
```

## Next Steps

- [Model Download Guide](./02_model_download.md) — Download and cache the Qwen3-8B model
- [Model Serving Guide](./03_model_serving.md) — Deploy TGI for model inference
