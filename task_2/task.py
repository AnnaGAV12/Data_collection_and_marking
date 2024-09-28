# Выполнить скрейпинг данных в веб-сайта http://books.toscrape.com/
# и извлечь информацию о всех книгах на сайте
# во всех категориях: название, цену, количество товара в наличии
# (In stock (19 available)) в формате integer, описание.
# Затем сохранить эту информацию в JSON-файле.

import requests
from bs4 import BeautifulSoup
import json
import re


# Основная функция скрепинга данных
def get_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Fail to conected to — {url}")

        data_list = []

        soup = BeautifulSoup(response.text, features="html.parser")  # парсим сайт.
        site_elements = soup.find_all("article", class_="product_pod")
        # print(soup.prettify()) # проверяем нахождения сведений о книге.

        for elements in site_elements:
            href_element = elements.h3.a["href"]  # ссылку на страницу товара.
            href_response = requests.get(
                "http://books.toscrape.com/catalogue/" + href_element)  # создаём правильный url книги.

            url_book = BeautifulSoup(href_response.text, 'html.parser')  # парсим страницу книги.
            book_elements = url_book.find_all("article", class_="product_page")  # заходим в книгу.

            for book in book_elements:
                try:
                    title = book.find("div", class_="col-sm-6 product_main").h1.text  # получаем название.
                    price = float(book.find("p", class_="price_color").text[1:].replace("£", ""))  # получаем цену.
                    stock_str = book.find("p",
                                          class_="instock availability").text.strip()  # количество товара в наличии.
                    stock = re.search(r"\d+", stock_str)  # регулярное выражение для извлечения числа.
                    number_str = stock.group()  # извлекаем число как строку.
                    number_int = int(number_str)  # преобразуем строку в число.
                    stock_int = re.sub(r"\d+", str(number_int),
                                       stock_str) if stock else 0  # подменяем строковое число на интовое число.
                    description = book.find_all('p')[3].text  # получаем описание книги.

                    # Добавляем в словарь.
                    data_all = {
                        'Title': title,
                        'Price': price,
                        'Stock_int': stock_int,
                        'Description': description
                    }
                    data_list.append(data_all)
                except Exception as e:
                    print(f"Error parsing book: {e}")
        return data_list
    except Exception as e:
        print(f"Error get data from — {url}: {e}")
        return [-1]


# Переход по страницам сайта
def scrape_site():
    try:
        print(f"Start parsing data.")
        url = "http://books.toscrape.com/"  # адрес сайта
        pages = 3  # Количество страниц
        all_data = []
        for page in range(1, pages + 1):
            current_page = url + f"catalogue/page-{page}.html"
            print(f"Scraping data from page {page}, please stand by...")
            data = get_data(current_page)
            all_data.extend(data)
        print(f"The parsing successfully completed.")
        return all_data
    except Exception as e:
        print(f"Error scraping site: {e}")


# Сохранение в json
def save_json(file_name, all_books_data):
    try:
        with open("./Data_collection_and_markup/task_2/" + file_name, 'w', encoding='utf-8') as file:
            json.dump(all_books_data, file, ensure_ascii=False, indent=4)
            print(f"Data saved to ./Data_collection_and_markup/task_2/{file_name}")
    except Exception as e:
        print(f"Error save data to < {file_name} > : {e}")


# Запуск прогарммы
if __name__ == "__main__":
    all_books_data = scrape_site()
    save_json("data_site_books.json", all_books_data)