from playwright.sync_api import sync_playwright
import pandas as pd
import os
import re
from urllib.parse import quote

def clean_price(price_str: str) -> float:
    """Limpa a string de preço e converte para float."""
    if not price_str:
        return 0.0
    # Remove tudo que não for dígito
    cleaned = re.sub(r'[^\d]', '', price_str)
    try:
        return float(cleaned)
    except:
        return 0.0

def _mercadolivre_lista_url(search_term: str) -> str:
    """Monta a URL de listagem do ML a partir do termo livre."""
    segment = "-".join(search_term.strip().split())
    if not segment:
        raise ValueError("Termo de busca vazio")
    encoded = quote(segment, safe="-")
    return f"https://lista.mercadolivre.com.br/{encoded}"


def collect_products(search_term: str = "RTX 3060"):
    """
    Coleta anúncios do Mercado Livre.
    """
    search_term = (search_term or "").strip()
    if not search_term:
        return []

    products = []
    with sync_playwright() as p:
        print(f"Iniciando busca por: {search_term}...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = _mercadolivre_lista_url(search_term)
        
        try:
            # domcontentloaded é muito mais rápido que networkidle
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            # Espera carregar a estrutura de resultados
            page.wait_for_selector(".ui-search-results, .ui-search-layout", timeout=15000)
        except Exception as e:
            print(f"[AVISO] A página demorou a responder, mas tentaremos extrair o que carregou: {e}")

        # Seletores variados para cobrir diferentes layouts do ML
        items = page.locator(".ui-search-layout__item, .poly-card, .ui-search-result__wrapper")
        count = items.count()
        
        if count == 0:
            print("[ERRO] Nenhum item detectado.")
            browser.close()
            return []

        print(f"[OK] Encontrados {count} itens. Extraindo dados...")
        
        # Scroll suave para carregar imagens/lazy load se necessário
        page.evaluate("window.scrollTo(0, 600)")
        
        for i in range(min(count, 35)):
            try:
                item = items.nth(i)
                # Tenta pegar o título
                title = item.locator("h2, h3, .ui-search-item__title, .poly-component__title").first.inner_text(timeout=2000)
                # Tenta pegar o preço (fração principal)
                price_text = item.locator(".andes-money-amount__fraction, .poly-price__current .andes-money-amount__fraction").first.inner_text(timeout=2000)
                price_val = clean_price(price_text)
                
                # Tenta pegar o link
                link = item.locator("a").first.get_attribute("href")
                
                if title and price_val > 0:
                    products.append({
                        "titulo": title.strip(),
                        "preco": price_val,
                        "link": link
                    })
            except:
                continue

        browser.close()
    
    return products

if __name__ == "__main__":
    import sys
    term = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else "RTX 3060"
    results = collect_products(term)
    print(f"Total coletado: {len(results)}")
