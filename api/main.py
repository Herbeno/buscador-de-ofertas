from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from scraper.collector import collect_products
import pandas as pd
import numpy as np

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(
    title="Buscador de Ofertas API",
    description="API dinâmica que busca produtos no Mercado Livre e identifica as melhores ofertas usando análise estatística.",
    version="1.0.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substituir pelo domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api", tags=["Home"])
def api_status():
    return {
        "message": "Buscador de Ofertas API está online!",
        "docs": "/docs",
        "example": "/search?item=monitor 27",
    }


@app.get("/", tags=["Home"], include_in_schema=False)
def serve_app():
    index = WEB_DIR / "index.html"
    if not index.is_file():
        return {"error": "Interface web não encontrada (pasta web/)."}
    return FileResponse(index)

@app.get("/search")
def search(
    item: str = Query(
        ...,
        min_length=1,
        description="Termo de busca no Mercado Livre (ex.: placa de vídeo, notebook, fone).",
    ),
):
    raw_products = collect_products(item)
    
    if not raw_products:
        return {"error": "Nenhum produto encontrado ou erro no scraper", "results": []}

    # Converte para DataFrame para facilitar a análise
    df = pd.DataFrame(raw_products)
    
    # Lógica de Análise (Filtro de ruído e cálculo de ofertas)
    # Filtro básico: remove itens com preço 0 ou fora de uma curva estatística normal (outliers)
    # Para buscas genéricas, usamos a mediana como base
    mediana = df['preco'].median()
    
    # Filtramos itens que estão entre 30% e 300% da mediana para evitar acessórios ou itens errados
    df_clean = df[(df['preco'] >= mediana * 0.3) & (df['preco'] <= mediana * 3.0)].copy()
    
    # Identifica ofertas (10% abaixo da mediana dos itens filtrados)
    mediana_limpa = df_clean['preco'].median()
    limite_oferta = mediana_limpa * 0.9
    
    df_clean['is_deal'] = df_clean['preco'] <= limite_oferta
    
    # Ordena por preço
    df_sorted = df_clean.sort_values(by='preco')
    
    # Retorna os dados
    return {
        "search_term": item,
        "stats": {
            "total_found": len(raw_products),
            "valid_items": len(df_clean),
            "median_price": float(mediana_limpa),
            "deal_threshold": float(limite_oferta)
        },
        "deals": df_sorted[df_sorted['is_deal']].to_dict(orient="records"),
        "others": df_sorted[~df_sorted['is_deal']].to_dict(orient="records")
    }

app.mount("/assets", StaticFiles(directory=str(WEB_DIR)), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
