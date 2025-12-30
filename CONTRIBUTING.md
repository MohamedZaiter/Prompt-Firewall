# Contributing to Prompt Firewall

Thank you for your interest in contributing to the Prompt Firewall project! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Maintain professional communication

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Prompt_Firewall.git
cd Prompt_Firewall
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 isort
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Guidelines

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/
```

### Type Hints

Use type hints for all function signatures:

```python
def check_prompt(self, prompt: str, use_ml: bool = True) -> Dict[str, Any]:
    """
    Check if a prompt is malicious.
    
    Args:
        prompt: Prompt text to analyze
        use_ml: Whether to use ML models
        
    Returns:
        Dictionary containing detection results
    """
    pass
```

### Documentation

- Add docstrings to all classes and functions
- Update README.md if adding new features
- Include examples in docstrings where appropriate

### Testing

Write tests for all new features:

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_firewall.py::test_check_prompt -v
```

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(classifier): add support for custom BERT models

fix(firewall): resolve race condition in batch processing

docs(readme): update installation instructions
```

## 🔍 What to Contribute

### High Priority
- [ ] Additional attack pattern detection
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Test coverage expansion
- [ ] Bug fixes

### Medium Priority
- [ ] New ML model integrations
- [ ] API endpoint enhancements
- [ ] Deployment guides
- [ ] Example applications

### Low Priority
- [ ] Code refactoring
- [ ] UI improvements
- [ ] Additional language support

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Minimal steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: Python version, OS, dependencies
6. **Code Sample**: Minimal reproducible example

Example:
```markdown
### Bug Description
Firewall crashes when processing empty strings

### Steps to Reproduce
1. Initialize firewall: `firewall = LLMFirewall()`
2. Check empty prompt: `firewall.check_prompt("")`

### Expected
Should return `{"is_malicious": False}`

### Actual
Raises `ValueError: Empty prompt`

### Environment
- Python 3.9
- Ubuntu 20.04
- Prompt_Firewall v1.0
```

## 💡 Suggesting Features

Feature requests should include:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Examples**: Code examples if applicable

## 🔄 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commits are well-formatted

### 2. Submit PR

1. Push to your fork
2. Open PR against `main` branch
3. Fill out PR template
4. Link related issues

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### 4. Review Process

- Maintainers will review within 48 hours
- Address feedback and update PR
- Once approved, PR will be merged

## 📦 Project Structure

```
Prompt_Firewall/
├── src/                 # Main source code
│   ├── classifiers/    # Detection models
│   ├── firewall.py     # Core firewall logic
│   └── utils.py        # Utility functions
├── tests/              # Test suite
├── notebooks/          # Research notebooks
├── docs/              # Documentation
└── examples/          # Usage examples
```

## 🎯 Development Workflow

1. **Issue**: Create or claim an issue
2. **Branch**: Create feature/fix branch
3. **Develop**: Write code + tests
4. **Test**: Run test suite
5. **Format**: Apply code formatters
6. **Commit**: Make well-formatted commits
7. **Push**: Push to your fork
8. **PR**: Open pull request
9. **Review**: Address feedback
10. **Merge**: Maintainer merges PR

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Questions?

- Open a discussion on GitHub
- Join our community chat
- Email maintainers

---

Thank you for contributing to Prompt Firewall! 🛡️
