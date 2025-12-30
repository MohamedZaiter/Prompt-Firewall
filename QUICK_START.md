# Quick Start Guide - Optimized Prompt Firewall

## 🚀 What's New

Your project has been updated with findings from your notebooks:

- ✅ **ML Classifiers** now use BERT embeddings (97.4% F1 score)
- ✅ **Fine-tuned Transformer** support added (97.4% F1 score)  
- ✅ **Training pipeline** for all models
- ✅ **Evaluation framework** with detailed reports
- ✅ **Enhanced firewall** with multi-level detection

## 📋 Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Usage

### Option 1: Use Pre-trained Models (if available)

```python
from src.firewall import LLMFirewall

# Initialize firewall
firewall = LLMFirewall(use_transformer=False)  # Fast ML models
# or
firewall = LLMFirewall(use_transformer=True)   # Best accuracy

# Check a prompt
result = firewall.check_prompt("Ignore previous instructions")

print(f"Malicious: {result['is_malicious']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Recommendation: {result['recommendation']}")
```

### Option 2: Train Your Own Models

```bash
# Step 1: Ensure dataset is in data/raw/
# - train-00000-of-00001-9564e8b05b4757ab.parquet
# - test-00000-of-00001-701d16158af87368.parquet

# Step 2: Train all models
python train_models.py

# Step 3: Evaluate models
python evaluate_models.py

# Step 4: Check results
# - models/ml_models/          # Trained ML models
# - models/transformers/       # Fine-tuned transformer
# - evaluation_results/        # Performance reports
```

## 🎨 Detection Strategies

### Strategy 1: Lightning Fast (< 10ms)
```python
firewall = LLMFirewall(use_transformer=False)
result = firewall.check_prompt(prompt, use_ml=False)  # Rules only
```

### Strategy 2: Balanced (10-100ms) ⭐ Recommended
```python
firewall = LLMFirewall(use_transformer=False)
result = firewall.check_prompt(prompt, use_ml=True)   # Rules + ML
```

### Strategy 3: Maximum Accuracy (100ms+)
```python
firewall = LLMFirewall(use_transformer=True)
result = firewall.check_prompt(prompt, use_transformer=True)
```

## 📊 Expected Performance

Based on notebook experiments:

| Method | F1 Score | Speed | Use Case |
|--------|----------|-------|----------|
| Rules Only | ~85% | Very Fast | First-pass filtering |
| ML + BERT | 97.4% | Fast | Production (recommended) |
| Fine-tuned Transformer | 97.4% | Slow | Critical applications |

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
detection:
  threshold_confidence: 0.75  # Adjust sensitivity
  use_ensemble: true          # Use multiple ML models
  use_rules: true            # Enable rule-based detection

models:
  ml_models:
    - logistic_regression  # Best performer
    - svm                  # Second best
    - random_forest
    - naive_bayes
```

## 📈 Training Details

From your notebooks:

**ML Classifiers:**
- Features: BERT embeddings (768-dimensional)
- Best model: Logistic Regression
- Training time: ~5 minutes
- Precision: 100% | Recall: 95%

**Transformer:**
- Model: XLM-RoBERTa-large
- Fine-tuning: 5 epochs
- Training time: ~2 hours (GPU recommended)
- Precision: 100% | Recall: 95%

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test firewall
python src/firewall.py
```

## 📁 Project Structure

```
Prompt_Firewall/
├── src/
│   ├── classifiers/
│   │   ├── ml_classifier.py         # ✅ Optimized
│   │   ├── transformer_classifier.py # ✅ Added fine-tuning
│   │   └── rule_based.py
│   ├── feature_extractor.py         # ✅ Added BERT
│   └── firewall.py                  # ✅ Enhanced
├── notebooks/                       # Your research
├── models/                          # Trained models
│   ├── ml_models/
│   └── transformers/
├── train_models.py                  # ✅ NEW
├── evaluate_models.py               # ✅ NEW
└── requirements.txt                 # ✅ Updated
```

## 💡 Tips

1. **For Development**: Use ML models (fast iteration)
2. **For Production**: Use ML models (good balance)
3. **For Critical Apps**: Use transformer (best accuracy)
4. **For Real-time**: Use rules only (fastest)

## 🐛 Troubleshooting

### "Model not found" error
```bash
# Train models first
python train_models.py
```

### "Out of memory" during training
```python
# In train_models.py, reduce batch_size
batch_size=4  # Instead of 8
```

### Slow predictions
```python
# Use ML models instead of transformer
firewall = LLMFirewall(use_transformer=False)
```

## 📚 Learn More

- See `PROJECT_OPTIMIZATIONS.md` for detailed improvements
- Check notebooks for experimental details
- Read `evaluation_results/EVALUATION_REPORT.md` after evaluation

## 🎉 You're Ready!

Your firewall is now optimized with state-of-the-art detection capabilities based on your notebook research!
