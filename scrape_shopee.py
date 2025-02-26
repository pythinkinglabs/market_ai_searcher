import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# 1. Definir o esquema de extração com seletores CSS para cada campo desejado
schema = {
    "name": "Shopee Popular Products",
    # Seleciona cada item de produto na listagem da Shopee
    "baseSelector": "div[data-sqe='item']",
    "fields": [
        {   # Nome do produto
            "name": "nome",
            "selector": "div._1NoI8_._16BAGk",  # seletor CSS para o nome do produto
            "type": "text"
        },
        {   # Preço do produto
            "name": "preco",
            "selector": "span._341bF0",  # seletor CSS para o preço
            "type": "text"
        },
        {   # Vendedor (loja) - na listagem da Shopee geralmente aparece a localidade ou nome da loja
            "name": "vendedor",
            "selector": "div._3amru2",  # seletor CSS para o texto do vendedor/loja (ou localidade)
            "type": "text"
        },
        {   # Número de vendas (unidades vendidas)
            "name": "vendidos",
            "selector": "div._18SLBt",  # seletor CSS para o texto de vendidos (e possivelmente avaliações)
            "type": "text"
        },
        # { # Avaliações (opcional: algumas páginas podem não exibir diretamente na listagem)
        #   "name": "avaliacoes",
        #   "selector": "div.selector_avaliacoes",  # *Exemplo* de seletor se disponível
        #   "type": "text"
        # }
    ]
}

# 2. Criar a estratégia de extração JSON a partir do esquema definido
extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

# 3. Configurar opções do crawler (ex: evitar cache e esperar o carregamento dos itens)
config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,                 # não usar cache (pegar sempre dados atualizados)
    wait_for="css=div[data-sqe='item']",         # espera o elemento base dos produtos aparecer
    extraction_strategy=extraction_strategy      # define a estratégia de extração criada
)

# 4. Função principal assíncrona para executar a coleta
async def coletar_produtos_populares():
    # URL de busca na Shopee ordenada por número de vendas (produtos populares)
    url = "https://shopee.com.br/search?keyword=a&sortBy=sales"
    # Inicia o crawler assíncrono
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            print("Falha na coleta:", result.error_message)
            return
        # Extrai e carrega o conteúdo JSON retornado
        dados_json = json.loads(result.extracted_content)
        # Ordena os produtos por número de vendidos (criterio de popularidade) - opcional
        # Aqui poderíamos converter o texto de 'vendidos' para número e ordenar. Exemplo simplificado:
        # dados_json.sort(key=lambda item: int(''.join(filter(str.isdigit, item['vendidos']))), reverse=True)
        # 5. Exibe os dados coletados na tela
        print("Produtos mais populares encontrados:\n")
        for produto in dados_json[:10]:  # limitando a exibição aos top 10, por exemplo
            nome = produto.get("nome", "").strip()
            preco = produto.get("preco", "").strip()
            vendedor = produto.get("vendedor", "").strip()
            vendidos = produto.get("vendidos", "").strip()
            print(f"- {nome}\n  Preço: {preco} | Vendedor: {vendedor} | Vendidos: {vendidos}\n")

# 6. Executa a função assíncrona principal
asyncio.run(coletar_produtos_populares())
