# Alcoteka Scraper

Scrapy-проект для парсинга данных с сайта [Alcoteka](https://alkoteka.com) через их API.

---

## Описание

Проект выполняет запросы к API сайта, собирает информацию о товарах и сохраняет её в формате JSON.  
Поддерживает работу через прокси для обхода ограничений по IP.

---

## Установка

1. Клонируем репозиторий:
git clone git@github.com:LyHaTik/test_scrapy.git

2. Создаем виртуальное окружение и устанавливаем зависимости:
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

---

## Настройки

### alcoteka/settings.py
DOWNLOAD_DELAY – задержка между запросами (по умолчанию 1 секунда)
CONCURRENT_REQUESTS_PER_DOMAIN – количество параллельных запросов (по умолчанию 1)
PROXIES – список прокси для подключения к API

### alcoteka/spr/spr_cities.json
Для извлечения данных по другим городам следует добавить словари в следующем формате:
[
  {
    "name": "Краснодар",
    "uuid": "65e2983b-d801-11eb-80d3-00155d03900a"
  }
]
uuid - извлекается "ручным" способом через режим разработчикав браузере

### alcoteka/spr/spr_categories_url.json
Для извлечения данных по другим категориям следует добавить словари в следующем формате:
[
  {
    "name": "Слабоалкогольные напитки",
    "url": "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2"
  }
]
url - извлекается "ручным" способом в браузере

---

## Запуск
scrapy crawl alkoteka_spider -o results.json

---

## dashbosrd
pbi/views.pbix

---

## Примечания
Проект использует только API сайта, поэтому User-Agent не обязателен.
Если PROXIES пуст, запросы выполняются напрямую без прокси.

---

## Структура проекта
test_scrapy/
│
├─ alcoteka/
│  ├─ parsers/               
│  │  └─ product_parser.py          # парсинга отдельного продукта
│  ├─ spiders/               
│  │  └─ alcoteka_project.py        # Паук  
│  ├─ spr/
│  │  ├─ spr_categories_url.json    # Cправочник категорий     
│  │  └─ spr_cities.json            # Cправочник городов       
│  ├─ items.py                      
│  ├─ middlewares.py                # Spider middlewares (включая ProxyMiddleware)
│  ├─ results.json                  # Результирующий файл парсинга
│  └─ settings.py                   # Настройки проекта
├─ pbi/                 
│  ├─ view.pbix                     # dashboard (PowerBI)
│  └─ logo.png                      # Лого сайта
├─ LICENSE  
├─ .gitiignore             
├─ requirements.txt           
├─ README.md                        # Этот файл
└─ scrapy.cfg                       # Конфиг Scrapy



## Развитие
- Сохранение сырых данных в raw-слой PostgreSQL.
- Нормализация данных.
- Добавление историчности.
- Точечное обновление данных с сохранением историчности.
- Ежедневное обновление данных. Наиболее пристально отслеживаемые поля: стоимость и количество товара. Это позволит рассчитывать наиболее покупаемые позиции.
