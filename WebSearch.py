import httpx
from bs4 import BeautifulSoup
import traceback
from urllib.parse import urlparse

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
searchURLs = [
    ("DuckDuckGo", "https://html.duckduckgo.com/html/?q=", ".result__url"),
    ("Brave", "https://search.brave.com/search?q=", ".snippet a"),
    ("Startpage", "https://www.startpage.com/do/search?language=english&cat=web&q=", "h3.clk a"),
    ("Qwant", "https://www.qwant.com/?q=", "[data-testid=webResult] a"),
    ("Bing", "https://www.bing.com/search?q=", "li.b_algo h2 a"),
    # ("Searx", "https://priv.au/search?q=", "&format=json"), # Needs new Instance to stop '429 Too Many Requests' Error
]

async def search(query):
    # print("Searching...")
    urls = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, baseURL, selector in searchURLs:
            try:
                if name != "Searx":
                    response = await client.get(baseURL + query, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    # urls = [a["href"] for a in soup.select(selector)][:5]
                    urls = [a["href"] for a in soup.select(selector)] # pass all URLS | Sort and Filter in cleanup()
                    # if urls:
                    #     print(urls)
                    #     break
                else:
                    response = await client.get(baseURL + query + selector, headers=headers)
                    response.raise_for_status()
                    results = response.json().get("results", [])
                    # urls = [r.get("url") for r in results][:5]  # Fixed: extract 'url' from dicts
                    urls = [r.get("url") for r in results]  # pass all URLS | Sort and Filter in cleanup()
                    # if urls:
                    #     print(urls)
                    #     break
            except Exception as e:  # Broader catch for debugging
                print(f"Request failed for {name}: {e}")
                # traceback.print_exc()
                continue

    # print(f"Found {len(urls)} results.")
    if urls:
        return await cleanup(urls)
    # print("Search Failure")
    return None

async def cleanup(urls):
    content = {}
    urlCount = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in urls:
            if (urlCount >= 5):
                break
            if (urlparse(url).scheme not in ("http", "https")) or (not urlparse(url).netloc):
                continue
            if ("youtube" in url.lower()):
                continue
            try:
                # print(f"Cleaning URL: {url}")
                page = await client.get(url, headers=headers)
                page.raise_for_status()
                soup = BeautifulSoup(page.text, "html.parser")
                # Target main content tags (adjust selectors as needed)
                content_elements = soup.select("article, p, div.content, div[class*='article'], div[class*='post']")
                main_content = " ".join(elem.get_text(strip=True) for elem in content_elements if elem.get_text(strip=True))
                if main_content:
                    # Truncate to ~1000 chars to avoid token overflow
                    truncated = main_content[:1000] + "..." if len(main_content) > 1000 else main_content
                    content[url] = truncated
                    urlCount += 1
                    # print(f"URL: {url}\nContent: {truncated}\n\n")
            except Exception as e:
                print(f"Cleanup failed for {url}: {e}")
                traceback.print_exc()
                continue
    return content if content else None

# async def cleanup(urls):
#     print("Cleaning up...")
#     content = {}
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         for url in urls:
#             try:
#                 page = await client.get(url, headers=headers)
#                 page.raise_for_status()
#                 main_content = trafilatura.extract(page.text)
#                 if main_content:
#                     content[url] = main_content
#                     print(f"URL: {url}\nContent: {main_content}\n\n")
#             except Exception as e:
#                 print(f"Cleanup failed for {url}: {e}")
#                 continue
#     return content if content else None


# import requests
# from bs4 import BeautifulSoup
# import trafilatura
# import LLM
#
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
# searchURLs = [
#     ("DuckDuckGo", "https://duckduckgo.com/html/?q=", ".result__url"),
#     ("Brave", "https://brave.com/search?q=", ".snippet a"),
#     ("Searx", "https://priv.au/search?q=", "&format=json"),
# ]
#
#
# def search(query):
#     global headers, searchURLs
#     urls = []
#     for name, baseURL, selector in searchURLs:
#         try:
#             if (name != "Searx"):
#                 response = requests.get(baseURL + query, headers=headers, timeout=10)
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 urls = [a["href"] for a in soup.select(selector)][:5]
#                 if (urls):
#                     print(urls)
#                     break
#             else:
#                 response = requests.get(baseURL + query + selector, headers=headers, timeout=5)
#                 # response.raise_for_status()
#                 results = response.json().get("results")
#                 urls = results[:5]
#
#         except requests.RequestException:
#             continue
#
#     print("Found " + str(len(urls)) + " results.")
#     if (urls != []):
#         return cleanup(urls)
#     else:
#         print("Search Failure")
#
#
# def cleanup(urls):
#     content = {}
#     for url in urls:
#         try:
#             page = requests.get(url, headers=headers, timeout=5)
#             page.raise_for_status()
#             main_content = trafilatura.extract(page.text)
#             if (main_content):
#                 content[url] = main_content
#                 print("URL:", url)
#                 print("Content:", main_content)
#                 print("\n\n")
#
#         except requests.RequestException:
#             continue
#
#     if (content != {}):
#         # LLM.searchContext = content
#         return content
#     else:
#         return None
