"""
Comprehensive Model Training Script
Based on notebook experiments:
- Notebook 1: ML classifiers with BERT embeddings
- Notebook 3: Fine-tuned XLM-RoBERTa

This script trains all models and saves them for production use.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.classifiers.ml_classifier import MLClassifier
from src.classifiers.transformer_classifier import TransformerClassifier
from src.feature_extractor import FeatureExtractor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Comprehensive model trainer for all firewall models"""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize the trainer
        
        Args:
            data_dir: Directory containing raw data files
        """
        self.data_dir = Path(data_dir)
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.models_dir / "ml_models").mkdir(exist_ok=True)
        (self.models_dir / "transformers").mkdir(exist_ok=True)
        
        self.train_data = None
        self.test_data = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        
        logger.info("Model Trainer initialized")
    
    def load_data(self):
        """Load training and testing datasets"""
        logger.info("="*60)
        logger.info("LOADING DATA")
        logger.info("="*60)
        
        # File paths
        train_file = self.data_dir / "train-00000-of-00001-9564e8b05b4757ab.parquet"
        test_file = self.data_dir / "test-00000-of-00001-701d16158af87368.parquet"
        
        if not train_file.exists() or not test_file.exists():
            raise FileNotFoundError(
                f"Data files not found in {self.data_dir}. "
                "Please ensure the dataset is downloaded."
            )
        
        # Load data
        self.train_data = pd.read_parquet(train_file)
        self.test_data = pd.read_parquet(test_file)
        
        # Rename columns
        self.train_data.rename(columns={"text": "prompt"}, inplace=True)
        self.test_data.rename(columns={"text": "prompt"}, inplace=True)
        
        logger.info(f"✓ Loaded {len(self.train_data)} training samples")
        logger.info(f"✓ Loaded {len(self.test_data)} test samples")
        
        # Show label distribution
        train_dist = self.train_data['label'].value_counts()
        logger.info(f"Training distribution - Benign: {train_dist[0]}, Injection: {train_dist[1]}")
    
    def extract_bert_embeddings(self):
        """Extract BERT embeddings for ML classifiers (Notebook 1 approach)"""
        logger.info("="*60)
        logger.info("EXTRACTING BERT EMBEDDINGS")
        logger.info("="*60)
        
        # Initialize feature extractor with BERT
        feature_extractor = FeatureExtractor(
            use_bert_embeddings=True,
            bert_model="bert-base-multilingual-uncased"
        )
        
        logger.info("Extracting embeddings for training data...")
        train_embeddings = feature_extractor.extract_embeddings(
            self.train_data['prompt'].tolist()
        )
        
        logger.info("Extracting embeddings for test data...")
        test_embeddings = feature_extractor.extract_embeddings(
            self.test_data['prompt'].tolist()
        )
        
        # Convert to DataFrames
        self.X_train = pd.DataFrame(train_embeddings)
        self.y_train = self.train_data['label'].values
        self.X_test = pd.DataFrame(test_embeddings)
        self.y_test = self.test_data['label'].values
        
        logger.info(f"✓ Embeddings shape: {self.X_train.shape}")
        
        # Save feature extractor
        feature_extractor_path = self.models_dir / "ml_models" / "feature_extractor.pkl"
        feature_extractor.save(str(feature_extractor_path))
        logger.info(f"✓ Saved feature extractor to {feature_extractor_path}")
    
    def train_ml_models(self):
        """Train all ML classifiers (Notebook 1 approach)"""
        logger.info("="*60)
        logger.info("TRAINING ML CLASSIFIERS")
        logger.info("="*60)
        
        results = pd.DataFrame(columns=["model", "accuracy", "precision", "recall", "f1"])
        
        models = ["logistic_regression", "svm", "random_forest", "naive_bayes"]
        
        for model_type in models:
            logger.info(f"\n{'='*40}")
            logger.info(f"Training {model_type}...")
            logger.info(f"{'='*40}")
            
            # Initialize and train
            classifier = MLClassifier(model_type)
            classifier.train(self.X_train.values, self.y_train)
            
            # Evaluate
            metrics = classifier.evaluate(self.X_test.values, self.y_test)
            logger.info(f"Results:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
            
            # Save results
            results.loc[len(results)] = [model_type, metrics['accuracy'], 
                                        metrics['precision'], metrics['recall'], metrics['f1']]
            
            # Save model
            model_path = self.models_dir / "ml_models" / f"{model_type}.pkl"
            classifier.save(str(model_path))
            logger.info(f"✓ Saved model to {model_path}")
        
        # Display and save results
        logger.info("\n" + "="*60)
        logger.info("ML CLASSIFIERS - FINAL RESULTS")
        logger.info("="*60)
        logger.info("\n" + results.to_string(index=False))
        
        results.to_csv(self.models_dir / "ml_models" / "results.csv", index=False)
        
        # Plot results
        self._plot_ml_results(results)
        
        return results
    
    def _plot_ml_results(self, results: pd.DataFrame):
        """Plot ML model comparison"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(results))
        width = 0.2
        
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            ax.bar(x + i*width, results[metric], width, label=metric.capitalize(), color=color)
        
        ax.set_xlabel('Model')
        ax.set_ylabel('Score')
        ax.set_title('ML Classifiers Performance Comparison')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(results['model'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.models_dir / "ml_models" / "performance_comparison.png", dpi=300)
        logger.info(f"✓ Saved performance plot")
        plt.close()
    
    def train_transformer_model(
        self, 
        model_name: str = "xlm-roberta-large",
        num_epochs: int = 5,
        batch_size: int = 8
    ):
        """Train fine-tuned transformer model (Notebook 3 approach)"""
        logger.info("="*60)
        logger.info("TRAINING FINE-TUNED TRANSFORMER")
        logger.info("="*60)
        logger.info(f"Model: {model_name}")
        logger.info(f"Epochs: {num_epochs}, Batch size: {batch_size}")
        
        # Initialize classifier
        classifier = TransformerClassifier(
            model_name=model_name,
            use_finetuned=False  # Start from pre-trained
        )
        
        # Prepare data
        train_prompts = self.train_data['prompt'].tolist()
        train_labels = self.train_data['label'].tolist()
        test_prompts = self.test_data['prompt'].tolist()
        test_labels = self.test_data['label'].tolist()
        
        # Fine-tune
        results_df = classifier.fine_tune(
            train_prompts=train_prompts,
            train_labels=train_labels,
            test_prompts=test_prompts,
            test_labels=test_labels,
            output_dir=str(self.models_dir / "transformers" / "training_output"),
            num_epochs=num_epochs,
            batch_size=batch_size
        )
        
        # Save model
        model_path = self.models_dir / "transformers" / "xlm_roberta_finetuned"
        classifier.save(str(model_path))
        logger.info(f"✓ Saved fine-tuned model to {model_path}")
        
        # Save results
        results_df.to_csv(self.models_dir / "transformers" / "training_results.csv", index=False)
        
        # Plot training progress
        self._plot_transformer_results(results_df)
        
        return results_df
    
    def _plot_transformer_results(self, results_df: pd.DataFrame):
        """Plot transformer training progress"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        
        for ax, metric, color in zip(axes.flat, metrics, colors):
            ax.plot(results_df['epoch'], results_df[metric], marker='o', 
                   linewidth=2, markersize=8, color=color)
            ax.set_xlabel('Epoch')
            ax.set_ylabel(metric.capitalize())
            ax.set_title(f'{metric.capitalize()} over Epochs')
            ax.grid(alpha=0.3)
            ax.set_ylim(0, 1.05)
        
        plt.tight_layout()
        plt.savefig(self.models_dir / "transformers" / "training_progress.png", dpi=300)
        logger.info(f"✓ Saved training progress plot")
        plt.close()
    
    def train_all(self):
        """Train all models"""
        logger.info("\n" + "="*60)
        logger.info("STARTING COMPLETE MODEL TRAINING PIPELINE")
        logger.info("="*60 + "\n")
        
        # Load data
        self.load_data()
        
        # Extract BERT embeddings for ML models
        self.extract_bert_embeddings()
        
        # Train ML models
        ml_results = self.train_ml_models()
        
        # Train transformer model
        transformer_results = self.train_transformer_model()
        
        logger.info("\n" + "="*60)
        logger.info("ALL MODELS TRAINED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info(f"\nML Models saved in: {self.models_dir / 'ml_models'}")
        logger.info(f"Transformer model saved in: {self.models_dir / 'transformers'}")
        logger.info("\nBest performing models:")
        logger.info(f"  - ML: Logistic Regression (F1: {ml_results[ml_results['model']=='logistic_regression']['f1'].values[0]:.4f})")
        logger.info(f"  - Transformer: XLM-RoBERTa fine-tuned (F1: {transformer_results['f1'].iloc[-1]:.4f})")


def main():
    """Main training function"""
    trainer = ModelTrainer()
    trainer.train_all()


if __name__ == "__main__":
    main()
