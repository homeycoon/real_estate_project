# Real Estate Project

Этот проект представляет собой приложение на Flask (с использованием Dash), 
которое визуализирует и позволяет анализировать статистику по рынку аренды коммерческой 
недвижимости в Казани (на основе данных с сайтов 2 агрегаторов недвижимости).

**ПРИМЕЧАНИЕ**: Данный проект носит демонстрационный характер, в базу данных предварительно загружено лишь относительно небольшое количество объявлений для демонстрации возможностей визуализации и расчетов в рамках сервиса (чтобы не создавать без особой надобности чрезмерной нагрузки на агрегаторы объявлений и не закидывать на GitHub слишком тяжелый файл SQLite), и потому представленная на дашборде / на карте / в калькуляторе информация не является полной и стопроцентно достоверной. Однако с помощью указанных ниже парсеров (также приложены к проекту) технически возможно выгрузить большее количество объявлений и использовать их как основу для построения более близкой к реальности статистики.

### Требования
- Python 3.8+
- Docker

### Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/homeycoon/real_estate_project.git
cd real_estate_project
```
2. Создайте файлы:
- `.env` (заполнить переменные по примеру `.env.example`: SECRET_KEY можно придумать любой; если нужно будет выгрузить данные с помощью парсеров: DADATA_TOKEN и DADATA_SECRET нужно получить на сайте https://dadata.ru/ после регистрации)
3. Запустите в терминале команду:
```bash
docker-compose up --build
```
Начнется сборка и запуск контейнеров. Дождитесь появления в
терминале сообщения о завершении запуска приложения.
4. Перейдите по пути `127.0.0.1:5000` для открытия приложения.

### Использование приложения
`/`: На **главной странице** представлена интерактивная карта с информацией о медианной ставке аренды за 1 м2 по районам Казани (Plotly).

<img src="map_REP.png" width="478" height="433" alt="Главная страница с картой">

`/dash/`: **Страница с дашбордом** представляет ключевые метрики по рынку аренды коммерческой недвижимости в Казани. Для удобства можно пользоваться _фильтрами_ по источнику данных, району города, микрорайону, типу помещения (офис / торговая площадь / свободного назначения), этажу (Dash).

<img src="dashboard_REP.png" width="696" height="840" alt="Страница с дашбордом">

`/calculator`: **Страница с калькулятором** позволяет по выбранным критериям рассчитать примерную стоимость аренды подобной коммерческой недвижимости (на основе данных в базе данных).

<img src="calculator_REP.png" width="478" height="433" alt="Страница с калькулятором">

**Главное меню**: для удобства на каждой странице есть меню с ссылками на все страницы приложения, а также кнопка `Выгрузить в .xlsx` для выгрузки краткой аналитической информации по рынку аренды коммерческой недвижимости.

### Данные
Источниками данных по рынку аренды коммерческой недвижимости в Казани послужили агрегаторы объявлений ЦИАН и ДомКлик.

Данные были собраны предварительно и сохранены в базе данных SQLite (файл `database/real_estate.db`).

Сбор данных осуществлялся с помощью двух парсеров: один - для ЦИАН, второй - для ДомКлик. Исходный код обоих парсеров также приложен к проекту в папке `parsers/`. При желании Вы можете запустить парсеры для сбора актуальных данных - для этого нужно запустить файл `parsers/main.py`.
