"""
Classificateurs ML classiques pour le pare-feu LLM
"""

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
from typing import Dict, Literal
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ModelType = Literal["logistic_regression", "svm", "random_forest", "naive_bayes"]


class MLClassifier:
    """Machine learning classifier for firewall threat detection.
    
    Based on experiments from notebook 1-ml-classification.ipynb, the best performing
    models are Logistic Regression and SVM with BERT embeddings.
    """
    
    SUPPORTED_MODELS: Dict[str, type] = {
        "logistic_regression": LogisticRegression,
        "svm": SVC,
        "random_forest": RandomForestClassifier,
        "naive_bayes": GaussianNB,
    }
    
    def __init__(self, model_type: ModelType = "logistic_regression"):
        """
        Initialize the classifier.
        
        Args:
            model_type: Type of model to use.
            
        Raises:
            ValueError: If model_type is not supported.
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model type '{model_type}' not supported. "
                           f"Choose from: {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model_type = model_type
        self.model = self._create_model()
        self.is_trained = False
    
    def _create_model(self):
        """Create and configure the model instance.
        
        Parameters optimized based on notebook experiments:
        - Logistic Regression: Best overall F1 score (97.4%)
        - SVM: Second best performance with high precision
        - Random Forest: Good performance with default params
        - Naive Bayes: Simple baseline with decent results
        """
        params = {
            "logistic_regression": {
                "max_iter": 1000, 
                "random_state": 42,
                "solver": "lbfgs",  # Good for multilingual BERT embeddings
                "C": 1.0  # Regularization strength
            },
            "svm": {
                "kernel": "rbf", 
                "probability": True, 
                "random_state": 42,
                "C": 1.0,
                "gamma": "scale"  # Works well with BERT embeddings
            },
            "random_forest": {
                "n_estimators": 100, 
                "random_state": 42,
                "max_depth": None,
                "min_samples_split": 2
            },
            "naive_bayes": {},  # No parameters for GaussianNB
        }
        
        ModelClass = self.SUPPORTED_MODELS[self.model_type]
        return ModelClass(**params[self.model_type])
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the model.
        
        Args:
            X_train: Training features.
            y_train: Training labels.
            
        Raises:
            ValueError: If input data is invalid.
        """
        if X_train.shape[0] != y_train.shape[0]:
            raise ValueError("X_train and y_train must have same number of samples")
        
        logger.info(f"Training {self.model_type} model on {X_train.shape[0]} samples...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        logger.info("Training completed!")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for input data.
        
        Args:
            X: Features to predict.
            
        Returns:
            Predicted labels.
            
        Raises:
            ValueError: If model is not trained.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Features to predict.
            
        Returns:
            Probability predictions.
            
        Raises:
            ValueError: If model is not trained.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        
        scores = self.model.decision_function(X)
        return np.column_stack([1 - scores, scores])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            X_test: Test features.
            y_test: Test labels.
            
        Returns:
            Dictionary with accuracy, precision, recall, and f1 metrics.
        """
        predictions = self.predict(X_test)
        
        return {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "f1": f1_score(y_test, predictions, zero_division=0),
        }
    
    def save(self, path: str) -> None:
        """Save the trained model to disk."""
        joblib.dump(self.model, path)
        logger.info(f"Model saved: {path}")
    
    def load(self, path: str) -> None:
        """Load a trained model from disk."""
        self.model = joblib.load(path)
        self.is_trained = True
        logger.info(f"Model loaded: {path}")


if __name__ == "__main__":
    from sklearn.datasets import make_classification
    
    logger.info("Starting ML classifier demonstration...")
    
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    results = {}
    for model_type in MLClassifier.SUPPORTED_MODELS.keys():
        logger.info(f"\nTraining {model_type}...")
        clf = MLClassifier(model_type)
        clf.train(X_train, y_train)
        metrics = clf.evaluate(X_test, y_test)
        results[model_type] = metrics
        logger.info(f"Metrics: {metrics}")
    
    logger.info("\n=== Final Results ===")
    for model, metrics in results.items():
        logger.info(f"{model}: F1={metrics['f1']:.3f}, Accuracy={metrics['accuracy']:.3f}")
