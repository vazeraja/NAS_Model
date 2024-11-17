from bs4 import BeautifulSoup
import requests


class PDFDownloader:

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