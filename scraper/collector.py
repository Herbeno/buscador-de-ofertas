from playwright.sync_api import sync_playwright
import pandas as pd
import os
import re
from urllib.parse import quote

def clean_price(price_str: str) -> float:
    """Limpa a string de preço e converte para float."""
    if not price_str:
        return 0.0
    # Remove pontos de milhar e substitui vírgula por ponto (se houver)
    cleaned = re.sub(r'[^\d]', '', price_str)
    return float(cleaned)

def _mercadolivre_lista_url(search_term: str) -> str:
    """Monta a URL de listagem do ML a partir do termo livre (espaços viram hífens)."""
    segment = "-".join(search_term.strip().split())
    if not segment:
        raise ValueError("Termo de busca vazio")
    encoded = quote(segment, safe="-")
    return f"https://lista.mercadolivre.com.br/{encoded}"


def collect_products(search_term: str = "RTX 3060"):
    """
    Coleta anúncios do Mercado Livre para qualquer termo de busca.
    O mesmo fluxo usado pela API (`/search?item=`) e pelo front quando enviar o termo.
    Retorna uma lista de dicionários: titulo, preco, link.
    """
    search_term = (search_term or "").strip()
    if not search_term:
        return []

    products = []
    with sync_playwright() as p:
        print(f"Iniciando busca por: {search_term}...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = _mercadolivre_lista_url(search_term)
        page.goto(url, wait_until="networkidle")
        
        try:
            page.wait_for_selector(".ui-search-layout, .poly-card", timeout=10000)
        except:
            print("[ERRO] Tempo de carregamento esgotado ou layout não reconhecido.")
            browser.close()
            return []
        
        items = page.locator(".ui-search-layout__item, .poly-card")
        count = items.count()
        
        if count == 0:
            print("[ERRO] Nenhum item encontrado na página.")
            browser.close()
            return []

        print(f"[OK] Encontrados {count} itens. Extraindo dados...")
        
        page.evaluate("window.scrollTo(0, 500)")
        
        for i in range(min(count, 30)):
            item = items.nth(i)
            try:
                title = item.locator("h2, h3, .ui-search-item__title").first.inner_text(timeout=3000)
                price_text = item.locator(".andes-money-amount__fraction").first.inner_text(timeout=3000)
                price_val = clean_price(price_text)
                link = item.locator("a").first.get_attribute("href")
                
                products.append({
                    "titulo": title,
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
    if results:
        df = pd.DataFrame(results)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/raw_data.csv", index=False, encoding="utf-8")
        print(f"\n[OK] Sucesso! {len(results)} produtos salvos em data/raw_data.csv")
    else:
        print("[ERRO] Falha na coleta.")
