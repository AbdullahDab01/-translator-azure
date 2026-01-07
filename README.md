# Tradutor de Artigos Técnicos com AzureAI

Projeto do bootcamp DIO para o Microsoft Certification Challenge #1 (AI-102). A aplicação em Python extrai conteúdo de páginas da web e traduz para português usando o Azure Cognitive Services Translator API, gerando um arquivo Markdown organizado.

## Funcionalidades
- Extrai títulos, parágrafos, listas e citações via seletores CSS (h1, h2, h3, p, li, blockquote).
- Tradução de inglês para português (pt-br) pelo Azure Translator REST API v3.0.
- Salva o conteúdo traduzido em `conteudo_traduzido.md` mantendo a estrutura em Markdown.
- Uso de variáveis de ambiente para credenciais, sem chaves hardcoded.

## Pré-requisitos
- Python 3.8+
- Conta e chave do Azure Translator (Cognitive Services) com região (ex.: brazilsouth)
- Acesso à internet para a página a ser traduzida e para o endpoint do Translator

## Instalação
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Configuração
1) Copie o template de variáveis e preencha suas chaves:
```bash
cp .env.example .env
```
2) Edite `.env` e informe:
- `TRANSLATOR_KEY`: sua chave do Azure Translator
- `TRANSLATOR_LOCATION`: região do recurso (ex.: brazilsouth)
- `TRANSLATOR_ENDPOINT`: opcional, mantém o padrão `https://api.cognitive.microsofttranslator.com`
- `SOURCE_URL`: opcional, URL padrão para ser traduzida (pode ser definida em tempo de execução alterando o código)

## Uso
```bash
python main.py
```
- O script carrega o `SOURCE_URL` (ou o valor padrão), extrai o conteúdo pelos seletores suportados e envia para tradução.
- A saída é gravada em `conteudo_traduzido.md` na raiz do projeto.

### Alterando URL ou seletores
- No `main.py`, ajuste a variável `url` em `main()` ou defina `SOURCE_URL` no `.env`.
- Para focar em partes específicas, modifique a lista `selectors = ["h1", "h2", "h3", "p", "li", "blockquote"]` e inclua/remova seletores CSS de interesse.

## Boas práticas para produção
- Armazene segredos em Azure Key Vault ou Azure App Configuration, evitando `.env` em ambientes produtivos.
- Habilite logging estruturado e monitore limites de uso da API do Translator.
- Trate paginações ou conteúdos dinâmicos conforme a origem do artigo (pode exigir Selenium ou APIs dedicadas).

## Estrutura do Azure Translator usada
- Endpoint: `/translate?api-version=3.0&from=en&to=pt-br`
- Cabeçalhos: `Ocp-Apim-Subscription-Key`, `Ocp-Apim-Subscription-Region`, `Content-Type: application/json`
- Corpo: `[{"text": "conteudo"}]`

## Tópicos
python, azure, rest-api, ia, azureai
