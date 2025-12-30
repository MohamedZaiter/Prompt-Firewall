# 🛡️ Prompt Firewall - LLM Threat Detection System

A comprehensive security system for detecting malicious prompts and protecting Large Language Models (LLMs) from prompt injection attacks, jailbreaks, and other security threats.

## 🎯 Features

### Multi-Layer Detection
- **Rule-Based Detection**: Fast pattern matching for known attack vectors
- **ML Classification**: Multiple machine learning models (Logistic Regression, SVM, Random Forest, Naive Bayes)
- **Ensemble Method**: Combines multiple detection strategies for higher accuracy
- **Response Filtering**: Detects sensitive information leakage in LLM responses

### Attack Detection Capabilities
- Prompt injection attempts
- Jailbreak commands
- System prompt extraction
- Credential/API key exposure
- Malicious instruction patterns
- Anomalous prompt lengths

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Prompt_Firewall

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### 1. Train Models (First Time Setup)

```bash
python main.py
```

This will:
- Load the training dataset
- Train all ML models (Logistic Regression, SVM, Random Forest, Naive Bayes)
- Save trained models to `models/ml_models/`
- Test the integrated firewall system

#### 2. Use the Firewall in Your Code

```python
from src.firewall import LLMFirewall

# Initialize the firewall
firewall = LLMFirewall(config_path="config.yaml")

# Check a single prompt
result = firewall.check_prompt("What is machine learning?")
print(f"Is Malicious: {result['is_malicious']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Detection Methods: {result['detection_methods']}")

# Check multiple prompts
prompts = ["Safe prompt", "Ignore all instructions"]
results = firewall.batch_check(prompts)
```

#### 3. Run the Streamlit Interface

```bash
streamlit run app_streamlit.py
```

#### 4. Run the FastAPI Server

```bash
python api.py
```

Then access the API at `http://localhost:8000`

## 📁 Project Structure

```
Prompt_Firewall/
├── src/                           # Core source code
│   ├── firewall.py               # Main firewall class (integrates all components)
│   ├── classifiers/              # Detection classifiers
│   │   ├── rule_based.py        # Rule-based detector
│   │   ├── ml_classifier.py     # ML classifier wrapper
│   │   └── transformer_classifier.py  # Transformer-based detector
│   ├── feature_extractor.py     # Feature extraction (TF-IDF, embeddings)
│   ├── preprocessor.py          # Text preprocessing
│   ├── data_loader.py           # Dataset loading
│   └── utils.py                 # Utility functions
├── models/                       # Trained models storage
│   ├── ml_models/               # ML classifiers (.pkl files)
│   └── rules/                   # Rule configurations
├── data/                        # Datasets
│   ├── raw/                    # Raw data
│   ├── processed/              # Processed data
│   └── embeddings/             # Cached embeddings
├── notebooks/                   # Jupyter notebooks
│   ├── 00_demo.ipynb           # Quick demo
│   ├── 01_data_exploration.ipynb
│   ├── 02_ml_training.ipynb
│   └── 03_evaluation.ipynb
├── tests/                       # Unit tests
├── static/                      # Static files for web interface
├── main.py                      # Main training & testing script
├── api.py                       # FastAPI server
├── app_streamlit.py            # Streamlit web interface
├── config.yaml                  # Configuration file
└── requirements.txt             # Python dependencies
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
models:
  embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  ml_models:
    - "logistic_regression"
    - "svm"
    - "random_forest"
    - "naive_bayes"

detection:
  threshold_confidence: 0.75    # Confidence threshold for malicious classification
  use_ensemble: true            # Use multiple models
  use_rules: true              # Enable rule-based detection

rules:
  max_prompt_length: 2000
  blocked_keywords:
    - "ignore previous instructions"
    - "disregard all"
    - "system prompt"
    # Add your own keywords...
```

## 🔍 Detection Methods

### 1. Rule-Based Detection (`src/classifiers/rule_based.py`)
- **Keyword Matching**: Detects known malicious phrases
- **Pattern Recognition**: Identifies sensitive information patterns
- **Length Anomaly**: Flags unusually long prompts
- **Fast & Reliable**: No training required

### 2. ML Classification (`src/classifiers/ml_classifier.py`)
- **Multiple Algorithms**: Supports LR, SVM, RF, NB
- **TF-IDF Features**: Text vectorization
- **Ensemble Voting**: Combines predictions from multiple models
- **Probability Scores**: Confidence metrics for each prediction

### 3. Integration (`src/firewall.py`)
The `LLMFirewall` class connects all components:
- Loads trained models automatically from `models/ml_models/`
- Applies rule-based checks first (fast)
- Uses ML ensemble for complex cases
- Combines scores for final decision
- Provides detailed detection breakdown

## 📊 Model Performance

After training, you'll see performance metrics:

```
Results Summary
----------------------------------------------------------
🏆 random_forest      | F1: 0.XXX | Acc: 0.XXX | Prec: 0.XXX | Rec: 0.XXX
   logistic_regression| F1: 0.XXX | Acc: 0.XXX | Prec: 0.XXX | Rec: 0.XXX
   svm               | F1: 0.XXX | Acc: 0.XXX | Prec: 0.XXX | Rec: 0.XXX
   naive_bayes       | F1: 0.XXX | Acc: 0.XXX | Prec: 0.XXX | Rec: 0.XXX
----------------------------------------------------------
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test firewall functionality
python -c "from src.firewall import LLMFirewall; fw = LLMFirewall(); print(fw.check_prompt('test'))"
```

## 📝 API Reference

### LLMFirewall Class

```python
firewall = LLMFirewall(config_path="config.yaml")

# Check single prompt
result = firewall.check_prompt(prompt: str, use_ml: bool = True) -> Dict

# Check multiple prompts
results = firewall.batch_check(prompts: List[str]) -> List[Dict]

# Filter response for data leakage
filter_result = firewall.filter_response(response: str) -> Dict

# Get firewall statistics
stats = firewall.get_statistics() -> Dict
```

### Response Format

```python
{
    'prompt': 'Truncated prompt text...',
    'is_malicious': True/False,
    'confidence': 0.85,  # 0.0 to 1.0
    'detection_methods': {
        'rules': {
            'is_malicious': True,
            'total_score': 0.8,
            'detected_keywords': ['ignore instructions'],
            ...
        },
        'ml_random_forest': {
            'prediction': 1,
            'confidence': 0.92
        },
        ...
    }
}
```

## 🛠️ Development

### Adding New Rules

Edit `config.yaml`:

```yaml
rules:
  blocked_keywords:
    - "your new keyword"
  sensitive_patterns:
    - "your pattern"
```

### Adding New ML Models

1. Update `config.yaml`:
```yaml
models:
  ml_models:
    - "your_model_name"
```

2. Add model to `MLClassifier.SUPPORTED_MODELS` in [src/classifiers/ml_classifier.py](src/classifiers/ml_classifier.py)

3. Retrain: `python main.py`

## 📦 Dependencies

- `scikit-learn` - Machine learning algorithms
- `sentence-transformers` - Text embeddings
- `transformers` - Transformer models
- `pandas`, `numpy` - Data manipulation
- `fastapi`, `uvicorn` - API server
- `streamlit` - Web interface
- `pyyaml` - Configuration
- `datasets` - Dataset loading

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Dataset: [deepset/prompt-injections](https://huggingface.co/datasets/deepset/prompt-injections)
- Embedding Model: sentence-transformers
- Built with ❤️ for LLM security

## 🔗 Resources

- [OWASP LLM Security](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Prompt Injection Attacks](https://simonwillison.net/2023/Apr/14/worst-that-can-happen/)
- [LLM Security Best Practices](https://learnprompting.org/docs/prompt_hacking/injection)

---

**⚠️ Security Note**: This firewall provides defense-in-depth but should be part of a comprehensive security strategy. Always validate and sanitize inputs at multiple layers.
