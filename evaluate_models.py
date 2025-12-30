"""
Model Evaluation Script
Compare all trained models as demonstrated in the notebooks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import json
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.classifiers.ml_classifier import MLClassifier
from src.classifiers.transformer_classifier import TransformerClassifier
from src.feature_extractor import FeatureExtractor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation and comparison"""
    
    def __init__(self, data_dir: str = "data/raw", models_dir: str = "models"):
        """
        Initialize evaluator
        
        Args:
            data_dir: Directory containing test data
            models_dir: Directory containing trained models
        """
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.results_dir = Path("evaluation_results")
        self.results_dir.mkdir(exist_ok=True)
        
        self.test_data = None
        self.X_test = None
        self.y_test = None
        
        logger.info("Model Evaluator initialized")
    
    def load_test_data(self):
        """Load test dataset"""
        logger.info("Loading test data...")
        
        test_file = self.data_dir / "test-00000-of-00001-701d16158af87368.parquet"
        
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        self.test_data = pd.read_parquet(test_file)
        self.test_data.rename(columns={"text": "prompt"}, inplace=True)
        
        logger.info(f"✓ Loaded {len(self.test_data)} test samples")
        
        # Show distribution
        dist = self.test_data['label'].value_counts()
        logger.info(f"Test distribution - Benign: {dist[0]}, Injection: {dist[1]}")
    
    def prepare_embeddings(self):
        """Prepare BERT embeddings for ML models"""
        logger.info("Preparing BERT embeddings...")
        
        # Load feature extractor
        feature_extractor_path = self.models_dir / "ml_models" / "feature_extractor.pkl"
        
        if not feature_extractor_path.exists():
            logger.warning("Feature extractor not found, creating new one...")
            feature_extractor = FeatureExtractor(
                use_bert_embeddings=True,
                bert_model="bert-base-multilingual-uncased"
            )
        else:
            feature_extractor = FeatureExtractor.load(
                str(feature_extractor_path),
                embedding_model="bert-base-multilingual-uncased"
            )
            feature_extractor.use_bert_embeddings = True
            feature_extractor.bert_tokenizer = None
            feature_extractor.bert_model = None
            # Reinitialize BERT
            from transformers import BertTokenizer, BertModel
            feature_extractor.bert_tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-uncased")
            feature_extractor.bert_model = BertModel.from_pretrained("bert-base-multilingual-uncased")
            feature_extractor.bert_model.eval()
        
        test_embeddings = feature_extractor.extract_embeddings(
            self.test_data['prompt'].tolist()
        )
        
        self.X_test = pd.DataFrame(test_embeddings)
        self.y_test = self.test_data['label'].values
        
        logger.info(f"✓ Embeddings prepared: {self.X_test.shape}")
    
    def evaluate_ml_models(self) -> pd.DataFrame:
        """Evaluate all ML models"""
        logger.info("="*60)
        logger.info("EVALUATING ML MODELS")
        logger.info("="*60)
        
        results = []
        models = ["logistic_regression", "svm", "random_forest", "naive_bayes"]
        
        for model_type in models:
            model_path = self.models_dir / "ml_models" / f"{model_type}.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model not found: {model_path}")
                continue
            
            logger.info(f"\nEvaluating {model_type}...")
            
            # Load model
            classifier = MLClassifier(model_type)
            classifier.load(str(model_path))
            
            # Predict
            y_pred = classifier.predict(self.X_test.values)
            y_proba = classifier.predict_proba(self.X_test.values)[:, 1]
            
            # Calculate metrics
            metrics = {
                'model': model_type,
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred, zero_division=0),
                'recall': recall_score(self.y_test, y_pred, zero_division=0),
                'f1': f1_score(self.y_test, y_pred, zero_division=0),
                'predictions': y_pred,
                'probabilities': y_proba
            }
            
            logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall:    {metrics['recall']:.4f}")
            logger.info(f"  F1 Score:  {metrics['f1']:.4f}")
            
            results.append(metrics)
            
            # Save confusion matrix
            cm = confusion_matrix(self.y_test, y_pred)
            self._plot_confusion_matrix(cm, model_type)
        
        # Create results DataFrame
        results_df = pd.DataFrame([{
            'model': r['model'],
            'accuracy': r['accuracy'],
            'precision': r['precision'],
            'recall': r['recall'],
            'f1': r['f1']
        } for r in results])
        
        logger.info("\n" + "="*60)
        logger.info("ML MODELS - SUMMARY")
        logger.info("="*60)
        logger.info("\n" + results_df.to_string(index=False))
        
        results_df.to_csv(self.results_dir / "ml_models_evaluation.csv", index=False)
        
        return results_df, results
    
    def evaluate_transformer_model(self) -> Dict:
        """Evaluate fine-tuned transformer model"""
        logger.info("="*60)
        logger.info("EVALUATING TRANSFORMER MODEL")
        logger.info("="*60)
        
        model_path = self.models_dir / "transformers" / "xlm_roberta_finetuned"
        
        if not model_path.exists():
            logger.error(f"Transformer model not found: {model_path}")
            return None
        
        # Load model
        classifier = TransformerClassifier(use_finetuned=False)
        classifier.load(str(model_path))
        
        # Prepare data
        test_prompts = self.test_data['prompt'].tolist()
        test_labels = self.test_data['label'].tolist()
        
        # Evaluate
        logger.info("Evaluating on test set...")
        metrics = classifier.evaluate(test_prompts, test_labels)
        
        logger.info(f"\nResults:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1 Score:  {metrics['f1']:.4f}")
        
        # Get predictions for confusion matrix
        predictions = []
        logger.info("Generating predictions...")
        for i, prompt in enumerate(test_prompts):
            if (i+1) % 100 == 0:
                logger.info(f"  Processed {i+1}/{len(test_prompts)} samples")
            pred, _ = classifier.predict(prompt)
            predictions.append(pred)
        
        # Confusion matrix
        cm = confusion_matrix(test_labels, predictions)
        self._plot_confusion_matrix(cm, "transformer_xlm_roberta")
        
        # Save results
        result = {
            'model': 'XLM-RoBERTa (fine-tuned)',
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1'],
            'predictions': predictions
        }
        
        pd.DataFrame([result]).drop('predictions', axis=1).to_csv(
            self.results_dir / "transformer_evaluation.csv", index=False
        )
        
        return result
    
    def _plot_confusion_matrix(self, cm: np.ndarray, model_name: str):
        """Plot confusion matrix"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Benign', 'Injection'],
                   yticklabels=['Benign', 'Injection'])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(self.results_dir / f"confusion_matrix_{model_name}.png", dpi=300)
        plt.close()
    
    def compare_all_models(self, ml_results_df: pd.DataFrame, transformer_result: Dict):
        """Create comprehensive comparison"""
        logger.info("="*60)
        logger.info("COMPREHENSIVE MODEL COMPARISON")
        logger.info("="*60)
        
        # Combine results
        all_results = ml_results_df.copy()
        if transformer_result:
            transformer_df = pd.DataFrame([{
                'model': transformer_result['model'],
                'accuracy': transformer_result['accuracy'],
                'precision': transformer_result['precision'],
                'recall': transformer_result['recall'],
                'f1': transformer_result['f1']
            }])
            all_results = pd.concat([all_results, transformer_df], ignore_index=True)
        
        logger.info("\n" + all_results.to_string(index=False))
        
        # Find best model
        best_model = all_results.loc[all_results['f1'].idxmax()]
        logger.info(f"\n🏆 Best Model: {best_model['model']}")
        logger.info(f"   F1 Score: {best_model['f1']:.4f}")
        
        # Save comprehensive results
        all_results.to_csv(self.results_dir / "all_models_comparison.csv", index=False)
        
        # Plot comparison
        self._plot_comparison(all_results)
        
        return all_results
    
    def _plot_comparison(self, results: pd.DataFrame):
        """Plot comprehensive comparison"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Bar plot
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        x = np.arange(len(results))
        width = 0.2
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            axes[0].bar(x + i*width, results[metric], width, label=metric.capitalize(), color=color)
        
        axes[0].set_xlabel('Model')
        axes[0].set_ylabel('Score')
        axes[0].set_title('All Models Performance Comparison')
        axes[0].set_xticks(x + width * 1.5)
        axes[0].set_xticklabels(results['model'], rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)
        axes[0].set_ylim(0, 1.05)
        
        # F1 score ranking
        sorted_results = results.sort_values('f1', ascending=True)
        axes[1].barh(sorted_results['model'], sorted_results['f1'], color='#9b59b6')
        axes[1].set_xlabel('F1 Score')
        axes[1].set_title('F1 Score Ranking')
        axes[1].grid(axis='x', alpha=0.3)
        axes[1].set_xlim(0, 1.05)
        
        # Add value labels
        for i, (idx, row) in enumerate(sorted_results.iterrows()):
            axes[1].text(row['f1'] + 0.01, i, f"{row['f1']:.4f}", va='center')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "comprehensive_comparison.png", dpi=300)
        logger.info(f"✓ Saved comprehensive comparison plot")
        plt.close()
    
    def generate_report(self):
        """Generate markdown report"""
        logger.info("Generating evaluation report...")
        
        report_path = self.results_dir / "EVALUATION_REPORT.md"
        
        # Read results
        ml_results = pd.read_csv(self.results_dir / "ml_models_evaluation.csv")
        transformer_results = pd.read_csv(self.results_dir / "transformer_evaluation.csv")
        all_results = pd.read_csv(self.results_dir / "all_models_comparison.csv")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Prompt Firewall - Model Evaluation Report\\n\\n")
            f.write("## Overview\\n\\n")
            f.write("This report summarizes the performance of all trained models ")
            f.write("based on the experimental approaches from the notebooks.\\n\\n")
            
            f.write("## Test Dataset\\n\\n")
            f.write(f"- Total samples: {len(self.test_data)}\\n")
            dist = self.test_data['label'].value_counts()
            f.write(f"- Benign prompts: {dist[0]}\\n")
            f.write(f"- Injection prompts: {dist[1]}\\n\\n")
            
            f.write("## ML Classifiers (with BERT embeddings)\\n\\n")
            f.write(ml_results.to_markdown(index=False))
            f.write("\\n\\n")
            
            f.write("## Transformer Model (Fine-tuned)\\n\\n")
            f.write(transformer_results.to_markdown(index=False))
            f.write("\\n\\n")
            
            f.write("## Overall Comparison\\n\\n")
            f.write(all_results.to_markdown(index=False))
            f.write("\\n\\n")
            
            best_model = all_results.loc[all_results['f1'].idxmax()]
            f.write("## Best Model\\n\\n")
            f.write(f"**{best_model['model']}** achieved the best F1 score of **{best_model['f1']:.4f}**\\n\\n")
            
            f.write("## Key Findings\\n\\n")
            f.write("Based on notebook experiments:\\n\\n")
            f.write("1. **ML Classifiers with BERT embeddings**: ")
            f.write("Logistic Regression and SVM show excellent performance (>97% F1)\\n")
            f.write("2. **Fine-tuned XLM-RoBERTa**: Best overall performance (97.4% F1)\\n")
            f.write("3. **Pre-trained models without fine-tuning**: Significantly lower performance\\n")
            f.write("4. **Recommendation**: Use fine-tuned transformer or Logistic Regression with BERT embeddings\\n\\n")
            
            f.write("## Visualization\\n\\n")
            f.write("![Comprehensive Comparison](comprehensive_comparison.png)\\n\\n")
        
        logger.info(f"✓ Report saved: {report_path}")
    
    def run_full_evaluation(self):
        """Run complete evaluation pipeline"""
        logger.info("\\n" + "="*60)
        logger.info("STARTING FULL EVALUATION PIPELINE")
        logger.info("="*60 + "\\n")
        
        # Load data
        self.load_test_data()
        
        # Prepare embeddings for ML models
        self.prepare_embeddings()
        
        # Evaluate ML models
        ml_results_df, ml_results = self.evaluate_ml_models()
        
        # Evaluate transformer
        transformer_result = self.evaluate_transformer_model()
        
        # Compare all
        all_results = self.compare_all_models(ml_results_df, transformer_result)
        
        # Generate report
        self.generate_report()
        
        logger.info("\\n" + "="*60)
        logger.info("EVALUATION COMPLETE!")
        logger.info("="*60)
        logger.info(f"\\nResults saved in: {self.results_dir}")


def main():
    """Main evaluation function"""
    evaluator = ModelEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
