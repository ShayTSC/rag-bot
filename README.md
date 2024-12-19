# Handbook RAG Service

A RAG (Retrieval-Augmented Generation) service that provides intelligent Q&A capabilities for company handbooks using local LLM with CUDA/MPS support.

## Features

- PDF document processing and embedding
- Local LLM support with GGUF models
- CUDA and MPS (Apple Silicon) support
- Vector similarity search using Qdrant
- Async task queue for document processing
- REST API with OpenAI-compatible endpoints
- Bearer token authentication
- Streaming response support
- Aliyun LLM fallback support

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- CUDA toolkit (for NVIDIA GPUs) or MPS (for Apple Silicon)
- Qdrant vector database
- Local GGUF model files

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd handbook-rag
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. For CUDA support, install llama-cpp-python with CUDA:
   ```bash
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" poetry run pip install llama-cpp-python
   ```
   
   Or for MPS support on macOS:
   ```bash
   CMAKE_ARGS="-DLLAMA_METAL=on" poetry run pip install llama-cpp-python
   ```

4. Set up Qdrant:
   ```bash
   docker run -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
   ```

## Configuration

Create a `.env` file in the project root:

```env
# API Settings
API_TOKEN=your-secret-token-here
HOST=0.0.0.0
PORT=8000

# Device Settings
DEVICE=cuda  # or mps, cpu
MAX_GPU_MEMORY=4GiB

# Model Settings
MODEL_DIR=./models
LOCAL_MODEL_PATH=./models/qwen2.5-7b-instruct
MODEL_PARTS_PATTERN=qwen2.5-7b-instruct-q4_0-{:05d}-of-{:05d}.gguf
MODEL_PARTS_COUNT=2

# Vector DB Settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Usage

### As a Python Package

```python
import asyncio
from handbook_rag.bootstrap import RAGService

async def main():
    service = RAGService()
    await service.initialize()
    
    # Process PDF
    await service.ensure_embeddings("path/to/handbook.pdf")
    
    # Query the handbook
    response = await service.process_query("What is the vacation policy?")
    print(response)
    
    await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### As a REST API Service

1. Start the server:
   ```bash
   poetry run python -m handbook_rag.api
   ```

2. Upload a PDF:
   ```bash
   curl -X POST "http://localhost:8000/v1/embed" \
     -H "Authorization: Bearer your-secret-token-here" \
     -F "file=@handbook.pdf"
   ```

3. Query the handbook:
   ```bash
   curl -X POST "http://localhost:8000/query" \
     -H "Authorization: Bearer your-secret-token-here" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the vacation policy?"}'
   ```

4. Use OpenAI-compatible endpoint:
   ```bash
   curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer your-secret-token-here" \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {"role": "user", "content": "What is the vacation policy?"}
       ],
       "stream": true
     }'
   ```

## Project Structure

```
handbook-rag/
├── handbook_rag/
│   ├── api/              # REST API implementation
│   ├── embeddings/       # PDF processing and embedding
│   ├── llm/             # LLM implementations
│   └── queue/           # Async task queue
├── tests/               # Test files
├── pyproject.toml       # Project dependencies
└── README.md           # This file
```

## Development

1. Format code:
   ```bash
   poetry run black .
   poetry run isort .
   ```

2. Run tests:
   ```bash
   poetry run pytest
   ```

## Model Support

The service is designed to work with GGUF format models. By default, it's configured to use Qwen 2.5 7B Instruct, but you can use any GGUF model by updating the configuration.

The model URL is: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF

We are using the `qwen2.5-7b-instruct-q4_0*.gguf` quantized model.

### Handling Split Models

The service supports split GGUF models. Configure the following in your `.env`:
- `MODEL_PARTS_PATTERN`: Pattern for split files (e.g., "model-q4_0-{:05d}-of-{:05d}.gguf")
- `MODEL_PARTS_COUNT`: Total number of parts

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (```git checkout -b feature/amazing-feature```)
3. Commit your changes (```git commit -m 'Add some amazing feature'```)
4. Push to the branch (```git push origin feature/amazing-feature```)
5. Open a Pull Request