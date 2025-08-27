import scrapy
import json
from alcoteka.parsers.product_parser import ProductParser
from alcoteka.items import ProductItem


class AlcotekaSpider(scrapy.Spider):
    name = 'alkoteka_spider'
    allowed_domains = ['alkoteka.com']

    def start_requests(self):
        with open('spr/spr_categories_url.json', encoding='utf-8') as f:
            categories = json.load(f)
        with open('spr/spr_cities.json', encoding='utf-8') as f:
            cities = json.load(f)

        for city in cities:
            for category in categories:
                yield scrapy.Request(
                    self.build_api_url_category(category['url'], city['uuid'], page=1),
                    callback=self.parse_category,
                    meta={'category': category, 'city': city, 'page': 1}
                )

    def build_api_url_category(self, category_url: str, city_uuid: str, page: int = 1) -> str:
        slug = category_url.rstrip('/').split('/')[-1]
        return f'https://alkoteka.com/web-api/v1/product?city_uuid={city_uuid}&page={page}&per_page=20&root_category_slug={slug}'

    def build_api_url_product(self, product_slug: str, city_uuid: str) -> str:
        return f'https://alkoteka.com/web-api/v1/product/{product_slug}?city_uuid={city_uuid}'

    def parse_category(self, response):
        data = json.loads(response.text)
        products = data.get("results", [])
        meta = data.get("meta", {})

        for product in products:
            slug = product.get('slug')
            if slug:
                yield scrapy.Request(
                    self.build_api_url_product(slug, response.meta['city']['uuid']),
                    callback=self.parse_product,
                    meta={
                        'category': response.meta['category'],
                        'city': response.meta['city'],
                        'slug': slug}
                )

        if meta.get("has_more_pages"):
            next_page = meta.get("current_page", 1) + 1
            next_url = self.build_api_url_category(
                response.meta['category']['url'],
                response.meta['city']['uuid'],
                page=next_page
            )
            yield scrapy.Request(
                next_url,
                callback=self.parse_category,
                meta={'category': response.meta['category'],
                      'city': response.meta['city'],
                      'page': next_page}
            )

    def parse_product(self, response):
        slug = response.meta['slug']
        data = json.loads(response.text)
        product_data = data.get("results", {})

        parser = ProductParser(product_data)
        parsed_data = parser.to_dict(slug)

        item = ProductItem(**parsed_data)
        item["city"] = response.meta['city']['name']
        item["city_uuid"] = response.meta['city']['uuid']
        item["category"] = response.meta['category']['name']

        yield item
