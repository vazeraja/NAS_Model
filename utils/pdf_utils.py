import pypandoc
from bs4 import BeautifulSoup
import requests
import os

class PDFUtils:

    @staticmethod
    async def epub_to_pdf(input_epub):
        """
        Converts an EPUB file to a PDF file using Pandoc. The output PDF is saved in the same directory
        as the input EPUB file with the same base name.

        :param input_epub: Path to the input EPUB file.
        """
        try:
            pypandoc.download_pandoc()

            # Get the directory and base filename of the input EPUB file
            base_name = os.path.splitext(os.path.basename(input_epub))[0]  # Remove extension
            directory = os.path.dirname(input_epub)  # Get directory
            output_pdf = os.path.join(directory, f"{base_name}.pdf")  # Construct PDF path

            # Convert EPUB to PDF
            pypandoc.convert_file(input_epub, 'pdf', outputfile=output_pdf, extra_args=['--pdf-engine=xelatex'])
            print(f"Converted {input_epub} → {output_pdf}")
        except Exception as e:
            print(f"Error converting {input_epub} to PDF: {e}")

    @staticmethod
    async def get_pdf_url(url: str):
        # Fetch the webpage content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links in the page
            links = soup.find_all('a', href=True)

            # Search for the link that points to the PDF
            for link in links:
                href = link['href']
                if href.endswith('.pdf'):
                    # Return the full PDF URL
                    if href.startswith('http'):
                        return href  # Direct URL
                    else:
                        return url + href  # Relative URL (adjust as needed)
        else:
            print(f"Error: Unable to fetch the webpage. Status code: {response.status_code} \n"
                  f"Webpage URL: {url}")
            return None
