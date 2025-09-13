# Ollama Dolphin Mixtral Setup

This repository helps you deploy the **Dolphin Mixtral 8×7B** model with [Ollama](https://ollama.ai) on macOS or Linux (including RunPod). The setup script checks prerequisites, installs Ollama, downloads the model, and prepares a Python environment for deeper research tasks or normal chatbot use.

## Quick Start

1. **Clone the repo**
   ```bash
   git clone <your-repo-url> && cd research
   ```
2. **Run setup**
   ```bash
   chmod +x setup_ollama.sh
   ./setup_ollama.sh
   ```
3. **Chat with the model**
   ```bash
   ollama run dolphin-mixtral:8x7b
   ```

## What the setup script does
- Detects macOS or Linux and installs missing prerequisites
- Installs Ollama if missing and ensures the service is running
- Pulls the `dolphin-mixtral:8x7b` model
- Installs Python packages for deep research (LangChain, ChromaDB, Requests, BeautifulSoup)

## Deep Research Workflow
1. Collect or download documents (web pages, PDFs, etc.).
2. Use Python libraries (e.g., LangChain) to create embeddings and store them in a vector database (ChromaDB).
3. Retrieve relevant context and feed it into the model using Ollama's API.

Example snippet:
```python
from langchain.document_loaders import WebBaseLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA

# Load documents
loader = WebBaseLoader("https://example.com")
docs = loader.load()

# Create embeddings and store
embeddings = OllamaEmbeddings(model="dolphin-mixtral:8x7b")
vectorstore = Chroma.from_documents(docs, embeddings)

# Build QA chain
qa = RetrievalQA.from_chain_type(llm=None, retriever=vectorstore.as_retriever())
print(qa.run("What is this page about?"))
```

## Normal Chatbot Mode
For casual conversation, simply run:
```bash
ollama run dolphin-mixtral:8x7b
```
Exit with `Ctrl+C`.

## Troubleshooting
- **Ollama not running**: `ollama serve` and retry the command.
- **Model missing**: Run `ollama pull dolphin-mixtral:8x7b`.
- **GPU not detected (Linux)**: Ensure your machine has an NVIDIA GPU and drivers installed.

## License
MIT

