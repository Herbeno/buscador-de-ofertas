# Buscador de Ofertas: Sistema de Monitoramento e Análise Estatística

## 1. Visão Geral
Este projeto consiste em uma aplicação Full-Stack desenvolvida para a coleta automatizada, processamento e análise de dados de mercado em tempo real. O sistema utiliza técnicas avançadas de Web Scraping para extrair informações de grandes plataformas de e-commerce, aplicando modelos estatísticos para identificar distorções de preço e oportunidades reais de compra (deals).

## 2. Arquitetura do Sistema
A solução é estruturada em três camadas modulares:

*   **Data Collection (Scraper):** Motor de extração desenvolvido em Python com a biblioteca Playwright. Implementa estratégias de navegação assíncrona e simulação de User-Agents para garantir a estabilidade e eficiência das requisições.
*   **Analytics API (Backend):** Camada desenvolvida em FastAPI que orquestra a coleta de dados e utiliza a biblioteca Pandas para o tratamento estatístico dos resultados em tempo real.
*   **Interface (Frontend):** Aplicação SPA desenvolvida em React 19 e TypeScript. Utiliza Tailwind CSS 4 para a interface de usuário e Framer Motion para o gerenciamento de estados visuais e transições.

## 3. Metodologia de Análise de Dados
O diferencial desta ferramenta reside na filtragem inteligente de ruídos, seguindo o seguinte fluxo lógico:

1.  **Tratamento de Outliers:** O sistema calcula a mediana inicial do conjunto de dados. Registros com preços inferiores a 30% ou superiores a 300% da mediana são descartados automaticamente para mitigar o impacto de anúncios irrelevantes (acessórios, peças avulsas ou valores simbólicos).
2.  **Cálculo da Mediana Refinada:** Após a limpeza, uma nova mediana é estabelecida, representando o valor de mercado atualizado para o termo pesquisado.
3.  **Detecção de Oportunidades (Deals):** É definido um limite de oferta (threshold) de 10% abaixo da mediana refinada. Itens que cruzam este limite são classificados pelo algoritmo como "Ofertas Reais".

## 4. Requisitos Técnicos
*   Python 3.10+
*   Node.js 20+
*   Playwright Browsers

## 5. Instalação e Execução

### Backend
1. Navegue até o diretório raiz do projeto.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação via script de inicialização:
   ```bash
   python run.py
   ```

### Frontend
1. Navegue até o diretório `frontend`.
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Inicie o ambiente de desenvolvimento:
   ```bash
   npm run dev
   ```

## 6. Considerações Técnicas e Éticas
Esta ferramenta foi desenvolvida com fins estritamente educacionais para o estudo de engenharia de dados e automação. O motor de busca implementa delays controlados para respeitar a integridade dos servidores de origem. O sistema de detecção de ofertas é baseado puramente em critérios estatísticos e não deve ser interpretado como recomendação de compra.

---
**Herben Oliveira**  
Analista de Dados | Backend & Automações
