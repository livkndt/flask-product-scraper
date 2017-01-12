# imports
import urllib2
from bs4 import BeautifulSoup, Comment
import json
import copy
import re

def categories (url):
    """
    Scrape the categories from the navigation HTML (top 2 levels of nav only)
    url - the root URL to scrape
    """
    # do scrape & parse
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    # remove noise (extra script tags, comments)
    [s.extract() for s in soup.findAll('script')]
    for comm in soup(text=lambda text:
        isinstance(text, Comment)):
            comm.extract()

    # get the UL top-level category menu
    menu = soup.findAll('li', class_="topLevelMenu")

    # loop over the list elements in top-level menu
    categories = []
    x = 1
    for row in menu:
        # get top-level category
        link = row.find('a')
        cat = {
            "parentCatId":  0,
            "catId":        x,
            "catTitle":     link.contents[0],
            "catUrl":       link["href"],
            "subcat":       []
        }
        parentId = x        # store ID of top-level cat to link to subcats
        x += 1

        # get subcategories (second level)
        submenu = row.findAll('li')
        subcategories = []
        for sub_row in submenu:
            # get sub-level categories
            sublink = sub_row.find('a')
            if sublink != None:
                subcat = {
                    "parentCatId":  parentId,
                    "catId":        x,
                    "catTitle":     sublink.contents[0],
                    "catUrl":       sublink["href"]
                }
                x += 1
                # build list of subcategory 'objects'
                subcategories.append(subcat)

            # add subcats to cat
            cat['subcat'] = subcategories

        # build list of category 'objects'
        if cat["catTitle"] != 'BLOG':
            categories.append(cat)

    # flatten categories for save to DB
    save_categories = []
    categories_clone = copy.deepcopy(categories)
    for top_level in categories_clone:
        for sub_level in top_level["subcat"]:
            save_categories.append(sub_level)
        # remove the subcat array
        del top_level["subcat"]
        save_categories.append(top_level)

    # save categories to file
    print "WRITE saving categories to database/category.json"
    with open('database/category.json', 'w') as fp:
        json.dump(save_categories, fp)

    # systematically crawl over all the URLs in the category list
    crawl (categories)

def crawl (categories):
    """
    Crawl over an entire site using the category navigation
    categories - array of dictionaries, containing URLS to scrape
    """
    # loop through category pages and scrape products
    # produce one array of all products
    products = []
    for top_level in categories:
        # scrape the top level URL
        products = products + get_pages(top_level['catId'], top_level['catUrl'])
        for sub_level in top_level['subcat']:
            # scrape the subcategory URLs
            products = products + get_pages(sub_level['catId'], sub_level['catUrl'])

    # save products to file
    print "WRITE saving products to database/product.json"
    with open('database/product.json', 'w') as fp:
        json.dump(products, fp)

    print "END scraping products complete"

def get_pages (catId, url):
    """
    Gets pagination URLs
    catId - category ID to link product to category
    url   - url of page to generate URLs for
    """
    # do scrape & parse
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    # store products
    products = []

    # manage pagination
    paging = soup.find('select', id="grid-paging-header")
    if paging != None:
        opt = paging.find_all('option')[-1].get_text()  # get last option element
        match = re.search('\(\d+\)', opt)               # format: "View all (%d)"
        if match == None:
            # 60 products; append 60 to URL + more pages to grab
            url = url + "?srule=best-matches&sz=60"
            # redo scrape & parse
            html = urllib2.urlopen(url)
            soup = BeautifulSoup(html, "html.parser")
            # get bottom pagination
            page_links = soup.find('div', class_="pagination")
            if page_links != None:
                last_link = page_links.find_all('li', attrs={'class': None})[-1].get_text()
                for x in xrange(1, int(last_link)+1):
                    new_url = ''
                    if x > 1:
                        suffix = "&start=%d" % (60 * (x - 1))
                        new_url = url + suffix
                    else:
                        new_url = url
                    # scrape the new URL
                    products = products + scrape_products(catId, new_url)
                # end for
             # end if
        else:
            # Viewing all: no more pages to grab, append limit to URL
            limit = match.group(0)[1:-1]
            url = url + "?srule=best-matches&sz=%s" % limit
        # end if
    # end if
    products = products + scrape_products(catId, url)

    # return sub list
    return products

def scrape_products (catId, url):
    """
    Extract product data from webpage
    catId - category ID to link product to category
    url   - url of page to scrape
    """
    # finally! scrape the actual products from the page
    print "READ scraping the URL: %s (catId: %s)" % (url, catId)
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    # remove script tags
    [s.extract() for s in soup.findAll('script')]

    # get all product tiles
    product_listing = soup.findAll('div', class_="product producttile small")

    # loop over product tiles, store relevant info to dict & store in array
    products = []
    for row in product_listing:
        productId = row.find('meta', itemprop="productID")
        url = row.find('meta', itemprop="url")
        img = row.find('img', itemprop="image")
        name = row.find('div', itemprop="name").find('a')
        price = row.find('div', class_="salesprice").get_text()
        prod = {
            "prodCode":     productId["content"],
            "prodUrl":      url["content"],
            "prodImg":      img["src"],
            "prodName":     name["title"],
            "prodPrice":    price,
            "catId":        catId
        }
        products.append(prod)

    # return list of products on page
    return products

if __name__ == "__main__":
    # ROOT Web URL to scrape
    webpage = "http://www.farah.co.uk"
    print "BEGIN scraping categories and products from: %s" % webpage
    # First, scrape the categories
    categories (webpage)
