from dotenv import load_dotenv
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import os
import asyncio
import json
import requests

from openai import OpenAI
import anthropic

from config import Config
from utils.dict_utils import DictUtils
from utils.pdf_utils import PDFUtils
from utils.utils import Utils

import mises

load_dotenv()

config = Config()
# client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
client = OpenAI(api_key=config.MD_OPENAI_KEY)

libgen_dir = '/data/library_gift'
mises_org_dir = '/data/mises_org'
test_questions = [
    "What does the book give as the meaning of scarcity",
    "What does the book give as the meaning of opportunity and what example does he give to support his definition?",
    "What is the meaning of 'Political Rent-Seeking'?",
    "What are the alleged exceptions to the 'Law of Demand'?",
    "What is the rule of private property rights",
    "What is the most basic premises of economics?",
    "What does it mean for individuals to be 'purposive actors' who 'economize'?",
    "The economic way of thinking is?"
]


class CoreThemes(Enum):
    METHODOLOGY = "Methodology"
    INSTITUTIONS_AND_INCENTIVES = "Institutions & Incentives"
    ENTREPRENEURSHIP = "Entrepreneurship"
    MARKET_PROCESS = "Market Process"
    ECONOMIC_CALCULATION_PROBLEM = "Economic Calculation Problem"
    KNOWLEDGE_PROBLEM = "Knowledge Problem"
    INDUSTRIAL_ORGANIZATION_MARKET_STRUCTURE = "Industrial Organization/Market Structure"
    CAPITAL_GOODS = "Capital Goods"
    SPATIAL_THEORY = "Spatial Theory"
    TIME_PREFERENCE_INTEREST = "Time Preference/Interest"
    MONETARY_THEORY = "Monetary Theory"
    BUSINESS_CYCLES = "Business Cycles"
    FREE_BANKING = "Free Banking"


@dataclass
class Document:
    document_id: str
    title: str
    author: str
    series: str
    publisher: str
    year: str
    ISBN: str
    file_path: str
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    date_added: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # If no document_id was provided, set a new UUID
        if not self.document_id:
            object.__setattr__(self, 'document_id', str(uuid.uuid4()))


@dataclass
class TextChunk:
    text: str
    source: str
    page_number: int
    theme: Enum = CoreThemes.MARKET_PROCESS  # Optional: Assign a theme if applicable


async def main():
    print("Running Document Embedder")
    # await download_libgen_pdfs()
    # await epub_to_pdf('data/library_gift')

    print('-------------------------------------------')
    pdf_files = await Utils.get_files_with_ext_full_path('data/mises_org', '.pdf')
    print(len(pdf_files))
    for pdf_file in pdf_files[0:2]:
        await parse_pdf_metadata(pdf_file)

    domains = await DictUtils.extract_and_sort_domains_by_frequency()
    for domain, count in domains:
        print(f"{domain}: {count}")
    print('-------------------------------------------')

    # m_links, m_pdfs = await DictUtils.get_pdfs_for_domain('mises.org')
    #     # failed_links = await mises.download_mises_pdfs(m_links)
    #     # print("Done. Failed link count:", len(failed_links))
    #     # print('-------------------------------------------')

    file_count = await Utils.get_file_count_in_directory('data/mises_org')
    print(f"File Count: {file_count}")


async def parse_pdf_metadata(pdf_path) -> Document:
    print(f"Processing PDF: {pdf_path}")
    instructions = """
            You are a PDF metadata extraction assistant. 
            Given the following text from the front matter of a book, 
            please provide the best guesses for:
              - Title
              - Author(s)
              - Series
              - Publisher
              - Year of Publication
              - ISBN

            Return your answer as valid JSON *only*, with the following keys exactly:
            {
              "title": "...",
              "authors": "...",   // or an array if multiple authors
              "series": "...",
              "publisher": "...",
              "year": "...",
              "isbn": "..."
            } 

            Do not include any extra text, explanation, or fields.
            If a field is not found, put "Unknown" in its place.
        """

    front_text = await get_front_matter_text(pdf_path, 5)
    response = await query_openai(instructions, front_text)

    try:
        metadata = json.loads(response)
    except json.JSONDecodeError:
        # If the LLM doesn’t strictly follow instructions and sends invalid JSON,
        # you could handle it here, or fall back to some default metadata.
        print(f"Invalid JSON from LLM: {response}")
        metadata = {
            "title": os.path.basename(pdf_path),
            "authors": "Unknown",
            "series": "Unknown",
            "publisher": "",
            "year": "",
            "isbn": ""
        }

    print(metadata)  # Debugging to see the raw metadata
    print('-------------------------------------------------------------')

    document = Document(
        document_id="",  # auto-generated in __post_init__
        title=metadata.get("title") or os.path.basename(pdf_path),
        author=metadata.get("authors", "Unknown"),  # Or handle lists, etc.
        series="",
        publisher=metadata.get("publisher", ""),
        year=metadata.get("year", ""),
        ISBN=metadata.get("isbn", ""),
        file_path=pdf_path
    )
    return document


# async def query_anthropic(query):
#     client = anthropic.Anthropic(
#         # defaults to os.environ.get("ANTHROPIC_API_KEY")
#         api_key="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",
#     )
#     message = client.messages.create(
#         model="claude-3-5-haiku-20241022",
#         max_tokens=1024,
#         messages=[
#             {"role": "user", "content": query}
#         ]
#     )
#     return message.content[0].text

async def query_openai(instructions, query):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": query}
        ],
        temperature=0.7
    )
    return completion.choices[0].message.content


async def get_front_matter_text(pdf_path: str, page_count=5) -> str:
    from pdf2image import convert_from_path
    import pytesseract
    import pdfplumber
    import pymupdf  # PyMuPDF

    text = []

    try:
        # Attempt extraction using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i in range(min(page_count, len(pdf.pages))):
                page = pdf.pages[i]
                page_text = page.extract_text()

                # If text extraction via pdfplumber fails, skip to the next method
                if not page_text.strip():
                    print(f"pdfplumber failed for page {i + 1}, trying other methods.")
                else:
                    text.append(page_text)
                    continue  # Skip to the next page if extraction is successful

    except Exception as e:
        print(f"Error extracting text with pdfplumber from PDF {pdf_path}: {e}")

    # Fallback: Attempt extraction using PyMuPDF (fitz)
    try:
        if len(text) < page_count:  # Only try fitz if pdfplumber failed
            doc = pymupdf.open(pdf_path)
            for i in range(min(page_count, len(doc))):
                page = doc[i]
                page_text = page.get_text("text")

                # If PyMuPDF fails, skip to the next method
                if not page_text.strip():
                    print(f"PyMuPDF failed for page {i + 1}, trying OCR.")
                else:
                    text.append(page_text)
                    continue  # Skip to the next page if extraction is successful
    except Exception as e:
        print(f"Error extracting text with PyMuPDF from PDF {pdf_path}: {e}")

    # Fallback: Attempt OCR using Tesseract
    try:
        if len(text) < page_count:  # Only try OCR for the remaining pages
            images = convert_from_path(pdf_path, first_page=1, last_page=page_count)
            for i, image in enumerate(images):
                print(f"Running OCR for page {i + 1}.")
                page_text = pytesseract.image_to_string(image)
                text.append(page_text or "")
    except Exception as e:
        print(f"Error extracting text with OCR from PDF {pdf_path}: {e}")

    return "\n".join(text)


async def epub_to_pdf(path, ext='.epub'):
    epub_files = await Utils.get_files_with_ext(path, ext)
    for file in epub_files:
        epub_file_path = path + file
        await PDFUtils.epub_to_pdf(epub_file_path)


async def download_libgen_pdfs(download_folder='data/library_gift/pdfs',
                               failed_json='data/library_gift/_failed_links.json'):
    """
    Downloads PDFs from library.lol links and saves them locally.

    1. Prints the file index (e.g. 1/50, 2/50, ...).
    2. If a link fails to download, it is added to a 'failed_links' list.
    3. At the end, all failed links are saved into a JSON file for inspection.

    :param download_folder: The folder where you want to save downloaded PDFs
    :param failed_json: The path of the JSON file to save the failed links
    """
    os.makedirs(download_folder, exist_ok=True)

    links, pdfs = await DictUtils.get_pdfs_for_domain("library.lol")

    failed_links = []  # For collecting links that fail
    total_links = len(links)

    for i, url in enumerate(links, start=1):
        print(f"[{i}/{total_links}] Processing: {url}")

        # Ensure it’s truly a library.lol link
        if "library.gift" not in url:
            print(f"  [!] Skipping non-library.gift link: {url}")
            failed_links.append(url)
            continue

        try:
            # 1) Request the library.lol page
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()

            # 2) Parse the HTML
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 3) Look for the <a> tag whose text is exactly 'GET'
            get_link = soup.find('a', string='GET')
            if not get_link:
                print(f"  [!] 'GET' link not found on page. Skipping.")
                failed_links.append(url)
                continue

            download_url = get_link.get('href')
            if not download_url.startswith('http'):
                print(f"  [!] Unexpected download URL: {download_url}. Skipping.")
                failed_links.append(url)
                continue

            # 4) Download the PDF
            pdf_resp = requests.get(download_url, timeout=60)
            pdf_resp.raise_for_status()

            # Option A: Use the filename from the URL path
            parsed_download_url = urlparse(download_url)
            filename = os.path.basename(parsed_download_url.path)
            filename = unquote(filename)  # Convert "%20" to spaces, etc.

            output_path = os.path.join(download_folder, filename)

            # 5) Save locally
            with open(output_path, 'wb') as f:
                f.write(pdf_resp.content)

            print(f"  [✔] Downloaded: {output_path}")

        except Exception as e:
            print(f"  [!] Failed to process {url}. Error: {e}")
            failed_links.append(url)

    # Write out failed links to a JSON file
    if failed_links:
        print(f"\n[!] Writing {len(failed_links)} failed links to '{failed_json}'...")
        with open(failed_json, 'w', encoding='utf-8') as f_json:
            # noinspection PyTypeChecker
            json.dump(failed_links, f_json, indent=2, ensure_ascii=False)
    else:
        print("\nNo failures to report.")

    return failed_links


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
