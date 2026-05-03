import pandas as pd
import os

def analyze_data(file_path="data/raw_data.csv"):
    if not os.path.exists(file_path):
        print(f"[ERRO] Arquivo {file_path} não encontrado. Rode o scraper primeiro.")
        return

    # Carrega os dados
    df = pd.read_csv(file_path)
    
    if df.empty:
        print("[ERRO] O arquivo de dados está vazio.")
        return

    total_inicial = len(df)
    
    # Filtro de Preço (Remover acessórios e anúncios absurdos)
    df_clean = df[(df['preco'] >= 1400) & (df['preco'] <= 4500)].copy()
    
    # Filtro de Palavras-Chave (Remover "caixas", "defeitos", etc)
    keywords_to_ignore = ['caixa', 'box', 'defeito', 'estragada', 'apenas', 'cooler', 'vazia']
    pattern = '|'.join(keywords_to_ignore)
    df_clean = df_clean[~df_clean['titulo'].str.contains(pattern, case=False, na=False)]
    
    total_final = len(df_clean)
    
    print("--- Relatório de Análise ---")
    print(f"Total de anúncios analisados: {total_inicial}")
    print(f"Anúncios válidos após filtragem: {total_final}")
    print(f"Itens descartados (ruído): {total_inicial - total_final}")
    
    if df_clean.empty:
        print("[AVISO] Nenhum anúncio restou após a filtragem. Verifique os critérios.")
        return

    # Estatísticas
    preco_medio = df_clean['preco'].mean()
    preco_min = df_clean['preco'].min()
    preco_mediano = df_clean['preco'].median()
    
    print(f"\n--- Estatísticas de Preço ---")
    print(f"Preço Médio:   R$ {preco_medio:.2f}")
    print(f"Preço Mediano: R$ {preco_mediano:.2f}")
    print(f"Melhor Preço:  R$ {preco_min:.2f}")
    
    # Identificando Ofertas (10% abaixo da mediana)
    limite_oferta = preco_mediano * 0.9
    ofertas = df_clean[df_clean['preco'] <= limite_oferta].sort_values(by='preco')
    
    print(f"\n--- Top 3 Melhores Ofertas (Abaixo de R$ {limite_oferta:.2f}) ---")
    if not ofertas.empty:
        for idx, row in ofertas.head(3).iterrows():
            print(f"- R$ {row['preco']:.2f} | {row['titulo'][:50]}...")
            print(f"  Link: {row['link']}")
    else:
        print("Nenhuma oferta encontrada no momento.")

if __name__ == "__main__":
    analyze_data()
