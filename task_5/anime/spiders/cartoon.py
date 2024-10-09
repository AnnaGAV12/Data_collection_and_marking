import scrapy
from scrapy.exceptions import NotSupported, IgnoreRequest
from twisted.internet.error import TCPTimedOutError, ConnectionRefusedError

class CartoonSpider(scrapy.Spider):
    name = "cartoon"
    allowed_domains = ["animefox.org"]
    start_urls = ["https://animefox.org/anime"]
    # Переменная для пагинации, старт отсчёта страниц
    page_count = 1

    def parse(self, response):
        # Скрапим с общего списка
        try:
            for ani in response.xpath('//article[@class="short clearfix with-mask"]'):
                anime_name = ani.xpath('.//div[@class="short-in"]/a/@title').get()
                anime_genre = ani.xpath('.//div[@class="short-cat"]/text()').get()
                anime_rating = ani.xpath('.//div[@class="rate_nums"]/text()').get()
                anime_rating = anime_rating + "/10" if anime_rating else None
                link = ani.xpath('.//div[@class="short-in"]/a[@class="short-title"]//@href').get()
                if link is not None:
                    yield response.follow(url=link, callback=self.anime_parse, meta={
                        'anime_name': anime_name,
                        'anime_genre': anime_genre,
                        'anime_rating': anime_rating
                    })
                else:
                    raise ValueError('The link to the anime details was not found.')
        # Отлов интернет ошибок
        except (NotSupported, IgnoreRequest, TCPTimedOutError, ConnectionRefusedError) as e:
            self.logger.error(f'Network error when trying to follow the link {e}')
        # Отлов всевозможных ошибок
        except Exception as e:
            self.logger.error(f'Error when parsing the anime page: {e}')
        # Пагинация на следующию страницу
        try:
            if self.page_count < 3:
                next_page = response.xpath('//div[@class="pagi-nav clearfix"]/span[@class="pnext"]/a/@href').get()
                if next_page is not None:
                    self.page_count += 1
                    yield response.follow(next_page, callback=self.parse)
                else:
                    raise ValueError('The link to the next page was not found, meybe end anime list page')
        # Отлов интернет ошибок
        except (NotSupported, IgnoreRequest, TCPTimedOutError, ConnectionRefusedError) as e:
            self.logger.error(f'Network error when trying to go to the next page: {e}')
        # Отлов всевозможных ошибок
        except Exception as e:
            self.logger.error(f'Error when trying to go to the next page: {e}')

  # Функция реквеста скапинга
    def anime_parse(self, response):
        try:
            for link_ani in response.xpath('//div[@class="fx-row"]/ul'):
                # Перенос с первой части кода
                name = response.request.meta['anime_name']
                genre = response.request.meta['anime_genre']
                rating = response.request.meta['anime_rating']
                # Парсим таблицу на другой странице
                voiceover = link_ani.xpath('.//li[contains(@class, "vis") and contains(., "Озвучка")]/text()').get()
                date_realese = link_ani.xpath('.//li[contains(@class, "vis") and contains(., "Выход:")]/text()').get()
                episods = link_ani.xpath('.//li[contains(@class, "vis") and contains(., "Эпизоды:")]/text()').get()
                studia = link_ani.xpath('.//li[contains(@class, "vis") and contains(., "Студия:")]/a/text()').get()
                # Добавляем в словарь
                yield {
                    'Название аниме' : name,
                    'Жанр аниме' : genre,
                    'Рейтинг аниме' : rating,
                    'Озвучка аниме' : voiceover,
                    'Дата выхода' : date_realese,
                    'Количество эпизодов' : episods,
                    'Студия произодства' : studia
                    }
        # Отлов интернет ошибок
        except (NotSupported, IgnoreRequest, TCPTimedOutError, ConnectionRefusedError) as e:
                self.logger.error(f'Network error when trying to follow the link {e}')
        # Отлов всевозможных ошибок
        except Exception as e:
            self.logger.error(f'Error when parsing the details anime page: {e}')

# Запуск и сохранение
# scrapy crawl cartoon -o anime_list.json