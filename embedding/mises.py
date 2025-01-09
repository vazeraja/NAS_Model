import os
import json
import asyncio
import requests
import hashlib
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from collections import defaultdict

async def download_mises_pdfs(links,
                              download_folder='data/mises_org',
                              failed_json='data/mises_org/failed_links.json',
                              map_json='data/mises_org/final_pdf_map.json'):
    """
    Attempts to download PDFs from a list of Mises.org links.
    Logs a mapping from original link -> final PDF link so we can see duplicates.
    """

    os.makedirs(download_folder, exist_ok=True)
    failed_links = []

    # 1) Dictionary to track { original_link : final_pdf_url_found }
    final_pdf_map = {}

    total_links = len(links)
    for i, url in enumerate(links, start=1):
        print(f"[{i}/{total_links}] Processing: {url}")

        pdf_downloaded = False
        final_pdf_link = None

        try:
            # Parse the main page
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Attempt to find PDF on main page
            pdf_downloaded, final_pdf_link = download_first_pdf_on_page(
                soup=soup,
                base_url=url,
                download_folder=download_folder
            )

            # If not found, check sublinks
            # if not pdf_downloaded:
            #     sublinks = extract_same_domain_sublinks(soup, base_url=url)
            #     for sublink in sublinks:
            #         try:
            #             sub_resp = requests.get(sublink, timeout=10)
            #             sub_resp.raise_for_status()
            #             sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
            #
            #             pdf_downloaded, final_pdf_link = download_first_pdf_on_page(
            #                 soup=sub_soup,
            #                 base_url=url,  # still the original link for naming
            #                 download_folder=download_folder
            #             )
            #             if pdf_downloaded:
            #                 break
            #         except Exception as e:
            #             print(f"  [!] Could not parse sublink {sublink}. Error: {e}")

            # Record success/failure
            if pdf_downloaded:
                print(f"  [✔] PDF found and downloaded for: {url}")
                # Save the final PDF link in our map
                if final_pdf_link:
                    final_pdf_map[url] = final_pdf_link
            else:
                print(f"  [✘] No PDF found for: {url}")
                failed_links.append(url)

        except Exception as e:
            print(f"  [!] Failed to process {url}. Error: {e}")
            failed_links.append(url)

    # Save failed links if any
    if failed_links:
        print(f"\n[!] Writing {len(failed_links)} failed links to '{failed_json}'...")
        os.makedirs(os.path.dirname(failed_json), exist_ok=True)
        with open(failed_json, 'w', encoding='utf-8') as f_json:
            json.dump(failed_links, f_json, indent=2, ensure_ascii=False)
    else:
        print("\nNo failures to report.")

    # 2) Write out the map of original_link -> final_pdf_link
    print(f"\nSaving final PDF link mapping to '{map_json}'...")
    os.makedirs(os.path.dirname(map_json), exist_ok=True)
    with open(map_json, 'w', encoding='utf-8') as mp_json:
        json.dump(final_pdf_map, mp_json, indent=2, ensure_ascii=False)

    # 3) Identify duplicates in final_pdf_map
    # identify_pdf_duplicates(final_pdf_map)

    return failed_links

def download_first_pdf_on_page(soup: BeautifulSoup, base_url: str, download_folder: str):
    """
    Returns (pdf_downloaded: bool, final_pdf_url: str or None).

    pdf_downloaded = True/False
    final_pdf_url = the PDF link that was actually fetched (or None if not found).
    """
    pdf_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().endswith(".pdf"):
            pdf_links.append(urljoin(base_url, href))
            break

    if len(pdf_links) > 0:
        pdf_link = pdf_links[0]
        try:
            pdf_resp = requests.get(pdf_link, timeout=15)
            pdf_resp.raise_for_status()
            save_pdf_unique_by_page(pdf_resp, original_page_url=base_url, pdf_url=pdf_link, download_folder=download_folder)
            return True, pdf_link
        except Exception as e:
            print(f"  [!] Error downloading PDF {pdf_link}: {e}")
            return False, None
    else:
        return False, None


def save_pdf_unique_by_page(pdf_resp: requests.Response, original_page_url: str, pdf_url: str, download_folder: str):
    # Exactly as before: ensure each original link produces a unique file
    page_hash = hashlib.md5(original_page_url.encode('utf-8')).hexdigest()[:8]
    base_name = os.path.basename(urlparse(pdf_url).path)
    base_name = unquote(base_name)

    unique_filename = f"{page_hash}_{base_name}"
    output_path = os.path.join(download_folder, unique_filename)
    with open(output_path, "wb") as f:
        f.write(pdf_resp.content)

def extract_same_domain_sublinks(soup: BeautifulSoup, base_url: str) -> list:
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    sublinks = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        if parsed_url.netloc == base_domain:
            sublinks.append(full_url)

    return list(set(sublinks))

def identify_pdf_duplicates(final_pdf_map: dict):
    """
    final_pdf_map: { original_link: final_pdf_url }

    Finds all final PDF URLs that appear multiple times (=> multiple original links
    pointing to the same PDF). Prints a summary of duplicates.
    """
    from collections import defaultdict
    pdf_groups = defaultdict(list)

    # Group original links by their final PDF URL
    for orig_link, final_link in final_pdf_map.items():
        pdf_groups[final_link].append(orig_link)

    # Now print any groups with more than one link
    duplicates_found = False
    print("\nDuplicate final PDFs (multiple original links => same PDF link):")
    for final_link, orig_links in pdf_groups.items():
        if len(orig_links) > 1:
            duplicates_found = True
            print(f"\nFinal PDF: {final_link}")
            for link in orig_links:
                print(f"  - {link}")

    if not duplicates_found:
        print("No duplicates. Every final PDF URL is unique.")
