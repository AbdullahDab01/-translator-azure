import os
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

DEFAULT_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
DEFAULT_FROM_LANG = "en"
DEFAULT_TO_LANG = "pt-br"


def translate_texts(texts: List[str], from_lang: str = DEFAULT_FROM_LANG, to_lang: str = DEFAULT_TO_LANG) -> List[str]:
    """Translate a list of texts using Azure Translator."""
    load_dotenv()
    key = os.getenv("TRANSLATOR_KEY")
    region = os.getenv("TRANSLATOR_LOCATION")
    endpoint = os.getenv("TRANSLATOR_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")

    if not key or not region:
        raise RuntimeError("TRANSLATOR_KEY e TRANSLATOR_LOCATION precisam estar definidos no .env")

    url = f"{endpoint}/translate"
    params = {"api-version": "3.0", "from": from_lang, "to": to_lang}
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json",
    }
    payload = [{"text": text} for text in texts]

    try:
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        raise RuntimeError(f"Falha na tradução: {http_err.response.status_code} {http_err.response.text}") from http_err
    except requests.RequestException as req_err:
        raise RuntimeError(f"Erro ao chamar o Translator: {req_err}") from req_err

    body = response.json()
    translations: List[str] = []
    for item in body:
        translation = item.get("translations", [{}])[0].get("text")
        translations.append(translation or "")

    return translations


def fetch_content(url: str, selectors: List[str]) -> List[Dict[str, str]]:
    """Fetch HTML and return ordered elements filtered by selectors."""
    headers = {"User-Agent": "azure-translator-scraper/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        raise RuntimeError(f"Falha ao buscar conteúdo: {http_err.response.status_code} {http_err.response.text}") from http_err
    except requests.RequestException as req_err:
        raise RuntimeError(f"Erro de rede ao buscar conteúdo: {req_err}") from req_err

    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.select(",".join(selectors))

    content: List[Dict[str, str]] = []
    for element in elements:
        text = element.get_text(" ", strip=True)
        if not text:
            continue
        tag = element.name.lower() if element.name else "p"
        content.append({"tag": tag, "text": text})

    return content


def save_markdown(structured_items: List[Dict[str, str]], translated_texts: List[str], output_path: str) -> None:
    """Persist translated content to a Markdown file following the original tag structure."""
    lines: List[str] = []

    for item, translated in zip(structured_items, translated_texts):
        tag = item.get("tag", "p")
        text = translated.strip()

        if tag == "h1":
            lines.append(f"# {text}")
        elif tag == "h2":
            lines.append(f"## {text}")
        elif tag == "h3":
            lines.append(f"### {text}")
        elif tag == "li":
            lines.append(f"- {text}")
        elif tag == "blockquote":
            lines.append(f"> {text}")
        else:
            lines.append(text)

        if tag not in {"li"}:
            lines.append("")  # blank line for readability

    with open(output_path, "w", encoding="utf-8") as md_file:
        md_file.write("\n".join(lines).strip() + "\n")


def main() -> int:
    load_dotenv()

    url = os.getenv(
        "SOURCE_URL",
        "https://learn.microsoft.com/en-us/azure/ai-services/translator/translator-overview",
    )
    selectors = ["h1", "h2", "h3", "p", "li", "blockquote"]

    try:
        items = fetch_content(url, selectors)
    except Exception as exc:  # noqa: BLE001
        print(f"Erro ao extrair conteúdo: {exc}")
        return 1

    if not items:
        print("Nenhum conteúdo encontrado para traduzir.")
        return 1

    texts = [item["text"] for item in items]

    try:
        translated = translate_texts(texts)
    except Exception as exc:  # noqa: BLE001
        print(f"Erro ao traduzir conteúdo: {exc}")
        return 1

    output_path = "conteudo_traduzido.md"
    save_markdown(items, translated, output_path)

    print(f"Tradução concluída e salva em {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
