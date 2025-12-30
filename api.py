"""
FastAPI Example - LLM Firewall API
Exemple d'API FastAPI pour intégrer le pare-feu LLM
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.firewall import LLMFirewall
from src.response_filter import ResponseFilter
from src.utils import Logger

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize app
app = FastAPI(
    title="LLM Firewall API",
    description="API pour la détection de prompts malveillants",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Initialize firewall and components
firewall = LLMFirewall()
response_filter = ResponseFilter()
logger = Logger()

# ============================================================================
# MODELS
# ============================================================================

class PromptCheckRequest(BaseModel):
    """Demande de vérification de prompt"""
    prompt: str
    use_ml: bool = True


class PromptCheckResponse(BaseModel):
    """Réponse de vérification de prompt"""
    prompt: str
    is_malicious: bool
    confidence: float
    detection_methods: dict


class ResponseFilterRequest(BaseModel):
    """Demande de filtrage de réponse"""
    response: str
    redact: bool = True


class ResponseFilterResponse(BaseModel):
    """Réponse du filtrage"""
    is_safe: bool
    leakage_score: float
    info_types: List[str]
    redacted_text: str = None


class BatchCheckRequest(BaseModel):
    """Demande de vérification en batch"""
    prompts: List[str]
    use_ml: bool = True


class HealthResponse(BaseModel):
    """Réponse de santé"""
    status: str
    firewall_ready: bool
    ml_models_loaded: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifier l'état du service"""
    stats = firewall.get_statistics()
    return HealthResponse(
        status="ok",
        firewall_ready=True,
        ml_models_loaded=stats['ml_models_loaded']
    )


@app.post("/check-prompt", response_model=PromptCheckResponse)
async def check_prompt(request: PromptCheckRequest):
    """
    Vérifier si un prompt est malveillant
    
    Paramètres:
    - prompt: Le prompt à vérifier
    - use_ml: Utiliser les modèles ML (par défaut: True)
    
    Retour:
    - is_malicious: True si malveillant
    - confidence: Score de confiance [0-1]
    - detection_methods: Détails des détections
    """
    try:
        if not request.prompt or len(request.prompt) == 0:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        result = firewall.check_prompt(request.prompt, use_ml=request.use_ml)
        
        # Log detection
        logger.log_detection(
            request.prompt,
            result['is_malicious'],
            result['confidence']
        )
        
        return PromptCheckResponse(
            prompt=result['prompt'],
            is_malicious=result['is_malicious'],
            confidence=result['confidence'],
            detection_methods=result['detection_methods']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-batch")
async def check_batch(request: BatchCheckRequest):
    """
    Vérifier plusieurs prompts
    
    Paramètres:
    - prompts: Liste de prompts
    - use_ml: Utiliser les modèles ML
    
    Retour:
    - results: Liste des résultats
    """
    try:
        if not request.prompts:
            raise HTTPException(status_code=400, detail="Prompts list cannot be empty")
        
        results = firewall.batch_check(request.prompts)
        
        return {
            "count": len(results),
            "malicious_count": sum(1 for r in results if r['is_malicious']),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/filter-response", response_model=ResponseFilterResponse)
async def filter_response(request: ResponseFilterRequest):
    """
    Filtrer une réponse pour détecter les fuites
    
    Paramètres:
    - response: La réponse à filtrer
    - redact: Masquer les infos sensibles
    
    Retour:
    - is_safe: True si sûr
    - leakage_score: Score de fuite [0-1]
    - info_types: Types d'infos détectées
    - redacted_text: Texte masqué si requested
    """
    try:
        if not request.response or len(request.response) == 0:
            raise HTTPException(status_code=400, detail="Response cannot be empty")
        
        result = response_filter.filter_response(
            request.response,
            redact=request.redact
        )
        
        # Log filtering
        if 'leakage_check' in result:
            logger.log_filter(
                request.response,
                result['leakage_check']['has_leakage'],
                result['leakage_check']['info_types']
            )
        
        return ResponseFilterResponse(
            is_safe=result.get('is_safe', True),
            leakage_score=result.get('leakage_check', {}).get('leakage_score', 0),
            info_types=result.get('leakage_check', {}).get('info_types', []),
            redacted_text=result.get('redacted_text')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """Obtenir les statistiques du pare-feu"""
    return firewall.get_statistics()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'erreurs HTTP"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


# ============================================================================
# DOCUMENTATION
# ============================================================================

@app.get("/docs")
async def get_docs():
    """Documentation de l'API"""
    return {
        "title": "LLM Firewall API",
        "version": "0.1.0",
        "endpoints": {
            "/health": "GET - Vérifier l'état du service",
            "/check-prompt": "POST - Vérifier un prompt",
            "/check-batch": "POST - Vérifier plusieurs prompts",
            "/filter-response": "POST - Filtrer une réponse",
            "/statistics": "GET - Obtenir les statistiques"
        }
    }


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("Starting LLM Firewall API...")
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================================================
# UTILISATION
# ============================================================================

"""
Pour utiliser l'API:

1. Installation des dépendances API:
   pip install fastapi uvicorn

2. Démarrage du serveur:
   python api.py

3. Tests avec curl:
   
   # Health check
   curl http://localhost:8000/health
   
   # Vérifier un prompt
   curl -X POST http://localhost:8000/check-prompt \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What is machine learning?",
       "use_ml": true
     }'
   
   # Vérifier plusieurs prompts
   curl -X POST http://localhost:8000/check-batch \
     -H "Content-Type: application/json" \
     -d '{
       "prompts": ["prompt1", "prompt2"],
       "use_ml": true
     }'
   
   # Filtrer une réponse
   curl -X POST http://localhost:8000/filter-response \
     -H "Content-Type: application/json" \
     -d '{
       "response": "Email: test@example.com",
       "redact": true
     }'

4. Accéder à la documentation interactive:
   http://localhost:8000/docs
"""
