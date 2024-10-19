from selenium import webdriver # Основной модуль веб-драйвера
from selenium.webdriver.chrome.options import Options # Модуль для браузера используем Ghrome
from selenium.webdriver.support.ui import WebDriverWait # Модуль для ожидания условия
from selenium.webdriver.support import expected_conditions as EC # Модуль набора присетов для WebDriverWait
from selenium.webdriver.common.keys import Keys # Модуль симуляции клавиатуры
from selenium.webdriver.common.by import By # Определение местоположения элементов
from selenium.common.exceptions import TimeoutException, NoSuchElementException # Отлов ошибок
import time # Модуль для работы с временем
import re # Модуль для работы с регулярными выражениями
import pandas as pd # Модуль для работы с базами данных
from bs4 import BeautifulSoup # Модуль анализа HTML документов
import requests # Модуль отправки HTML запросов

# Модуль работы браузера
options = Options()
options.add_argument('start-maximized')  # Запуск браузера в полном окне
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
driver = webdriver.Chrome(options=options)  # Драйвер который запускает экземпляр браузера
driver.get('https://www.wildberries.ru/') # открытие вебсайта
time.sleep(4) # Таймер задержки

# Поиск строки поиска и ввод запроса в строку
wait = WebDriverWait(driver, 10) # Ожидание прогрузки страницы
try:
    input = wait.until(EC.presence_of_element_located((By.ID, "searchInput"))) # Ищем строку поиска
except (TimeoutException, NoSuchElementException, Exception) as e:
        print("Error dont find element: {e} ")
# Вводим фразу поиска и нажимаем Enter
input.send_keys('процессор amd 9') # Имитируем ввод запроса в строку поиска
input.send_keys(Keys.ENTER) # Имитируем нажание кнопки ввода

# Модуль создания списка, прокручивания сайта и подсчёта карточек товара, парсинга и перехода на следующию страницу
product_list = []  # Список процессоров
# Прокручиваем сайт до конца
try:
    while True:
        count = None  # Для подсчёта количества карточек товара
        while True:
            time.sleep(4)  # Таймер задержки
            cards = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//article[@id]')))  # Ищем карточку товара

            if len(cards) == count:  # Выходим из цикла, если при прокрутке страницы, количество товаров не меняется
                break

            count = len(cards)  # Посчитываем количество карточек товара на странице

            driver.execute_script('window.scrollBy(0, 1800)')  # Прокручиваем страницу выполняя JAVA Script
            time.sleep(2)  # Таймер задержки
        # Проходимся по карточкам, извлекаем ссылку на товар и добавляем в product_list
        for card in cards:
            url = card.find_element(By.XPATH, './div/a').get_attribute('href')
            product_list.append(url)

        try:
            next = driver.find_element(By.XPATH,
                                       "//a[@class='pagination-next pagination__next j-next-page']")  # Ищем кнопку перехода на следующию страницу
            next.click()
        except (TimeoutException, NoSuchElementException, Exception):
            break
finally:
    driver.quit()

# Модуль парсинга данных с страницы товара
driver2 = webdriver.Chrome(options=options)  # Ещё один экземпляр браузера FireFox
wait2 = WebDriverWait(driver2, 10)  # Таймер ожидания действий driver2
data_list = []  # Лист данных о процессорах
try:
    # Парсинг данных
    for url_item in product_list:
        data_parsing = {}  # Словарь для парсинга

        driver2.get(url_item)  # Переход по страницам

        # Парсим название процессора
        try:
            data_parsing['name'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//h1"))).text
        except (TimeoutException, Exception):
            data_parsing['name'] = None

        # Блок парсинга цены, с скидкой, без, старой ценой, новой ценой и тд
        # Парсим цену процессора, WB кошелёк распродажа
        try:
            price = wait2.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@class, "price-block__wallet-price")]')))
            data_parsing['price_wb_wallet_sales'] = float(re.sub(r'[^\d.]+', '', price[1].text))
        except (TimeoutException, Exception):
            data_parsing['price_wb_wallet_sales'] = None

        # Парсим цену процессора, WB кошелёк старая цена
        try:
            price = wait2.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[contains(@class, "price-block__final-price wallet")]')))
            data_parsing['price_wb_wallet_old'] = float(re.sub(r'[^\d.]+', '', price[1].text))
        except (TimeoutException, Exception):
            data_parsing['price_wb_wallet_old'] = None

        # Парсим цену процессора, цена распродажа
        try:
            price = wait2.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[contains(@class, "price-block__final-price") and not(contains(@class, "wallet"))]')))
            data_parsing['price_sales'] = float(re.sub(r'[^\d.]+', '', price[1].text))
        except (TimeoutException, Exception):
            data_parsing['price_sales'] = None

        # Парсим цену процессора, старая цена до распродажи
        try:
            price = wait2.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@class, "price-block__old-price")]')))
            data_parsing['price_old'] = float(re.sub(r'[^\d.]+', '', price[1].text))
        except (TimeoutException, Exception):
            data_parsing['price_old'] = None

        # Парсим бренд процессора
        try:
            data_parsing['brand'] = wait2.until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-page__header-brand"))).text
        except (TimeoutException, Exception):
            data_parsing['brand'] = None

        # Ссылка на процессор
        try:
            data_parsing['url'] = url_item
        except (TimeoutException, Exception):
            data_parsing['url'] = None

        # Парсинг дополнительного элемента (Названия магазина) с помощью BeautifulSoup
        url_item = product_list
        response = driver2.page_source
        soup = BeautifulSoup(response, features="html.parser")
        site_elements = soup.find_all("div", class_="seller-info__content")

        try:
            shop_info = soup.select_one(
                'div.product-page__seller-wrap:nth-child(7) > section:nth-child(2) > div:nth-child(6) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span:nth-child(1)')
            if shop_info:
                data_parsing['shop_name'] = shop_info.text.strip()
        except Exception as e:
            data_parsing['shop_name'] = None

        # Находим кликабельный элемент "Все характеристики и описание" чтобы получить открыть таблицу с данными
        try:
            button = WebDriverWait(driver2, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'product-page__btn-detail')))
            if button:
                button.click()  # Имитируем клик на кнопку "Все характеристики и описание"
                WebDriverWait(driver2, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@class="popup popup-product-details shown"]')))
        except (TimeoutException, NoSuchElementException, Exception) as e:
            print("Error dont find element: {e} ")

        # Обрабатываем табличные данные
        table_row_name = wait2.until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="popup popup-product-details shown"]//th')))
        table_row_param = wait2.until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="popup popup-product-details shown"]//td')))
        # Заносим данные в зависимости от названия
        for i in range(len(table_row_name)):
            if table_row_name[i].text == 'Процессор':
                try:
                    data_parsing['processor'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['processor'] = None
            elif table_row_name[i].text == 'Линейка процессоров':
                try:
                    data_parsing['family_processor'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['family_processor'] = None
            elif table_row_name[i].text == 'Сокет':
                try:
                    data_parsing['soked'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['soked'] = "-"
            elif table_row_name[i].text == 'Тактовая частота процессора':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['cpu_clock_speed'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['cpu_clock_speed'] = None
            elif table_row_name[i].text == 'Максимальная частота в турбо режиме':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['bost_cpu_clock_speed'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['bost_cpu_clock_speed'] = None
            elif table_row_name[i].text == 'Количество ядер процессора':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['processor_cores'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['processor_cores'] = None
            elif table_row_name[i].text == 'Максимальное число потоков':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['max_count_threads'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['max_count_threads'] = None
            elif table_row_name[i].text == 'Техпроцесс':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['technical_process'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['technical_process'] = None
            elif table_row_name[i].text == 'Встроенная графическая система':
                try:
                    data_parsing['processor_graphic'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['processor_graphic'] = None
            elif table_row_name[i].text == 'Объем кэша L3':
                try:
                    val = table_row_param[i].text.strip()
                    val, *_ = val.split()
                    data_parsing['cashe_L3'] = float(re.sub(r'[^\d.]+', '', val))
                except (TimeoutException, Exception):
                    data_parsing['cashe_L3'] = None
            elif table_row_name[i].text == 'Страна производства':
                try:
                    data_parsing['country'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['country'] = None
            elif table_row_name[i].text == 'Гарантийный срок':
                try:
                    data_parsing['guarantee_period'] = table_row_param[i].text
                except (TimeoutException, Exception):
                    data_parsing['guarantee_period'] = None

        data_list.append(data_parsing)  # Добавляем спарсеные значения в базу
finally:
    driver2.quit()

# Замена None на "-"
df = df.fillna('-').astype(object)

# Сохраняем DataFrame в CSV файл
filename = 'amd_processor.csv'
df = pd.DataFrame(df)
df.to_csv(filename, index=False, encoding='utf-8-sig')
print(f'Данные успешно сохранены в файл: {filename}')