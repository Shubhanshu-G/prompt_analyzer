# 🎯 AI Prompt & Decision Evaluator

A local, privacy-focused tool for analyzing and scoring AI prompts and decision points. Powered by Ollama and Streamlit.

## ✨ Features

- 📝 **Line-by-Line Analysis**: Deep dive into every sentence for clarity and actionability.
- ⚖️ **Decision Analysis**: Evaluate AI reasoning and logic soundness.
- 🚨 **Hallucination Detection**: Assess risk scores for potential AI factual errors.
- 🔢 **Token Tracking**: Monitor your local LLM usage in real-time.
- 📄 **Document Support**: Evaluate text directly or upload `.txt`, `.docx`, or `.pdf` files.
- 🔒 **100% Local**: No cloud APIs, no data leakage. Everything runs on your machine.

## 🚀 Quick Start

### 1. Prerequisites
- **Ollama**: [Download and install Ollama](https://ollama.ai/)
- **Python**: 3.9+ recommended

### 2. Setup
```bash
# Clone the repository
cd multi-agent-ai

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Ollama
Ensure Ollama is running and you have a model pulled:
```bash
ollama pull llama3.1:8b  # recommended
```

### 4. Run the App
```bash
streamlit run evaluate.py
```

## 🐳 Running with Docker

If you prefer using Docker:

```bash
docker-compose up -d
```
The application will be available at `http://localhost:8501`.

## 📂 Project Structure

- `evaluate.py`: Main application entry point.
- `config.py`: Configuration for models and evaluators.
- `utils/`: Core logic for analysis and LLM interaction.
- `extra/`: Archive of legacy scripts and documentation.
- `uploads/`: Temporary storage for evaluated files.

## 🛠️ Configuration
You can customize evaluation criteria and default models in `config.py`.
"# prompt_analyzer" 
