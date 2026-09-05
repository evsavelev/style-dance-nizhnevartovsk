"""One-time, reproducible transfer from the read-only Stitch export."""
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from PIL import Image
from fontTools.ttLib import TTFont
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ORIG=ROOT/'stitch-original'
s=BeautifulSoup((ORIG/'desktop/f5ee03817e2940f0ae21469e0799ad15/index.html').read_text(encoding='utf-8'),'html.parser')
manifest=json.loads((ORIG/'download-manifest.json').read_text(encoding='utf-8'))
downloads={r['url']:ORIG/r['file'] for r in manifest if r['status']=='ok'}
for d in ['assets/images','assets/fonts']: (ROOT/d).mkdir(parents=True,exist_ok=True)
# Keep exact original Tailwind tokens, compile to a local CSS file.
config=s.select_one('#tailwind-config').string.replace('tailwind.config =','module.exports =')
(ROOT/'tailwind.config.cjs').write_text(config+";\nmodule.exports.content = ['./index.html', './script.js'];\n",encoding='utf-8')
for tag in s.select('script, style, head link'): tag.decompose()
for c in s.find_all(string=lambda t:isinstance(t,Comment)): c.extract()
def fragment(text): return BeautifulSoup(text,'html.parser')
def replace_text(old,new):
 for t in list(s.find_all(string=True)):
  if old in t: t.replace_with(str(t).replace(old,new))
def settext(node,text): node.clear();node.append(text)
def addclass(node,*cs): node['class']=node.get('class',[])+list(cs)
# Local, deduplicated image pipeline; descriptive filenames retain image roles.
names=['hero','hip-hop','kpop','bachata','high-heels','breakdance','kids','studio','training','teacher-hip-hop','teacher-kpop','teacher-high-heels','teacher-breakdance','gallery-events','kids','studio','high-heels','bachata','hero','breakdance','teacher-hip-hop']
image_map={};asset_log=[]
for i,img in enumerate(s.select('img')):
 url=img['src']; original_src=downloads[url]; src=original_src
 full=ROOT/'.tools/source-images'/src.name
 if full.exists(): src=full
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 if digest not in image_map:
  name=names[i];im=Image.open(src).convert('RGB'); im.thumbnail((1440,1440))
  rel='assets/images/'+name+'.webp'; im.save(ROOT/rel,'WEBP',quality=84,method=6)
  w,h=im.size
  image_map[digest]=(rel,w,h)
  if w>640:
   small=im.copy();small.thumbnail((640,1000));small.save(ROOT/('assets/images/'+name+'-640.webp'),'WEBP',quality=82,method=6)
  if w>800:
   medium=im.copy();medium.thumbnail((800,1400));medium.save(ROOT/('assets/images/'+name+'-800.webp'),'WEBP',quality=82,method=6)
  asset_log.append({'source':str(original_src.relative_to(ORIG)),'fullResolution':full.exists(),'file':rel,'width':w,'height':h,'bytes':(ROOT/rel).stat().st_size})
 rel,w,h=image_map[digest]; img['src']=rel;img['width']=w;img['height']=h;img['decoding']='async'
 if w>640:
  img['srcset']=rel.replace('.webp','-640.webp')+' 640w, '+(rel.replace('.webp','-800.webp')+' 800w, ' if w>800 else '')+rel+' '+str(w)+'w'
  img['sizes']='(max-width: 639px) calc(100vw - 40px), (max-width: 1023px) 50vw, 600px'
  if img.find_parent(id='styles'):img['sizes']='(max-width: 639px) calc(100vw - 40px), (max-width: 1023px) 50vw, 390px'
  if img.find_parent(id='teachers'):img['sizes']='(max-width: 639px) 45vw, (max-width: 1023px) 45vw, 270px'
  if img.find_parent(class_='gallery-item'):
   item=img.find_parent(class_='gallery-item'); span=next((int(c.split('-')[-1]) for c in item.get('class',[]) if c.startswith('lg:col-span-')),12)
   img['sizes']='(max-width: 767px) '+('calc(100vw - 40px)' if span>=8 else '45vw')+', (max-width: 1023px) 50vw, '+str(round(1216*span/12))+'px'
 img['alt']=img.get('alt','').replace('STYLE DANCE','').replace('в Нижневартовске','').strip()
 if i==0: img['fetchpriority']='high';img['loading']='eager';img['alt']='Командная хореография в индустриальном зале — иллюстрация'
 else: img['loading']='lazy'
 if img.find_parent(id='teachers'): img['alt']='Танцевальный образ: '+['Hip-Hop','K-Pop','High Heels','Брейк-данс'][i-9]
# Only normal DM Sans 400/600/700 and Space Grotesk 400/600/700; use WOFF2.
font_css=[]
css=(ORIG/'assets/resource-c9c2f70d3ac9ebf7.css').read_text()
for block in re.findall(r'@font-face\s*\{([^}]+)\}',css):
 family=re.search(r"font-family:\s*'([^']+)'",block).group(1)
 weight=re.search(r'font-weight:\s*(\d+)',block).group(1)
 style=re.search(r'font-style:\s*(\w+)',block).group(1)
 if style!='normal' or weight not in ['400','600','700']:continue
 url=re.search(r'url\(([^)]+)\)',block).group(1)
 filename=family.lower().replace(' ','-')+'-'+weight+'.woff2'
 font=TTFont(downloads[url]);font.flavor='woff2';font.save(ROOT/'assets/fonts'/filename)
 font_css.append("@font-face{font-family:'"+family+"';font-style:normal;font-weight:"+weight+";font-display:swap;src:url('./assets/fonts/"+filename+"') format('woff2');}")
(ROOT/'fonts.css').write_text('\n'.join(font_css),encoding='utf-8')
(ROOT/'asset-provenance.json').write_text(json.dumps(asset_log,ensure_ascii=False,indent=2),encoding='utf-8')
# Content truth: no fictional results, staff, equipment, schedule or form submissions.
replacements={
'0+':'Старт','Светлые залы':'Дружбы Народов, 25','Для детей и взрослых':'Выберите свой стиль',
'6 направлений танца':'Найдите свой ритм',
'Живая энергия репетиций в STYLE DANCE':'Музыка. Движение. Твой ритм.',
'Мы находимся в самом сердце Нижневартовска на улице Дружбы Народов, 25. На втором этаже мы спроектировали пространство, где каждый чувствует свободу самовыражения: от первого шага в зале до уверенных импровизаций.':'Школа находится в Нижневартовске, на улице Дружбы Народов, 25, на втором этаже. Позвоните, чтобы выбрать направление, узнать о занятиях и договориться о первом визите.',
'Чистый и плотный звук':'Почувствовать музыку',
'Акустика настроена под глубокие басы и четкий бит, чтобы каждый акцент трека чувствовался телом.':'Hip-Hop, K-Pop, Dancehall — найдите ритм и характер движения, который вам близок.',
'Вентиляция и микроклимат':'Попробовать новое',
'Свежий воздух на протяжении всей тренировки даже при максимальной нагрузке в группах.':'От пластики High Heels до парной бачаты: начните со стиля, который давно хотелось попробовать.',
'Поддерживающее комьюнити':'Начать с разговора',
'Уважение, открытость и полное отсутствие неловкости для новичков.':'Расскажите администратору о своём опыте и пожеланиях — уточните подходящий формат занятий.',
'Удобный доступ, парковка рядом со зданием и панорамный свет.':'Нижневартовск. Время первого визита согласуйте со школой по телефону.',
'Педагоги с опытом в баттлах, постановочных проектах и сценических шоу. Составы групп и кураторы распределяются перед стартом блоков.':'Познакомьтесь с преподавателем выбранного направления на занятии. Имена, состав команды и подходящую группу уточните у администратора. Портреты ниже — визуальные образы демо, не фотографии сотрудников.',
'Преподаватель направления':'Ваше направление',
'Профиль и видео-визитка формируются к сезону.':'Уточните преподавателя и формат занятий по телефону.',
'Формируем группы и актуальное время под запросы учеников. Точное время тренировок и уровень группы уточняются при записи у администратора.':'Актуальные дни, время, стоимость и уровень группы уточните у администратора: +7 (3466) 57-03-83. Подберём направление для первого знакомства со школой.',
'Настоящие моменты репетиций, постановок, баттлов и вдохновения в залах на ул. Дружбы Народов, 25.':'Ритм, характер и настроение разных направлений. Галерея иллюстраций демо — не документальная съёмка школы.',
'Оставьте заявку на сайте или напишите нам. Администратор согласует удобное время и расскажет про форму одежды.':'Позвоните по номеру +7 (3466) 57-03-83. Уточните время, стоимость занятия и подходящую одежду.',
'Или несколько, если сомневаетесь. Пробные уроки позволяют познакомиться со стилем без обязательств.':'Или несколько, если сомневаетесь. Расскажите администратору, что вам интересно и какой у вас опыт.',
'Познакомьтесь с тренером, оцените просторные залы на ул. Дружбы Народов, 25 и сделайте свой первый шаг.':'После согласования времени приходите по адресу: ул. Дружбы Народов, 25, 2 этаж. Познакомьтесь с преподавателем и сделайте первый шаг.',
'Никакого прежнего опыта не требуется. Базу раскладываем шаг за шагом.':'Уточните у администратора, какие занятия подойдут для знакомства с танцами.',
'Единомышленники, совместные видеосъемки и заряд драйва после учебы или работы.':'Хотите общаться с людьми, которым тоже нравится музыка и движение.',
'© 2025 STYLE DANCE STUDIO. ALL RIGHTS RESERVED. ARCHITECTURAL DANCE SPACES.':'© 2026 STYLE DANCE · Демонстрационная версия',
'События и баттлы (Events)':'Баттлы и сцена',
'По расписанию групп и предварительной записи на занятия':'Актуальные часы работы и время занятий уточняйте по телефону.',
}
for a,b in replacements.items():replace_text(a,b)
replace_text('и настоящая брейкинг-культура для всех возрастов.','и культура брейкинга.')
settext(s.select('body > section')[0].select_one('.grid-cols-3 > div > div'),'16')
replace_text('6 ключевых направлений для детей и взрослых','Направления для детей и взрослых')
for i,h in enumerate(s.select('#teachers h3')):settext(h,['Hip-Hop','K-Pop','High Heels','Брейк-данс'][i])
# Stable semantic document and anchor navigation.
hero=s.select('body > section')[0];hero['id']='home';addclass(hero,'hero')
s.body['id']='top'
for h in s.select('h4,h5'):h.name='h3'
main=s.new_tag('main',id='main-content')
s.header.insert_after(main)
for sec in list(s.select('body > section')):main.append(sec.extract())
skip=fragment('<a class="skip-link" href="#main-content">Перейти к содержимому</a>').a;s.body.insert(0,skip)
for a in s.select('a[href="#"]'):a['href']='#top'
for a in s.select('a[href^="tel:"]'):a['href']='tel:+73466570383'
# Remove simulated form entirely. Booking is an explicit contact section.
s.select_one('#booking-modal').decompose()
for b in list(s.select('button[onclick]')):
 action=b.get('onclick','')
 if action.startswith('openBookingModal'):
  b.name='a';b['href']='#booking';del b['onclick']
  addclass(b,'booking-link')
  if 'мессенджер' in b.get_text(): b.decompose()
for sec in main.select(':scope > section'):
 if 'Хватит смотреть' in sec.get_text():
  sec['id']='booking';addclass(sec,'booking-section')
  cta=sec.select_one('.booking-link');cta['href']='tel:+73466570383';settext(cta,'Позвонить и записаться')
  cta.insert_after(fragment('<a class="booking-phone" href="tel:+73466570383">+7 (3466) 57-03-83</a><p class="booking-note">Уточните время и стоимость занятия у администратора.</p>'))
# Contacts: supplied number visible, working routes only.
contact=s.select_one('#contacts')
contact.select_one('h2').insert_after(fragment('<a class="contact-phone" href="tel:+73466570383">+7 (3466) 57-03-83</a>'))
# Remove nonfunctional day tabs and replace invented times/levels.
s.select_one('#day-tabs').decompose()
for i,row in enumerate(s.select('.schedule-item')):
 row.select_one('.font-code-time').string='По записи'
 h=row.select_one('h3');settext(h,['Hip-Hop','K-Pop','High Heels','Детские танцы'][i])
 badge=row.select_one('span.font-label-caps');settext(badge,'Время уточняется')
 addclass(row,'schedule-row')
# Make all supplied additional styles discoverable, without asserting group availability.
s.select_one('#styles > div').append(fragment('<div class="more-styles"><h3>Ещё больше движения</h3><p>Zumba · Jazz-funk · Dancehall · Contemporary · Latina · Stretching · Shuffle · Свадебный танец · Вальс · Тверк</p><a href="tel:+73466570383">Уточнить набор по направлениям <span aria-hidden="true">↗</span></a></div>'))
# Header responsive behavior.
s.header['class']=['site-header']
s.header.select_one('div')['class']=['header-inner']
s.header.select_one('nav')['class']=['desktop-nav']
s.header.select_one('nav')['aria-label']='Основная навигация'
s.select_one('#mobile-menu')['class']=['mobile-menu']
s.select_one('#mobile-menu')['hidden']=''
s.select_one('#mobile-menu')['aria-label']='Мобильная навигация'
s.select_one('#mobile-menu').name='nav'
menub=s.select_one('#mobile-menu-btn');menub['class']=['menu-toggle'];menub['aria-expanded']='false';menub['aria-controls']='mobile-menu';menub['type']='button'
addclass(s.header.select_one('.booking-link'),'header-booking')
# Real gallery controls, native links without JS and dialog enhancement with JS.
for b in s.select('.gallery-filter-btn'):
 cat=re.search(r"filterGallery\('([^']+)'",b['onclick']).group(1)
 del b['onclick'];b['data-filter']=cat;b['aria-pressed']='true' if cat=='all' else 'false';b['type']='button'
for item in s.select('.gallery-item'):
 item.name='a';img=item.img;item['href']=img['src'];item['aria-label']='Увеличить: '+img['alt'];item['data-lightbox']=''
 # Captions are decorative; equivalent alt is included in accessible link name.
 if item.div: item.div['aria-hidden']='true'
status=fragment('<p id="gallery-status" class="sr-only" role="status" aria-live="polite">Показано 8 изображений</p>')
s.select_one('#gallery-filter-tabs').insert_after(status)
s.body.append(fragment('<dialog id="photo-dialog" aria-label="Просмотр изображения"><button class="dialog-close" type="button" aria-label="Закрыть изображение">×</button><figure><img id="dialog-image" alt=""><figcaption id="dialog-caption"></figcaption></figure></dialog>'))
# Replace heavy Material icon font with small inline SVGs.
paths={
'arrow_outward':'M7 17 17 7M7 7h10v10','arrow_forward':'M4 12h16m-6-6 6 6-6 6',
'south':'M12 4v16m-6-6 6 6 6-6','bolt':'m13 2-9 12h7l-1 8 10-13h-7z',
'location_on':'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0ZM12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6',
'calendar_month':'M4 5h16v16H4zM4 10h16M8 2v6M16 2v6M8 14h2m4 0h2m-8 3h2m4 0h2',
'menu':'M4 6h16M4 12h16M4 18h16','graphic_eq':'M4 9v6m4-10v14m4-17v20m4-17v14m4-10v6',
'equalizer':'M5 13v7m7-15v15m7-11v11','air':'M3 8h12a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h5',
'group':'M8 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM2 21v-3c0-6 12-6 12 0v3m2-17a4 4 0 0 1 0 8m1 3c4 0 5 2 5 6',
'info':'M12 16v-5m0-4v1M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
'call':'M5 3h4l2 5-3 2a16 16 0 0 0 6 6l2-3 5 2v4c0 2-2 3-4 2C10 19 5 14 3 7c-1-2 0-4 2-4Z',
'navigation':'m3 10 18-7-7 18-3-8z','schedule':'M12 6v6l4 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
'location_city':'M3 21V7h8v14M11 3h10v18M6 10h2m-2 4h2m6-8h4m-4 4h4m-4 4h4M1 21h22',
'question_answer':'M3 3h18v14H8l-5 4zM7 7h10M7 11h7',
'open_in_new':'M14 3h7v7m0-7L10 14M10 3H3v18h18v-7'
}
paths['pin_drop']=paths['location_on'];paths['place']=paths['location_on'];paths['edit_calendar']=paths['calendar_month']
for icon in list(s.select('.material-symbols-outlined')):
 name=icon.get('data-icon',icon.get_text(strip=True))
 svg=fragment('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="'+paths.get(name,paths['arrow_forward'])+'"/></svg>').svg
 svg['class']=['icon']+[c for c in icon.get('class',[]) if c!='material-symbols-outlined'];icon.replace_with(svg)
# Metadata and local resources.
s.head.append(fragment('<link rel="preload" as="font" type="font/woff2" href="assets/fonts/space-grotesk-700.woff2" crossorigin><link rel="preload" as="font" type="font/woff2" href="assets/fonts/dm-sans-400.woff2" crossorigin>'))
base='https://evsavelev.github.io/style-dance-nizhnevartovsk/'
description='STYLE DANCE — школа танцев в Нижневартовске. Hip-Hop, K-Pop, High Heels, бачата и другие направления. Дружбы Народов, 25, 2 этаж. Запись: +7 (3466) 57-03-83.'
s.head.append(fragment('<meta name="description" content="'+description+'"><meta name="theme-color" content="#121316"><link rel="canonical" href="'+base+'"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="fonts.css"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="STYLE DANCE"><meta property="og:title" content="STYLE DANCE — школа танцев в Нижневартовске"><meta property="og:description" content="'+description+'"><meta property="og:url" content="'+base+'"><meta property="og:image" content="'+base+'assets/images/hero.webp"><meta property="og:image:alt" content="Танцевальная команда — иллюстрация STYLE DANCE"><meta name="twitter:card" content="summary_large_image">'))
schema={'@context':'https://schema.org','@type':['LocalBusiness','EducationalOrganization'],'@id':base+'#school','name':'STYLE DANCE','url':base,'description':'Школа танцев в Нижневартовске','telephone':'+73466570383','address':{'@type':'PostalAddress','streetAddress':'ул. Дружбы Народов, 25, 2 этаж','addressLocality':'Нижневартовск','addressRegion':'Ханты-Мансийский автономный округ — Югра','addressCountry':'RU'}}
tag=s.new_tag('script',type='application/ld+json');tag.string=json.dumps(schema,ensure_ascii=False);s.head.append(tag)
script=s.new_tag('script',src='script.js',defer='');s.head.append(script)
# Give repeated action links a contextual accessible name.
for a in s.select('#styles .booking-link'):
 h=a.find_parent(class_='group').find(['h3','h4'])
 if h:a['aria-label']='Записаться на пробное — '+h.get_text(' ',strip=True)
for el in s.select('[onclick]'): del el['onclick']
(ROOT/'index.html').write_text(str(s),encoding='utf-8')
print('Transferred',len(asset_log),'unique images,',len(font_css),'font faces')
