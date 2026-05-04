from playwright.sync_api import sync_playwright
import re
from urllib.parse import quote
import time

def clean_price_kabum(price_str: str) -> float:
    if not price_str: return 0.0
    # Procura por padrões de preço como 1.234,56 ou 234,56
    # No mobile, o preço às vezes aparece colado com outros textos
    nums = re.findall(r'[\d\.]+\,\d{2}', price_str)
    if not nums: return 0.0
    
    prices = []
    for n in nums:
        try:
            val = float(n.replace('.', '').replace(',', '.'))
            if val > 50: prices.append(val)
        except: continue
    # Retorna o menor preço encontrado no bloco (geralmente o à vista)
    return min(prices) if prices else 0.0

def collect_kabum(search_term: str):
    search_term = (search_term or "").strip()
    if not search_term: return []

    products = []
    with sync_playwright() as p:
        print(f"[Kabum] Iniciando busca por: {search_term}...")
        browser = p.chromium.launch(headless=True)
        # Usando um User-Agent de Mobile que é mais difícil de bloquear e tem DOM mais simples
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
            viewport={'width': 390, 'height': 844},
            is_mobile=True
        )
        page = context.new_page()

        url = f"https://www.kabum.com.br/busca?query={quote(search_term)}"
        
        try:
            page.goto(url, wait_until="load", timeout=60000)
            page.wait_for_timeout(8000) # Espera o JS renderizar
            
            # No mobile, os produtos ficam dentro de tags 'article' ou links diretos
            # Vamos buscar os containers de produtos
            cards = page.locator("article, a[href*='/produto/']")
            count = cards.count()
            print(f"[Kabum] Elementos detectados: {count}")

            for i in range(min(count, 30)):
                try:
                    card = cards.nth(i)
                    text = card.inner_text().strip()
                    if len(text) < 30: continue # Ignora elementos pequenos (menus, etc)
                    
                    # Tenta extrair o título: geralmente é o primeiro texto longo ou um H3
                    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
                    if not lines: continue
                    
                    title = lines[0]
                    # Se a primeira linha for algo como "-10%" ou "SELO", pega a próxima
                    if any(x in title.upper() for x in ["%", "SELO", "FRETE", "DESCONTO"]):
                        if len(lines) > 1: title = lines[1]

                    price_val = clean_price_kabum(text)
                    
                    # Garante que pegamos o link correto
                    href = card.get_attribute("href")
                    if not href:
                        link_el = card.locator("a").first
                        href = link_el.get_attribute("href") if link_el.count() else None
                    
                    full_link = f"https://www.kabum.com.br{href}" if href and href.startswith("/") else href
                    
                    # Filtro para garantir que o título contém o termo de busca (parcialmente)
                    # e que o preço é razoável
                    term_parts = search_term.lower().split()
                    matches_term = any(part in title.lower() for part in term_parts)

                    if price_val > 100 and matches_term:
                        products.append({
                            "titulo": title,
                            "preco": price_val,
                            "link": full_link or "#",
                            "loja": "Kabum"
                        })
                except: continue
                    
        except Exception as e:
            print(f"[Kabum] Erro: {e}")
        finally:
            browser.close()
            
    # Filtro final de unicidade e relevância
    unique = {}
    for p in products:
        if p['link'] not in unique or p['preco'] < unique[p['link']]['preco']:
            unique[p['link']] = p
            
    return list(unique.values())
