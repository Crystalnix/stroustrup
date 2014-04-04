# -*- coding: utf-8 -*-
author = 'Roman Usynin'
email = 'r.usynin@crystalnix.com'
copyright = 'Copyright 2014, Crystalnix'

from urllib2 import urlopen
from amazon.api import AmazonAPI, AsinNotFound
from re import search
from bs4 import BeautifulSoup
from django.conf import settings
from urlparse import urlparse


class BaseParser(object):
    def parse(self, urlopen_object):
        raise NotImplementedError()


class AmazonParser(BaseParser):
    def parse(self, urlopen_object):
        product_url = search('http://www.amazon.com/([\\w-]+/)?(dp|gp/product)/(\\w+/)?(\\w{10})', urlopen_object.url)
        if product_url is not None:
                id_product = product_url.group(4)
                amazon = AmazonAPI(settings.AMAZON_ACCESS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_ASSOC_TAG)
                product = amazon.lookup(ItemId=id_product)
                title = product.title
                authors = u", ".join(unicode(v) for v in product.authors)
                price = '{0} {1}'.format(product.price_and_currency[0], product.price_and_currency[1])
                description = product.editorial_review
                if product.medium_image_url is None:
                    book_image_url = ''
                else:
                    book_image_url = product.medium_image_url
                return {'title': title,
                        'authors': authors,
                        'price': price,
                        'description': description,
                        'book_image_url': book_image_url}

        else:
            return None


class OzonParser(BaseParser):
    def parse(self, urlopen_object):
        try:
            soup = BeautifulSoup(urlopen_object.read().replace('\n', '').decode('windows-1251'))
            title = soup.find("h1").text
            authors = soup.find("p", itemprop="author").text.split(':')[1]
            book_image_url = soup.find("img", attrs={'class': "eMicroGallery_fullImage"}).attrs['src']
            price = soup.find("span", attrs={'itemprop': 'price', 'class': 'hidden'}).text
            description = soup.find("div", id="detail_description").text.replace(u"Сообщить о неточности в описании",'')
            return {'title': title,
                    'authors': authors,
                    'price': price,
                    'description': description,
                    'book_image_url': book_image_url}
        except:
            return None


#factory pattern
def book_shop_factory(url):
    name_shop = urlparse(url)[1].split('.')[1]
    shops = {
        'amazon': AmazonParser,
        'ozon': OzonParser,
    }
    if name_shop in shops:
        return shops[name_shop]()
    else:
        return None