from playwright.sync_api import sync_playwright
import re
from urllib.parse import quote
import time

def clean_price_terabyte(price_str: str) -> float:
    if not price_str: return 0.0
    # A Terabyte usa formato R$ 1.234,56 ou apenas 1.234,56
    cleaned = re.sub(r'[^\d,]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except:
        return 0.0

def collect_terabyte(search_term: str):
    search_term = (search_term or "").strip()
    if not search_term: return []

    products = []
    with sync_playwright() as p:
        print(f"[Terabyte] Iniciando busca por: {search_term}...")
        browser = p.chromium.launch(headless=True)
        # Vamos usar um navegador Desktop real para a Terabyte
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        # URL de busca
        url = f"https://www.terabyteshop.com.br/busca?str={quote(search_term)}"
        
        try:
            page.goto(url, wait_until="load", timeout=60000)
            
            # Espera forçada para garantir o carregamento do conteúdo dinâmico
            page.wait_for_timeout(8000)
            
            # Vamos buscar todos os cards de produto
            # Na Terabyte os produtos ficam em divs com a classe 'p-container'
            cards = page.locator(".p-container, .product-item, div[class*='prod-']")
            count = cards.count()
            print(f"[Terabyte] Cards encontrados: {count}")

            for i in range(min(count, 30)):
                try:
                    card = cards.nth(i)
                    
                    # Nome do produto
                    title_el = card.locator(".prod-name, .product-item__name, h2").first
                    title = title_el.inner_text(timeout=2000).strip()
                    
                    # Filtro de Relevância
                    term_parts = search_term.lower().split()
                    if not all(part in title.lower() for part in term_parts): continue

                    # Preço à vista (geralmente em .prod-new-price ou .val-prod)
                    price_el = card.locator(".prod-new-price, .val-prod, #val-prod").first
                    price_text = price_el.inner_text(timeout=2000)
                    price_val = clean_price_terabyte(price_text)
                    
                    # Link
                    link_el = card.locator("a").first
                    href = link_el.get_attribute("href")
                    
                    if price_val > 100:
                        products.append({
                            "titulo": title,
                            "preco": price_val,
                            "link": href,
                            "loja": "Terabyte"
                        })
                except: continue

            # Backup caso o seletor de card falhe: buscar por links de produtos
            if not products:
                print("[Terabyte] Tentativa de emergência via links...")
                links = page.locator("a[href*='/produto/']")
                for i in range(min(links.count(), 20)):
                    try:
                        link_el = links.nth(i)
                        title = link_el.inner_text().strip()
                        if len(title) < 15: continue
                        
                        # Tenta achar o preço subindo no DOM até o container
                        container = link_el.locator("xpath=./ancestor::div[contains(@class, 'prod')][1]")
                        price_text = container.locator("text=/R\$.*/").first.inner_text(timeout=1000)
                        price_val = clean_price_terabyte(price_text)
                        
                        if price_val > 100:
                            products.append({
                                "titulo": title, "preco": price_val,
                                "link": link_el.get_attribute("href"),
                                "loja": "Terabyte"
                            })
                    except: continue

        except Exception as e:
            print(f"[Terabyte] Erro na coleta: {e}")
        finally:
            browser.close()
            
    # Filtro de unicidade
    unique = {p['link']: p for p in products if p.get('link')}.values()
    return list(unique)
