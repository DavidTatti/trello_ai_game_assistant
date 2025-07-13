# AI Configuration Guide

This project supports two AI providers for generating Trello card comments and metadata:

## 1. Ollama (Local AI) - Default

Ollama runs locally on your machine, providing privacy and no API costs.

### Setup:
1. Install Ollama from https://ollama.ai/
2. Pull a model: `ollama pull llama3`
3. Set environment variables:
   ```bash
   AI_PROVIDER=ollama
   OLLAMA_MODEL=llama3
   ```

## 2. OpenAI (ChatGPT API) - Cloud AI

Uses OpenAI's ChatGPT API for potentially better responses.

### Setup:
1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Set environment variables:
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

## Environment Variables

Add these to your `.env` file:

```bash
# AI Provider Configuration
AI_PROVIDER=ollama  # or "openai"
OLLAMA_MODEL=llama3
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Your existing Trello and Slack configuration...
```

## Switching Between Providers

To switch from Ollama to OpenAI:
1. Set `AI_PROVIDER=openai` in your `.env` file
2. Add your `OPENAI_API_KEY`
3. Restart your application

To switch back to Ollama:
1. Set `AI_PROVIDER=ollama` in your `.env` file
2. Ensure Ollama is running locally
3. Restart your application

## Troubleshooting

### Ollama Issues:
- Ensure Ollama is running: `ollama serve`
- Check available models: `ollama list`
- Pull a model if needed: `ollama pull llama3`

### OpenAI Issues:
- Verify your API key is correct
- Check your OpenAI account has credits
- Ensure the model name is valid (e.g., `gpt-3.5-turbo`, `gpt-4`) 