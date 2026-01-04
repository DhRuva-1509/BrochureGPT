import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

from WebScrapper.scrape_site import scrape_site

# ─────────────────────────────────────────────
# Environment & LLM setup
# ─────────────────────────────────────────────

load_dotenv(override=True)

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

ollama = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)
SYSTEM_PROMPT = """
You are an expert brand copywriter and marketing strategist.

Your task is to write a compelling, emotionally engaging COMPANY BROCHURE.
This is NOT a summary or an informational article.

BROCHURE RULES:
- Write in persuasive, customer-facing language
- Use short sections with strong headings
- Highlight the experience, emotions, and lifestyle
- Avoid bullet-point facts unless used stylistically
- Do NOT sound like Wikipedia or a report
- Do NOT list locations mechanically
- Use warm, inviting, premium marketing language
- End with a clear call-to-action

FORMAT:
- Markdown
- NO code blocks
- Headings and short paragraphs only
"""

LINK_SYSTEM_PROMPT ="""
You are provided with a list of website links and the contents of those web pages. 
You are able to decide which links are relevant and must include in the creative brochure, such as About page or Company Page etc.

You should respond in JSON as in this example:

{
  "start_url": "https://url.com",
  "pages_scraped": 15,
  "pages": [
    {
      "title": "Title of the page",
      "text": "Contents of the page",
      "url": "https://url.com"
    },

"""

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def extract_links_and_content(scraped: dict) -> list[str]:
    items = []
    for page in scraped.get("pages", []):
        url = page.get("url")
        text = page.get("text", "")
        if url and text:
            items.append(f"{url}\n{text[:500]}")
    return items


def get_links_user_prompt(url: str) -> str:
    scraped = scrape_site(url)
    links = extract_links_and_content(scraped)

    prompt = f"""
Here is the list of links and contents on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email and Discord links.

Links (some might be relative links):
"""
    prompt += "\n\n".join(links)
    return prompt


def select_relevant_links(url: str) -> dict:
    response = ollama.chat.completions.create(
        model="gemma3:latest",
        messages=[
            {"role": "system", "content": LINK_SYSTEM_PROMPT},
            {"role": "user", "content": get_links_user_prompt(url)},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def format_scraped_content(scraped: dict, selected_links: dict) -> str:
    allowed = set(selected_links.get("links", []))
    sections = []

    for page in scraped.get("pages", []):
        if page.get("url") in allowed:
            title = page.get("title", "")
            text = page.get("text", "")
            sections.append(f"## {title}\n{text}")

    return "\n\n".join(sections)


# ─────────────────────────────────────────────
# Streaming LLM functions
# ─────────────────────────────────────────────

def stream_gemma(prompt: str):
    stream = ollama.chat.completions.create(
        model="gemma3:latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    result = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            result += delta
            yield result


def stream_llama(prompt: str):
    stream = ollama.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    result = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            result += delta
            yield result


# ─────────────────────────────────────────────
# Gradio entry function
# ─────────────────────────────────────────────

def stream_brochure(company_name, url, model):
    scraped = scrape_site(url)
    selected_links = select_relevant_links(url)
    content_text = format_scraped_content(scraped, selected_links)

    prompt = f"""
You are looking at a company called: {company_name}

Here are the contents of its landing page and other relevant pages.
Create a short brochure in markdown (no code blocks).

{content_text}
"""

    if model == "Gemma3":
        stream = stream_gemma(prompt)
    elif model == "Llama3.2":
        stream = stream_llama(prompt)
    else:
        raise ValueError("Unknown model")

    for chunk in stream:
        yield chunk


# ─────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────

name = gr.Textbox(label="Company Name")
url = gr.Textbox(label="Landing Page URL (https://)")
model_selector = gr.Dropdown(
    choices=["Gemma3", "Llama3.2"],
    value="Gemma3",
    label="Model"
)
output = gr.Markdown(label="Brochure")

view = gr.Interface(
    fn=stream_brochure,
    title="BrochureGPT",
    inputs=[name, url, model_selector],
    outputs=output,
    flagging_mode="never",
)

if __name__ == "__main__":
    view.launch()
