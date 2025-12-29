# BrochureGPT

BrochureGPT is an AI-powered application that automatically generates professional, sales-ready company brochures from a company name and website.  
It combines **web scraping**, **LLM-driven decision making**, and **structured content generation** to simulate a real-world GenAI business product.

This project was built as **Week 1’s capstone project** in an AI Engineer course and represents my first end-to-end Generative AI system.

---

## What This Project Does

Given a company website, BrochureGPT:

1. Scrapes the website intelligently (handling both static and JS-rendered pages)
2. Identifies **relevant business pages** (About, Careers, Mission, Products, etc.)
3. Filters out irrelevant links (privacy policies, legal pages, footers)
4. Uses a local Large Language Model to:
   - Understand company context
   - Make decisions on what content matters
   - Generate a **well-structured marketing brochure**
5. Outputs clean, formatted content suitable for:
   - Sales outreach
   - Investor decks
   - Recruiting pages

---

## Models & Tech Stack

- **LLM**: `gemma3:latest` (running locally)
- **Model Runtime**: Ollama-compatible OpenAI interface
- **Languages**: Python
- **Web Scraping**:
  - `requests`
  - `BeautifulSoup`
  - `Playwright` (for JavaScript-heavy sites)
- **Environment Management**: `python-dotenv`
- **Interface**: Jupyter Notebook

This project runs **entirely locally**, demonstrating how modern GenAI products can be built without relying on paid cloud APIs.

---

## What I Learned (Week 1)

**Week 1: Foundations and First Projects**

During this week, I:

- Learned the **fundamentals of Transformers**
- Experimented with **six frontier LLMs**
- Built my **first real GenAI business product**
- Learned how to:
  - Structure system and user prompts
  - Use LLMs for decision-making, not just text generation
  - Chain tools together (scraper → model → formatter)
  - Design outputs for real business use cases

BrochureGPT is the practical outcome of these learnings.

---

## Project Structure
```graphql
BrochureGPT/
│
├── BrochureGPT/
│ └── brochureGpt.ipynb # Main notebook (LLM logic + brochure generation)
│
├── WebScrapper/
│ ├── scrape_site.py # Intelligent website crawler
│ └── init.py
│
├── README.md
└── .gitignore
```

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/DhRuva-1509/BrochureGPT.git
cd BrochureGPT
```

### 2. Install dependencies
```bash
pip install requests beautifulsoup4 playwright python-dotenv openai
playwright install
```

### 3. Run Gemma locally
Ensure you have Gemma 3 running locally (example with Ollama):

```bash
ollama run gemma3:latest
```

### 4. Environment variables
Create a .env file
```
GEMMA_API_KEY=your_local_key
GEMMA_BASE_URL=http://localhost:11434/v1
```

## How to Use
1. Open the notebook:
```
jupyter notebook BrochureGPT/brochureGpt.ipynb
```
2. Enter a company website URL
3. Run the cells step-by-step
4. Receive a structured, AI-generated brochure

## Why This Project Matters
This project demonstrates:
* Practical LLM usage beyond chatbots
* Real-world AI system design
* Tool-augmented reasoning
* Prompt engineering for structured outputs
* Local-first AI deployment
* It reflects how modern AI engineers build products, not just demos.

## Future Improvements (Planned)
To further evolve BrochureGPT, I plan to add:
* PDF & HTML brochure export
* Multi-language brochure generation
* Brand-tone customization
* UI using Streamlit or FastAPI
* Caching & performance optimizations
* RAG-based brochure generation
* Model comparison benchmarks
* Automated tests and CI pipeline

## Author
Dhruva Patil

AI Engineer in Training,
Focused on building production-ready Generative AI system
