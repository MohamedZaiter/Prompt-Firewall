"""
Filtrage des réponses du modèle LLM
"""

import re
from typing import Dict, List
import yaml


class ResponseFilter:
    """Classe pour filtrer les réponses du modèle"""
    
    def __init__(self, config_or_path: str | Dict = "config.yaml"):
        """
        Initialiser le filtre
        
        Args:
            config_or_path: Chemin vers le fichier de configuration ou dict
        """
        if isinstance(config_or_path, dict):
            self.config = config_or_path
        else:
            self.config = self._load_config(config_or_path)
            
        self.filter_config = self.config.get('response_filter', {})
        
        self.check_leakage = self.filter_config.get('check_leakage', True)
        self.check_toxicity = self.filter_config.get('check_toxicity', False)
        self.max_personal_info_score = self.filter_config.get('max_personal_info_score', 0.3)
        
        # Patterns sensibles
        self.patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'api_key': r'[a-zA-Z0-9]{32,}',
            'password_mention': r'password[:\s=]+[^\s]+',
            'token': r'(token|bearer|auth)[:\s=]+[a-zA-Z0-9_-]+',
        }
    
    @staticmethod
    def _load_config(config_path: str) -> Dict:
        """Charger la configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'response_filter': {}}
    
    def detect_personal_info(self, text: str) -> Dict[str, List[str]]:
        """
        Détecter les informations personnelles
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire des informations détectées
        """
        found_info = {}
        
        for info_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_info[info_type] = matches
        
        return found_info
    
    def calculate_leakage_score(self, text: str) -> float:
        """
        Calculer un score de fuite d'informations
        
        Args:
            text: Texte à analyser
            
        Returns:
            Score de 0 à 1
        """
        found_info = self.detect_personal_info(text)
        
        if not found_info:
            return 0.0
        
        # Compter le nombre d'informations trouvées
        total_findings = sum(len(matches) for matches in found_info.values())
        
        # Normaliser par rapport à la longueur du texte
        text_length = len(text.split())
        score = min(total_findings / max(text_length / 10, 1), 1.0)
        
        return score
    
    def check_for_leakage(self, text: str) -> Dict:
        """
        Vérifier la présence de fuites d'informations
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec les résultats
        """
        found_info = self.detect_personal_info(text)
        leakage_score = self.calculate_leakage_score(text)
        
        has_leakage = leakage_score > self.max_personal_info_score
        
        return {
            'has_leakage': has_leakage,
            'leakage_score': leakage_score,
            'info_found': found_info,
            'info_types': list(found_info.keys())
        }
    
    def redact_sensitive_info(self, text: str) -> str:
        """
        Masquer les informations sensibles
        
        Args:
            text: Texte à redacter
            
        Returns:
            Texte avec les infos masquées
        """
        redacted_text = text
        
        for info_type, pattern in self.patterns.items():
            replacement = f"[{info_type.upper()}]"
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def filter_response(self, text: str, redact: bool = False) -> Dict:
        """
        Filtrer une réponse complète
        
        Args:
            text: Réponse à filtrer
            redact: Masquer les infos sensibles
            
        Returns:
            Dictionnaire avec les résultats
        """
        result = {
            'original_length': len(text),
            'is_safe': True,
            'warnings': []
        }
        
        # Vérifier les fuites
        if self.check_leakage:
            leakage_result = self.check_for_leakage(text)
            result['leakage_check'] = leakage_result
            
            if leakage_result['has_leakage']:
                result['is_safe'] = False
                result['warnings'].append(f"Fuite d'informations détectée: {leakage_result['info_types']}")
        
        # Redacter si nécessaire
        if redact and not result['is_safe']:
            result['redacted_text'] = self.redact_sensitive_info(text)
        
        return result


if __name__ == "__main__":
    filter = ResponseFilter()
    
    test_responses = [
        "Machine learning is a fascinating field of AI.",
        "Contact me at john@example.com or call 555-123-4567",
        "Your API key is: sk_live_1234567890abcdef",
    ]
    
    print("=== Test du filtre de réponses ===\n")
    for response in test_responses:
        result = filter.filter_response(response, redact=True)
        print(f"Response: {response[:50]}...")
        print(f"Is Safe: {result['is_safe']}")
        if 'redacted_text' in result:
            print(f"Redacted: {result['redacted_text']}")
        print()
