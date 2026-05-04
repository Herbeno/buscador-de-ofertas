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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api", tags=["Home"])
def api_status():
    return {
        "message": "Buscador de Ofertas API está online!",
        "docs": "/docs",
        "example": "/search?item=RTX 4060",
    }

@app.get("/search")
def search(
    item: str = Query(
        ...,
        min_length=1,
        description="Termo de busca no Mercado Livre.",
    ),
):
    # Voltamos ao coletor original estável do Mercado Livre
    raw_products = collect_products(item)
    
    if not raw_products:
        return {"error": "Nenhum produto encontrado ou erro no scraper.", "results": []}

    # Converte para DataFrame para facilitar a análise
    df = pd.DataFrame(raw_products)
    
    # Lógica de Análise Estatística
    mediana = df['preco'].median()
    
    # Filtramos itens que estão entre 30% e 300% da mediana para evitar ruído
    df_clean = df[(df['preco'] >= mediana * 0.3) & (df['preco'] <= mediana * 3.0)].copy()
    
    # Identifica ofertas (10% abaixo da mediana dos itens filtrados)
    mediana_limpa = df_clean['preco'].median()
    limite_oferta = mediana_limpa * 0.9
    
    df_clean['is_deal'] = df_clean['preco'] <= limite_oferta
    
    # Ordena por preço
    df_sorted = df_clean.sort_values(by='preco')
    
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

@app.get("/", tags=["Home"], include_in_schema=False)
def serve_app():
    index = WEB_DIR / "index.html"
    if not index.is_file():
        return {"error": "Interface web não encontrada."}
    return FileResponse(index)

app.mount("/assets", StaticFiles(directory=str(WEB_DIR)), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
