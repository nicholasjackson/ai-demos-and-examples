# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains AI pattern demonstrations and configurations using Jumppad for infrastructure orchestration. Each pattern demonstrates different AI application setups and integrations.

## Architecture

The repository is organized by pattern, with each pattern contained in its own directory:

- `jumppad/` - Hugging Face Chat-UI with MongoDB and OpenAI integration
  - Uses Jumppad HCL configuration to orchestrate containers
  - Sets up a containerized chat interface with persistent MongoDB storage
  - Configured for OpenAI GPT-4 and GPT-3.5 Turbo models

### Jumppad Pattern Structure

Jumppad configurations follow this general structure:
- **Network resources**: Define container networking with custom subnets
- **Container resources**: Define services with dependencies, health checks, and environment configuration
- **Volume mounts**: Persistent data storage (e.g., `./data/mongodb`)
- **Outputs**: Provide connection strings and setup instructions

## Common Commands

### Jumppad Environment Management

```bash
# Start a pattern (from the pattern directory)
cd jumppad
jumppad up

# Stop and clean up
jumppad down

# View running resources
jumppad status
```

### Required Environment Variables

For the Chat-UI pattern:
```bash
export OPENAI_API_KEY=your_api_key_here
export HF_TOKEN=your_hf_token_here  # Optional, for additional Hugging Face features
```

## Development Workflow

When creating new patterns:
1. Create a new directory for the pattern
2. Define infrastructure in `main.hcl` using Jumppad resource blocks
3. Include usage instructions in comments at the top of the HCL file
4. Use `output` blocks to provide connection details and setup instructions
5. Use health checks for services with dependencies to ensure proper startup order

## Jumppad Configuration Details

- Configuration language: HCL (HashiCorp Configuration Language)
- Resource types used: `network`, `container`, `output`
- Container images are pulled from Docker Hub or GitHub Container Registry
- Environment variables can reference host environment using `${env("VAR_NAME")}`
- JSON configuration can be embedded using `jsonencode()` function

## Documentation
For documentation on Jumppad or any of the packages and tools inside this respository,
please try the context7 MCP server or visit the respective official documentation sites.