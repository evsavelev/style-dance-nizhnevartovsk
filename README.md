# STYLE DANCE — Нижневартовск

Демонстрационный статический сайт по утверждённому экспорту Stitch.

- Сайт: https://evsavelev.github.io/style-dance-nizhnevartovsk/
- Репозиторий: https://github.com/evsavelev/style-dance-nizhnevartovsk
- Локальная папка: C:\LANDINGS\style-dance-nizhnevartovsk
- Контакт: +7 (3466) 57-03-83, ул. Дружбы Народов, 25, 2 этаж, Нижневартовск.

## Открыть и изменить

Можно открыть index.html непосредственно в браузере. Для HTTP-проверки:
```powershell
python -m http.server 4173 --bind 127.0.0.1
```
Открыть http://127.0.0.1:4173/.

Готовые index.html, styles.css, fonts.css, script.js и assets/ работают без npm, Stitch, Tailwind CDN, Google Fonts или backend. Все пути относительные и подходят для GitHub Pages в подпапке.

При изменении utility-классов или source.css:
```powershell
npm ci
npm run build
```
styles.css — результат локальной сборки Tailwind 3.4.17; source.css — дополнительные исходные стили; tailwind.config.cjs сохраняет токены Stitch. React/Next не используются.

## Дизайн и материалы

Исходник: f5ee03817e2940f0ae21469e0799ad15. Сравнение: dd83ae81ebd343d18a2c4f6ac5fc4c39. Третий HTML — его дубль.
Решения и аудит: DESIGN.md. Соответствие оригинальных изображений production-файлам: asset-provenance.json.
Из 32 экспортированных изображений выбраны 13 уникальных; те же кадры дополнительно получены в полном разрешении (896–1376 px по ширине) в .tools/source-images/ без изменения stitch-original. Production содержит WebP и варианты 640/800 px каждого кадра. Фотографии и портреты — иллюстрации демо из Stitch, не подтверждение реальной команды/интерьера.
Шрифты: шесть локальных WOFF2 DM Sans / Space Grotesk. Кириллица использует системный fallback.
stitch-original/ исключён из Git и никогда не используется сайтом. Контрольная копия остаётся локально без изменений. Никакие исходные download URL и метаданные приватного проекта не публикуются.

## Поведение

- Все кнопки записи ведут к блоку #booking, затем к реальному tel:+73466570383.
- Отправки форм и фиктивных подтверждений нет; персональные данные не собираются.
- Расписание не содержит выдуманного времени: для четырёх направлений показан запрос времени у администратора.
- Галерея фильтруется, снимки открываются в доступном dialog (Escape, возврат фокуса).
- Mobile menu: aria-expanded, Escape, закрытие после навигации и при изменении ширины.
- Телефон и ссылки маршрута используют данные из задания.
- Цены, имена и биографии педагогов, отзывы, стаж и награды не придуманы.

## Проверки

```powershell
node tools/browser-qa.cjs
node tools/browser-qa.cjs https://evsavelev.github.io/style-dance-nizhnevartovsk/ live
```
Playwright использует установленный Chromium; для другого компьютера задайте CHROME_PATH.
Проверяются 1280×900, 1440×900, 768×1024, 375×812, 390×844, 430×932; overflow, изображения, все назначения CTA, меню, фильтры, lightbox, console и ответы HTTP, внешние runtime-зависимости, axe WCAG A/AA.
Скриншоты, JSON и Lighthouse-отчёты находятся локально в qa/ и исключены из публикации. Результаты — QA.md.
tools/audit-source.py создаёт исходный SHA-манифест. Не запускать повторно для подтверждения неизменности: сравнивать существующий qa/original-sha256.json с текущими файлами.
tools/transfer-stitch.py — одноразовый перенос из локального экспорта, требует Python-пакеты из tools/requirements.txt и перезаписывает рабочий HTML. Обычные правки делать непосредственно в рабочих файлах.
tools/fetch-full-images.py получает полное разрешение тех же изображений из ссылок экспорта в игнорируемый .tools/source-images/. Запустить перед transfer-stitch.py, если нужно повторить перенос с нуля. Оригинал не изменяется.

## SEO и публикация

Статические title/description, canonical, Open Graph, семантические заголовки, LocalBusiness + EducationalOrganization JSON-LD, alt, sitemap.xml и robots.txt.
Никакие рейтинги, цены, часы работы или идентичности сотрудников не включены в Schema.
На project Pages robots.txt из подпапки не управляет корнем evsavelev.github.io: общие crawler-правила относятся к /robots.txt аккаунта. Здесь сохранён запрошенный файл; canonical и sitemap содержат конечный URL.
GitHub Pages публикуется из main, папка / (root). Сборка CSS выполняется до commit; runtime build не нужен.
Не включать stitch-original/ или qa/ в Git. При откате использовать git revert соответствующего коммита, затем push main.

Источники технических решений, проверены 2026-09-05:
- https://v3.tailwindcss.com/docs/installation — локальная сборка CSS;
- https://developers.google.com/search/docs/appearance/structured-data/local-business — бизнес-метаданные.
Лабораторная производительность не равна полевым Core Web Vitals. Индексация и появление расширенных результатов не проверялись.
