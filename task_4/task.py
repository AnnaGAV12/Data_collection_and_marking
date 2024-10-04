# 1. Выберите веб-сайт с табличными данными, который вас интересует.
# 2. Напишите код Python, использующий библиотеку requests для отправки HTTP GET-запроса на сайт и получения HTML-содержимого страницы.
# 3. Выполните парсинг содержимого HTML с помощью библиотеки lxml, чтобы извлечь данные из таблицы.
# 4. Сохраните извлеченные данные в CSV-файл с помощью модуля csv.

import requests
from lxml import html
import csv

# Получение ответа от сайта
def get_response(url):
    # UserAgent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f'Error response: {url}: {e}')


# Парсинг данных с сайта
def parse_data(response):
    tree = html.fromstring(response.content)
    table_rows = tree.xpath("//table[@class='wikitable']/tbody/tr")
    data_list = []
    try:
        for rows in table_rows:
            data = {}
            data["Country (exonym)"] = ''.join(map(str.strip, rows.xpath(
                ".//th[1]//text() | .//td/i/b/a/text() | .//td/b/a/text() | .//td/i/a/text() | .//td/i/a/b/text()")))
            data["Capital (exonym)"] = ''.join(map(str.strip, rows.xpath(".//th[2]//text() | .//td[2]/a/text()")))
            data["Country (endonym)"] = ''.join(
                map(str.strip, rows.xpath(".//th[3]//text() | .//td[3]/b/text() | .//td[3]/b/span/span/text()")))
            data["Capital (endonym)"] = ''.join(
                map(str.strip, rows.xpath(".//th[4]//text() | .//td[4]/b/text() | .//td[4]/b/span/span/text()")))
            data["Official or native language"] = ''.join(
                map(str.strip, rows.xpath(".//th[5]//text() | .//td[5]/a/text()")))
            data_list.append(data)
        return data_list
    except Exception as e:
        print(f'Parsing error: {e}')


# Сохранение данных в csv
def save_data(data_list, file_path):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            csvwriter = csv.writer(file)
            # Создание заголовков для CSV файла
            for row in data_list:
                csvwriter.writerow([row["Country (exonym)"], row["Capital (exonym)"], row["Country (endonym)"],
                                    row["Capital (endonym)"], row["Official or native language"]])
    except IOError as e:
        print(f'Error save: {file_path}:  {e}')


def main():
    file_path = 'c:/Users/a.goncharova/PycharmProjects/pythonProject2/Data_collection_and_markup/task_4/task.csv'
    # URL для запроса данных
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_and_their_capitals_in_native_languages'

    response = get_response(url)
    if response:
        data_list = parse_data(response)
        save_data(data_list, file_path)


if __name__ == "__main__":
    main()
