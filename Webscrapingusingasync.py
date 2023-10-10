import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup
import time
'''hello'''
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Referer': 'https://www.example.com/',
#     'Upgrade-Insecure-Requests': '1',
#     'Cache-Control': 'max-age=0',
# }

async def isObjectEmpty(productdetailname):
    if productdetailname:
        return productdetailname.text
    else:
        return None

async def scrapProductDetails(session, url, listOfDict):
    dict1 = {}
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        fullcontainer = soup.find(class_="a-container")
        title = fullcontainer.find(id="productTitle")

        if title:
            imagecontainer = fullcontainer.find(id="imgTagWrapperId")
            images = imagecontainer.find_all("img")
            image = images[0]['src']
            price = fullcontainer.find(class_="a-price-whole")
            price = await isObjectEmpty(price)
            
            mrp = fullcontainer.find(class_="a-price a-text-price")
            mrp1 = await isObjectEmpty(mrp)
            finalmrp = None
            if mrp1:
                finalmrp = mrp.find(class_="a-offscreen")
                finalmrp = await isObjectEmpty(finalmrp)
            print(finalmrp)
            ratingcontainer = fullcontainer.find(id="averageCustomerReviews")
            ratingcontainer1 = await isObjectEmpty(ratingcontainer)
            rating = None
            if ratingcontainer1:
                rating = ratingcontainer.find(class_='a-size-base a-color-base')
                rating = await isObjectEmpty(rating)

            listofdes = fullcontainer.find(class_="a-unordered-list a-vertical a-spacing-mini")
            listofdes = await isObjectEmpty(listofdes)
            dict1["PRODUCT TITLE"] = title.text
            dict1["Images"] = image
            dict1["MRP"] = finalmrp
            dict1["PRICE"] = price
            dict1["RATING"] = rating
            dict1["DESCRIPTION"] = listofdes
    return dict1

async def writeInFile(listOfDict):
    fieldnames = listOfDict[0].keys()
    async with open("C:\\Users\\DELL\\OneDrive\\Desktop\\begineerpython\\pythonbeginner\\webscrap7.csv", mode="a", encoding="utf-8") as file:
        productfile = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            productfile.writeheader()
        for item in listOfDict:
            await productfile.writerow(item)
    return f"Wrote results for 20 products in file"

async def getAllPagesHref(keyword, no_of_pages, session):
    listOfEveryPageUrls = []
    url = f"https://www.amazon.in/s?k={keyword}&page=1"
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup1 = BeautifulSoup(html, "html.parser")
        hrefsclass = soup1.find_all(class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
        if hrefsclass:
            maxPages = int(soup1.find(class_="s-pagination-item s-pagination-disabled").text)
            print(maxPages)
            if no_of_pages is None:
                no_of_pages = maxPages
            elif 1 <= no_of_pages <= maxPages:
                pass
            else:
                return f"Number of pages entered are invalid"

            for i in range(1, no_of_pages + 1):
                url = f"https://www.amazon.in/s?k={keyword}&page={i}"
                listOfEveryPageUrls.append(url)
            result = await fetchEveryPageProductHref(listOfEveryPageUrls, session)
            return result
        else:
            return f"No results for {keyword} try checking your spelling or use more general terms"

async def fetchEveryPageProductHref(listOfEveryPageUrls, session):
    listOfProductLinks = []
    index = 0
    for i in range(0, len(listOfEveryPageUrls)):
        print(f"Page no {i} is started scrapping")
        onePageUrl = listOfEveryPageUrls[i]
        async with session.get(onePageUrl, headers=headers) as response:
            html = await response.text()
            soup1 = BeautifulSoup(html, "html.parser")
            hrefsclasses = soup1.find_all(
                class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
            for hrefclass in hrefsclasses:
                link = hrefclass.get("href")
                prefix = "https://www.amazon.in"
                url = f"{prefix}{link}"
                listOfProductLinks.append(url)
                if len(listOfProductLinks) >= index + 20:
                    result_for_20_multiprocess_product = await doAsyncProcessing(listOfProductLinks[index:index + 20])
                    print(result_for_20_multiprocess_product)
                    index = index + 20
    return f"Scrapped the details of {len(listOfProductLinks)} products"

async def doAsyncProcessing(listOfProductLinks):
    tasks = []
    listOfDict=[]
    async with aiohttp.ClientSession() as session:
        for url in listOfProductLinks:
            task = asyncio.create_task(scrapProductDetails(session, url, listOfDict))
            tasks.append(task)
    listOfDict= await asyncio.gather(*tasks)
    print(listOfDict)
    result= await writeInFile(listOfDict)
    print(result)
    listOfDict[:] = []
    return f"Async processed completed for 20 products"

async def enterKeyword():
    keyword = input("SEARCH HERE----------> ")
    no_of_pages = int(input("ENTER NO. OF PAGES TO SCRAP----------> "))
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        result = await getAllPagesHref(keyword, no_of_pages, session)
        print(result)
    elapsed = time.perf_counter() - start
    return f"{elapsed} sec spent on scrapping the result"

if __name__ == "_main_":
    result=asyncio.run(enterKeyword())
    print(result)