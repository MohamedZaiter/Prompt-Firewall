"""
Utilitaires pour le pare-feu LLM
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class Logger:
    """Classe pour enregistrer les événements du pare-feu"""
    
    def __init__(self, log_path: str = "logs/firewall.log"):
        """Initialiser le logger"""
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """
        Enregistrer un événement
        
        Args:
            event_type: Type d'événement
            details: Détails de l'événement
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_detection(self, prompt: str, is_malicious: bool, confidence: float):
        """Enregistrer une détection"""
        self.log_event('detection', {
            'prompt': prompt[:100],
            'is_malicious': is_malicious,
            'confidence': confidence
        })
    
    def log_filter(self, response: str, has_leakage: bool, info_types: list):
        """Enregistrer un filtrage"""
        self.log_event('filter', {
            'response': response[:100],
            'has_leakage': has_leakage,
            'info_types': info_types
        })


class MetricsCollector:
    """Classe pour collecter les métriques"""
    
    def __init__(self):
        """Initialiser le collecteur"""
        self.metrics = {
            'total_prompts_checked': 0,
            'malicious_detected': 0,
            'false_positives': 0,
            'responses_filtered': 0,
            'leakages_detected': 0
        }
    
    def increment_counter(self, counter: str):
        """Incrémenter un compteur"""
        if counter in self.metrics:
            self.metrics[counter] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques"""
        total = self.metrics['total_prompts_checked']
        detection_rate = (self.metrics['malicious_detected'] / total * 100) if total > 0 else 0
        
        return {
            **self.metrics,
            'detection_rate': f"{detection_rate:.2f}%"
        }
    
    def reset(self):
        """Réinitialiser les métriques"""
        for key in self.metrics:
            self.metrics[key] = 0


def format_detection_report(result: Dict) -> str:
    """
    Formater un rapport de détection
    
    Args:
        result: Résultat de la détection
        
    Returns:
        Rapport formaté
    """
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    DETECTION REPORT                          ║
╠══════════════════════════════════════════════════════════════╣
║ Prompt: {result['prompt']:<50} ║
║ Malicious: {str(result['is_malicious']):<46} ║
║ Confidence: {result['confidence']:.4f}{' ' * 39} ║
╠══════════════════════════════════════════════════════════════╣
║                  DETECTION METHODS                           ║
"""
    
    for method, details in result['detection_methods'].items():
        report += f"║ {method:<58} ║\n"
        if isinstance(details, dict):
            for key, value in details.items():
                if key != 'keywords' and key != 'patterns':
                    report += f"║   {key}: {value:<50} ║\n"
    
    report += "╚══════════════════════════════════════════════════════════════╝"
    return report


def format_filter_report(result: Dict) -> str:
    """
    Formater un rapport de filtrage
    
    Args:
        result: Résultat du filtrage
        
    Returns:
        Rapport formaté
    """
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     FILTER REPORT                            ║
╠══════════════════════════════════════════════════════════════╣
║ Response: {result['response']:<48} ║
║ Safe: {str(result.get('is_safe', True)):<52} ║
"""
    
    if 'leakage_check' in result:
        leakage = result['leakage_check']
        report += f"║ Has Leakage: {str(leakage['has_leakage']):<44} ║\n"
        report += f"║ Leakage Score: {leakage['leakage_score']:.4f}{' ' * 38} ║\n"
    
    report += "╚══════════════════════════════════════════════════════════════╝"
    return report


if __name__ == "__main__":
    # Test du logger
    logger = Logger()
    logger.log_detection("Test prompt", True, 0.95)
    
    # Test des métriques
    metrics = MetricsCollector()
    metrics.increment_counter('total_prompts_checked')
    metrics.increment_counter('malicious_detected')
    print(metrics.get_metrics())
