import os
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from ..items import UnsplItem
from itemloaders.processors import MapCompose


class UnsplashSpider(scrapy.Spider):
    name = "unsplash"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com/"]

    def parse(self, response):
        # Проходимся по списку изображений
        for image in response.xpath('//div[@class="d95fI"]/figure//div/a[@class="Prxeh"]/@href').extract():
            # Соединяем ссылку на полное отдельное  изображение
            yield scrapy.Request(response.urljoin(image), self.parse_image)

    # Поиск и парсинг размеров изображений
    def parse_image(self, response):
        # Получаем все значения srcset для изображений
        srcset_values = response.xpath('//div/button//div/img[@class="ApbSI z1piP vkrMA"]/@srcset').extract_first()
        # Разделяем значения srcset и преобразуем их в список словарей с URL и размером
        images = [{'url': src.split(' ')[0], 'size': int(src.split(' ')[1].replace('w', ''))}
                  for src in srcset_values.split(', ')]

        # Находим превью изображение
        pref_size_image = min(images, key=lambda x: x['size'])
        if pref_size_image:
            yield scrapy.Request(response.urljoin(pref_size_image['url']), self.save_preview_image)

        # Находим полное изображение
        full_size_image = max(images, key=lambda x: x['size'])
        if full_size_image:
            yield scrapy.Request(response.urljoin(full_size_image['url']), self.save_full_image)

        # Сбор данных в элементы
        loader = ItemLoader(item=UnsplItem(), response=response)
        loader.default_input_processor = MapCompose(str.strip)

        # Парсим имя картинки
        loader.add_xpath('name_image', '//div[@class="VgSmN"]//div/h1/text()')

        # Парсим категорию картинки
        categori_selectors = response.xpath('//div[@class="rx3zu _UNLg"]//div[@class="uK_kT"]/div//span/a/text()')
        categori = [s.get().strip() for s in categori_selectors if s.get().strip()]
        if categori:
            loader.add_value('featured_in', categori)

        # Парсим адрес картинки
        loader.add_value('image_urls', pref_size_image['url'])

        yield loader.load_item()

    # Префикс превью изображений
    def save_preview_image(self, response):
        self.save_image(response, 'preview_')

    # Префикс полноразмерных изображений
    def save_full_image(self, response):
        self.save_image(response, 'full_')

    # Сохранение изображений
    def save_image(self, response, prefix):
        # Удаляем лишние из URL
        url_file_name = os.path.basename(response.url.split('?')[0])
        # Вручную добавляем расширение файлам
        if not any(url_file_name.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
            url_file_name += '.jpg'
        # Добавляем префикс к имени файла
        file_name = f'{prefix}{url_file_name}'
        # Сохраняем файл
        with open(f'images/{file_name}', 'wb') as f:
            f.write(response.body)

class UnsplashItemSpider(CrawlSpider):
    name = "unsplash_rule"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com/"]

    rules = (Rule(LinkExtractor(restrict_xpaths='//div[@class="NHQ0m"]/div[@class="d95fI"]'), callback="parse_item",
                  follow=True),
             Rule(LinkExtractor(restrict_xpaths='//*[@class="oaSYM ZR5jm"]/@href'))
             )

    def parse_item(self, response):
        for category in response.xpath(
                '//div[@class="NHQ0m"]/div[@class="d95fI"]/figure//div/a[@class="Prxeh"]/@href').extract():
            yield scrapy.Request(response.urljoin(category), callback=self.parse_category)

        loader = ItemLoader(item=UnsplItem(), response=response)
        loader.default_input_processor = MapCompose(str.strip)

        loader.add_xpath('name_image', '//div[@class="VgSmN"]//div/h1/text()')

        categori_selectors = response.xpath('//div[@class="rx3zu _UNLg"]//div[@class="uK_kT"]/div//span/a/text()')
        categori = [s.get().strip() for s in categori_selectors if s.get().strip()]
        if categori:
            loader.add_value('featured_in', categori)

        image_urls = response.xpath(
            '//div[@class="NHQ0m"]/div[@class="d95fI"]/figure//div/a[@class="Prxeh"]/@href').extract()
        full_image_urls = []
        for url in image_urls:
            full_url = response.urljoin(url)
            full_image_urls.append(full_url)
        loader.add_value('image_urls', full_image_urls)

        yield loader.load_item()

# //div[@class="NHQ0m"]/div[@class="d95fI"] - прямая ссылка на изображение...
# //div[@class="NHQ0m"]/div[@class="d95fI"]/figure//div/a[@class="Prxeh"]/@href