# Smart Onboarding & Compliance AI Copilot

> An AI-powered SaaS solution for staffing agencies to automate onboarding and compliance document verification, reducing manual effort, speeding processing, and improving regulatory adherence.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
streamlit run main.py
```

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** ([Download here](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([Download here](https://git-scm.com/downloads))

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### Step 2: Create Virtual Environment (Recommended)

This keeps your project dependencies isolated from other Python projects.

**For macOS/Linux:**
```bash
python -m venv env
source env/bin/activate
```

**For Windows:**
```bash
python -m venv env
env\Scripts\activate
```

> 💡 **Tip**: You should see `(env)` in your terminal prompt when the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables Setup

1. Create a `.env` file in the project root:
   ```bash
   touch .env  # macOS/Linux
   # OR create manually using your text editor
   ```

2. Add your API keys to the `.env` file:
   ```ini
   OPENAI_API_KEY=your-openai-key-here
   GROQ_API_KEY=your-groq-key-here
   ```

3. **Important**: Ensure `.env` is in your `.gitignore` file to prevent accidentally committing secrets:
   ```gitignore
   # Environment variables
   .env
   ```

### Required API Keys

| Service | Purpose | How to Get |
|---------|---------|------------|
| OpenAI | AI document processing | [Get API Key](https://platform.openai.com/api-keys) |
| Groq | Alternative AI processing | [Get API Key](https://console.groq.com/) |

---

## 🚀 Running the Application

Start the Streamlit application:

```bash
streamlit run main.py
```

The app will automatically open in your browser at:
```
http://localhost:8501
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **"Python not found"** | Ensure Python 3.9+ is installed and added to PATH |
| **"Module not found"** | Run `pip install -r requirements.txt` again |
| **"API key error"** | Check your `.env` file has correct API keys |
| **"Port already in use"** | Try `streamlit run main.py --server.port 8502` |

### Getting Help

If you're still experiencing issues:

1. Check the [Issues](https://github.com/your-username/your-repo-name/issues) page
2. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error message (if any)
   - Steps you've already tried

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by OpenAI and Groq APIs
- Icons from [Emoji Guide](https://emojipedia.org/)

---

<div align="center">

**[⬆ Back to Top](#smart-onboarding--compliance-ai-copilot)**


</div>