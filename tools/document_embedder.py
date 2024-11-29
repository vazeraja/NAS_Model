import asyncio
import json
import requests
from tempfile import NamedTemporaryFile

from langchain_community.document_loaders import PyPDFLoader
from transformers import GPT2TokenizerFast


async def main():
    pdf_path = "books/Alchian_UniversalEconomics1674.pdf"
    textbook_text = load_textbook(pdf_path)
    chunks = tokenize_and_chunk(textbook_text)
    print(f"Generated {len(chunks)} chunks.")

    for i, chunk in enumerate(chunks[:3]):
        print(f"Chunk {i + 1}:\n{chunk[:500]}...\n")


def load_textbook(pdf_path):
    """
    Load text from a local PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Combined text from the PDF.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    combined_text = " ".join([doc.page_content for doc in documents])
    return combined_text

def tokenize_and_chunk(text, max_tokens=512, overlap=50):
    """
    Tokenize and chunk text into segments of max_tokens with overlap.

    Args:
        text (str): Input text to chunk.
        max_tokens (int): Maximum tokens per chunk.
        overlap (int): Token overlap between chunks.

    Returns:
        list: List of text chunks.
    """
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokens = tokenizer.tokenize(text)
    chunks = []
    current_chunk = []

    for token in tokens:
        current_chunk.append(token)
        if len(current_chunk) >= max_tokens:
            chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
            current_chunk = current_chunk[-overlap:]  # Preserve overlap

    if current_chunk:
        chunks.append(tokenizer.convert_tokens_to_string(current_chunk))

    return chunks



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
