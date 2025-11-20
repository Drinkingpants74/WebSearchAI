import httpx
from bs4 import BeautifulSoup
import traceback
from urllib.parse import urlparse
from readability import Document

bannedURLs = ["youtube", "duckduckgo", "google", "bing"]
usedURLs = []
idToURL = {}
previousInfo = {}
# {
#   "ID": int
#   "CHUNK": str
# }

chunkID = 0

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
                    if urls:
                    #     print(urls)
                        break
                else:
                    response = await client.get(baseURL + query + selector, headers=headers)
                    response.raise_for_status()
                    results = response.json().get("results", [])
                    # urls = [r.get("url") for r in results][:5]  # Fixed: extract 'url' from dicts
                    urls = [r.get("url") for r in results]  # pass all URLS | Sort and Filter in cleanup()
                    if urls:
                    #     print(urls)
                        break
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
    global previousInfo, usedURLs, chunkID, bannedURLs, idToURL
    content = []
    urlCount = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in urls:
            if (urlCount >= 5):
                break
            if (url in usedURLs):
                continue
            banned = False
            for i in bannedURLs:
                if (str(i) in url.lower()):
                    banned = True
                    break
            if (banned):
                continue
            if (urlparse(url).scheme not in ("http", "https")) or (not urlparse(url).netloc):
                continue
            try:
                # print(f"Cleaning URL: {url}")
                page = await client.get(url, headers=headers)
                # Block Redirects and Trackers
                if (page.status_code in (301, 302, 303, 307, 308)):
                    continue
                page.raise_for_status()
                html = page.text
                # html = BeautifulSoup(page.text, "html.parser")
                doc = Document(html)
                cleanHTML = doc.summary()
                soup = BeautifulSoup(cleanHTML, "lxml")
                main_content = soup.get_text(strip=True)
                main_content_split = main_content.split("\n")
                for chunk in main_content_split:
                    if (chunk.strip() != ""):
                        content.append({"ID": chunkID, "CHUNK": chunk})
                        # previousInfo.append({"ID": chunkID, "CHUNK": chunk})
                        previousInfo[chunkID] = chunk
                        urlCount += 1
                        usedURLs.append(url)
                        idToURL[chunkID] = url
                        chunkID += 1

                # Target main content tags (adjust selectors as needed)
                # content_elements = html.select("article, p, div.content, div[class*='article'], div[class*='post']")
                # main_content = " ".join(elem.get_text(strip=True) for elem in content_elements if elem.get_text(strip=True))
                # if main_content:
                    # Truncate to ~1000 chars to avoid token overflow
                    # truncated = main_content[:1000] + "..." if len(main_content) > 1000 else main_content
                    # truncated = LLM.summarize_article(main_content) if main_content_size > 250 else main_content
                    # content[url] = main_content
                    # urlCount += 1
                    # usedURLs.append(url)
                    # previousInfo[url] = main_content
                    # previousInfo.append({url: truncated})
                    # previousInfo += f"\nSource: {url}\n{truncated}"
                    # print(f"URL: {url}\nContent: {truncated}\n\n")
            except Exception as e:
                print(f"Cleanup failed for {url}: {e}")
                traceback.print_exc()
                continue
    return content if content else None
