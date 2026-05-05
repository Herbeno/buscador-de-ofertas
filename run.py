import sys
import os
import uvicorn

# Adiciona o diretório atual ao path para que o Python encontre 'scraper' e 'api'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import app

if __name__ == "__main__":
    print("Iniciando o Buscador de Ofertas na porta 8085...")
    print("Acesse: http://localhost:8085")
    uvicorn.run(app, host="127.0.0.1", port=8085)
