"""
Prétraitement des données pour le pare-feu LLM
"""

import re
import string
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


class Preprocessor:
    """Classe pour prétraiter les textes"""
    
    def __init__(self):
        """Initialiser le préprocesseur"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stopwords = set(stopwords.words('english'))
        self.stopwords.update(stopwords.words('french'))
    
    def clean_text(self, text: str) -> str:
        """
        Nettoyer le texte
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not isinstance(text, str):
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Supprimer les adresses email
        text = re.sub(r'\S+@\S+', '', text)
        
        # Supprimer les caractères spéciaux mais garder les espaces
        text = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizer le texte
        
        Args:
            text: Texte à tokenizer
            
        Returns:
            Liste de tokens
        """
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Supprimer les mots vides
        
        Args:
            tokens: Liste de tokens
            
        Returns:
            Tokens sans mots vides
        """
        return [token for token in tokens if token not in self.stopwords and len(token) > 1]
    
    def preprocess(self, text: str, remove_stops: bool = False) -> str:
        """
        Prétraiter le texte complet
        
        Args:
            text: Texte à prétraiter
            remove_stops: Supprimer les mots vides
            
        Returns:
            Texte prétraité
        """
        # Nettoyer
        text = self.clean_text(text)
        
        # Tokenizer et traiter
        if remove_stops:
            tokens = self.tokenize(text)
            tokens = self.remove_stopwords(tokens)
            return ' '.join(tokens)
        
        return text
    
    def extract_n_grams(self, text: str, n: int = 2) -> List[str]:
        """
        Extraire les n-grammes
        
        Args:
            text: Texte à traiter
            n: Taille des n-grammes
            
        Returns:
            Liste de n-grammes
        """
        tokens = self.tokenize(text)
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


if __name__ == "__main__":
    processor = Preprocessor()
    
    sample_text = "Check this suspicious link: https://malicious.com or email me@test.com"
    print(f"Original: {sample_text}")
    print(f"Cleaned: {processor.clean_text(sample_text)}")
    print(f"Preprocessed: {processor.preprocess(sample_text, remove_stops=True)}")
