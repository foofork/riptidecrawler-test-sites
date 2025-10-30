from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from faker import Faker
import random

app = FastAPI()

# Initialize Faker for different locales
fake_en = Faker('en_US')
fake_ar = Faker('ar_SA')
fake_he = Faker('he_IL')

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "site": "encoding-and-i18n"}

@app.get("/", response_class=HTMLResponse)
async def index():
    """Index page with navigation to all encoding tests"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Encoding & i18n Test Site</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .nav-links { list-style: none; padding: 0; }
            .nav-links li { margin: 10px 0; }
            .nav-links a { color: #3498db; text-decoration: none; font-size: 18px; }
            .nav-links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🌍 Encoding & Internationalization Test Site</h1>
        <p>This site tests various character encodings and internationalization features.</p>
        <ul class="nav-links">
            <li><a href="/latin1">Page 1: ISO-8859-1 (Latin-1) Encoding</a></li>
            <li><a href="/utf8-arabic">Page 2: UTF-8 with Arabic (RTL)</a></li>
            <li><a href="/hebrew">Page 3: Hebrew with Bidi Markers</a></li>
            <li><a href="/emoji">Page 4: Emoji-Heavy Content</a></li>
            <li><a href="/mismatch">Page 5: Content-Type Mismatch Test</a></li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/latin1")
async def latin1_page():
    """Page with ISO-8859-1 encoding - includes special Latin characters"""
    # Generate fake data with Latin-1 compatible characters
    company = fake_en.company()
    address = fake_en.address().replace('\n', ', ')

    # Use only Latin-1 safe characters (no emoji)
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="iso-8859-1">
        <title>Café - Menu</title>
        <style>
            body {{ font-family: Georgia, serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f9f9f9; }}
            h1 {{ color: #8b4513; }}
            .menu-item {{ margin: 15px 0; padding: 10px; background: white; border-left: 3px solid #8b4513; }}
            .price {{ float: right; font-weight: bold; color: #d2691e; }}
        </style>
    </head>
    <body>
        <h1>Café de Paris</h1>
        <p><strong>Adresse:</strong> {address}</p>
        <h2>Menu du Jour</h2>
        <div class="menu-item">
            <span class="price">8.50 EUR</span>
            <strong>Café au lait</strong><br>
            Café noir mélangé avec du lait chaud et mousseux
        </div>
        <div class="menu-item">
            <span class="price">12.00 EUR</span>
            <strong>Crêpe Française</strong><br>
            Crêpe traditionnelle avec confiture de fraises et crème fraîche
        </div>
        <div class="menu-item">
            <span class="price">6.50 EUR</span>
            <strong>Croissant Beurré</strong><br>
            Croissant frais avec beurre de Normandie
        </div>
        <div class="menu-item">
            <span class="price">15.00 EUR</span>
            <strong>Spécialité du Chef</strong><br>
            Soufflé au fromage avec salade niçoise
        </div>
        <p style="margin-top: 30px; font-style: italic;">
            La vie est trop courte pour boire du mauvais café! - Napoléon
        </p>
        <p><a href="/">Retour à l'accueil</a></p>
    </body>
    </html>
    """
    try:
        # Return with ISO-8859-1 encoding
        return Response(content=html.encode('iso-8859-1', errors='replace'), media_type="text/html; charset=iso-8859-1")
    except Exception as e:
        # Fallback to UTF-8 if encoding fails
        return HTMLResponse(content=html)

@app.get("/utf8-arabic")
async def arabic_page():
    """Page with UTF-8 Arabic content (RTL text)"""
    # Generate fake Arabic content
    name = fake_ar.name()
    company = fake_ar.company()
    text = fake_ar.text(max_nb_chars=200)

    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>صفحة عربية</title>
        <style>
            body {{ font-family: 'Arial', 'Tahoma', sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #fef5e7; }}
            h1 {{ color: #196f3d; text-align: right; }}
            .content {{ background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }}
            .author {{ margin-top: 20px; padding: 10px; background: #e8f8f5; border-right: 4px solid #1abc9c; }}
            a {{ color: #2980b9; }}
        </style>
    </head>
    <body>
        <h1>🌙 موقع اختبار اللغة العربية</h1>
        <div class="content">
            <h2>مرحبا بكم في موقعنا</h2>
            <p>هذا النص مكتوب باللغة العربية لاختبار الترميز UTF-8 ودعم النصوص من اليمين إلى اليسار (RTL).</p>

            <h3>معلومات الشركة</h3>
            <p><strong>الاسم:</strong> {name}</p>
            <p><strong>الشركة:</strong> {company}</p>

            <h3>نص تجريبي</h3>
            <p>{text}</p>

            <div class="author">
                <strong>ملاحظة مهمة:</strong> يجب أن يظهر هذا النص من اليمين إلى اليسار بشكل صحيح.
            </div>

            <h3>أرقام عربية ورموز</h3>
            <p>الأرقام: ١٢٣٤٥٦٧٨٩٠</p>
            <p>الرموز الخاصة: ﷼ (ريال) | ٪ (نسبة مئوية)</p>
        </div>
        <p style="margin-top: 20px; text-align: right;"><a href="/">← العودة إلى الصفحة الرئيسية</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/hebrew")
async def hebrew_page():
    """Page with Hebrew content and bidi markers"""
    # Generate fake Hebrew content
    name = fake_he.name()
    company = fake_he.company()
    address = fake_he.address().replace('\n', ', ')

    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>דף בעברית</title>
        <style>
            body {{ font-family: 'Arial', 'David', 'Times New Roman', sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #e3f2fd; }}
            h1 {{ color: #0d47a1; text-align: right; }}
            .content {{ background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }}
            .bidi-test {{ padding: 15px; margin: 15px 0; background: #fff3e0; border: 2px dashed #ff6f00; }}
            .ltr-text {{ direction: ltr; text-align: left; }}
            a {{ color: #1976d2; }}
        </style>
    </head>
    <body>
        <h1>✡️ אתר בדיקה בשפה העברית</h1>
        <div class="content">
            <h2>ברוכים הבאים</h2>
            <p>זהו טקסט בעברית לבדיקת קידוד UTF-8 ותמיכה בטקסט דו-כיווני (BiDi).</p>

            <h3>פרטי איש קשר</h3>
            <p><strong>שם:</strong> {name}</p>
            <p><strong>חברה:</strong> {company}</p>
            <p><strong>כתובת:</strong> {address}</p>

            <div class="bidi-test">
                <h3>בדיקת סימני Bidi (U+202A, U+202B, U+202C)</h3>
                <p>טקסט עברי עם \u202aטקסט LTR מוטמע\u202c בתוך המשפט.</p>
                <p>מספר טלפון: \u202a+1-555-0123\u202c (מוטמע LTR)</p>
                <p>דוא"ל: \u202auser@example.com\u202c</p>
                <p class="ltr-text">English text: This is embedded LTR content within an RTL page.</p>
            </div>

            <h3>תווים מיוחדים</h3>
            <p>סימנים: ₪ (שקל) | % (אחוז) | © (זכויות יוצרים)</p>
            <p>ניקוד: שָׁלוֹם עוֹלָם (שלום עולם עם ניקוד)</p>

            <h3>טקסט מעורב</h3>
            <p>זהו משפט בעברית עם מילים באנגלית: Hello World וגם מספרים: 123456</p>
        </div>
        <p style="margin-top: 20px; text-align: right;"><a href="/">← חזרה לדף הבית</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/emoji")
async def emoji_page():
    """Page with emoji-heavy content"""
    emojis = [
        ("🎉", "Party Popper"), ("🚀", "Rocket"), ("❤️", "Red Heart"),
        ("👍", "Thumbs Up"), ("🌟", "Star"), ("🔥", "Fire"),
        ("💡", "Light Bulb"), ("🎨", "Artist Palette"), ("🌈", "Rainbow"),
        ("🦄", "Unicorn"), ("🐱", "Cat Face"), ("🍕", "Pizza"),
        ("☕", "Coffee"), ("🎵", "Musical Note"), ("📱", "Mobile Phone"),
        ("💻", "Laptop"), ("🌍", "Earth Globe"), ("✨", "Sparkles")
    ]

    emoji_grid = ""
    for emoji, name in emojis:
        emoji_grid += f'<div class="emoji-card"><span class="big-emoji">{emoji}</span><p>{name}</p></div>\n'

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>🎨 Emoji Test Page</title>
        <style>
            body {{ font-family: 'Segoe UI Emoji', 'Apple Color Emoji', Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            h1 {{ text-align: center; font-size: 3em; }}
            .container {{ background: rgba(255, 255, 255, 0.95); color: #333; padding: 30px; border-radius: 10px; }}
            .emoji-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; margin: 30px 0; }}
            .emoji-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; transition: transform 0.3s; }}
            .emoji-card:hover {{ transform: scale(1.1); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
            .big-emoji {{ font-size: 4em; display: block; margin-bottom: 10px; }}
            .emoji-text {{ font-size: 2em; line-height: 1.8; margin: 20px 0; text-align: center; }}
            .sequences {{ background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            a {{ color: #2196f3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Emoji Heavy Content Test 🚀</h1>
            <p style="text-align: center; font-size: 1.2em;">Testing Unicode emoji support and rendering</p>

            <div class="emoji-text">
                🌟 Welcome to the emoji test page! 🎉<br>
                Let's see how well your crawler handles these: 🦄🌈✨<br>
                Some food emojis: 🍕🍔🍣🍰🍦🍪<br>
                Animals: 🐱🐶🐼🦁🐵🐸🦊<br>
                Weather: ☀️🌙⭐🌧️⛈️🌩️❄️
            </div>

            <h2>📊 Emoji Grid</h2>
            <div class="emoji-grid">
                {emoji_grid}
            </div>

            <div class="sequences">
                <h3>🔬 Complex Emoji Sequences</h3>
                <p>Family: 👨‍👩‍👧‍👦 (Man, Woman, Girl, Boy with ZWJ)</p>
                <p>Flags: 🇺🇸 🇬🇧 🇯🇵 🇫🇷 🇩🇪 🇮🇹 🇪🇸 (Regional Indicators)</p>
                <p>Skin Tones: 👋 👋🏻 👋🏼 👋🏽 👋🏾 👋🏿 (Fitzpatrick Modifiers)</p>
                <p>Gender Variants: 👨‍⚕️ 👩‍⚕️ 👨‍🍳 👩‍🍳 (ZWJ Sequences)</p>
                <p>Keycaps: 1️⃣ 2️⃣ 3️⃣ 🔟 (Combining Enclosing Keycap)</p>
            </div>

            <h2>🎯 Fun Emoji Sentences</h2>
            <p style="font-size: 1.3em; line-height: 2;">
                🌅 Good morning! ☕ Time for coffee and 💼 work.<br>
                📚 Reading a 📖 book by the 🌊 beach is 😌 relaxing.<br>
                🚗 Driving to the 🏔️ mountains for a 🏕️ camping trip! ⛺<br>
                🎂 Birthday party 🎉 with 🎈 balloons and 🎁 presents! 🥳<br>
                🌮 Taco Tuesday! 🍻 Let's celebrate with 🎊 confetti!
            </p>

            <p style="text-align: center; margin-top: 30px;">
                <a href="/">⬅️ Back to Home</a>
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/mismatch")
async def mismatch_page():
    """Content-Type mismatch test - declares UTF-8 but sends ISO-8859-1"""
    # Use only Latin-1 safe characters (no emoji or smart quotes)
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Content-Type Mismatch Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #fff3cd; }
            .warning { background: #f8d7da; border: 2px solid #dc3545; padding: 20px; border-radius: 5px; margin: 20px 0; }
            h1 { color: #dc3545; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Content-Type Mismatch Test</h1>
        <div class="warning">
            <h2>Warning: Encoding Mismatch!</h2>
            <p>This page declares <code>charset=utf-8</code> in the HTTP header but the content is actually encoded as <code>ISO-8859-1</code>.</p>
        </div>

        <h2>Test Characters</h2>
        <p>These characters may display incorrectly:</p>
        <ul>
            <li>French: café, crème, naïve</li>
            <li>German: Mädchen, Größe, Füße</li>
            <li>Spanish: niño, año, señor</li>
        </ul>

        <p>If your crawler properly detects encoding, it should notice this mismatch and handle it appropriately.</p>

        <p><a href="/">Back to Home</a></p>
    </body>
    </html>
    """
    try:
        # Declare UTF-8 in header but encode as ISO-8859-1
        return Response(content=html.encode('iso-8859-1', errors='replace'), media_type="text/html; charset=utf-8")
    except Exception as e:
        # Fallback to UTF-8 if encoding fails
        return HTMLResponse(content=html)

@app.get("/ja/")
async def japanese_page():
    """Japanese page with UTF-8 encoding and kanji characters"""
    html = """<!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>日本語ページ - Japanese Page</title>
        <style>
            body { font-family: 'Hiragino Kaku Gothic Pro', 'Meiryo', sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #fce4ec; }
            h1 { color: #c2185b; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            .section { margin: 20px 0; padding: 15px; background: #f3e5f5; border-left: 4px solid #9c27b0; }
            a { color: #7b1fa2; }
        </style>
    </head>
    <body>
        <h1>🗾 日本語テストページ</h1>
        <div class="content">
            <h2>こんにちは世界</h2>
            <p>これは日本語のテストページです。UTF-8エンコーディングと漢字文字のテストを行います。</p>

            <div class="section">
                <h3>📝 日本語の文字種</h3>
                <p><strong>ひらがな:</strong> あいうえお かきくけこ さしすせそ</p>
                <p><strong>カタカナ:</strong> アイウエオ カキクケコ サシスセソ</p>
                <p><strong>漢字:</strong> 日本語 東京 京都 大阪 富士山</p>
                <p><strong>ローマ字:</strong> Nihongo (Japanese)</p>
            </div>

            <div class="section">
                <h3>🌸 日本文化</h3>
                <p>日本は美しい国です。桜の花、富士山、伝統的な寺院や神社があります。</p>
                <p>日本料理は世界中で人気があります：寿司、ラーメン、天ぷら、刺身。</p>
                <p>伝統芸能：歌舞伎、能、茶道、華道、書道。</p>
            </div>

            <div class="section">
                <h3>🔢 数字とシンボル</h3>
                <p>アラビア数字: 0123456789</p>
                <p>漢数字: 一二三四五六七八九十百千万</p>
                <p>通貨: ¥ (円) | 価格: ¥1,000</p>
                <p>句読点: 、。「」『』</p>
            </div>

            <h3>📖 サンプルテキスト</h3>
            <p>吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。</p>
            <p style="font-style: italic;">— 夏目漱石「吾輩は猫である」より</p>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← ホームに戻る (Back to Home)</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/ar/")
async def arabic_page_alt():
    """Alternative route for Arabic page (UTF-8, RTL)"""
    return await arabic_page()

@app.get("/zh/")
async def chinese_page():
    """Chinese page with UTF-8 encoding and simplified Chinese characters"""
    html = """<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>中文页面 - Chinese Page</title>
        <style>
            body { font-family: 'Microsoft YaHei', 'SimHei', sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #e8f5e9; }
            h1 { color: #2e7d32; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            .section { margin: 20px 0; padding: 15px; background: #fff9c4; border-left: 4px solid #f57f17; }
            a { color: #558b2f; }
        </style>
    </head>
    <body>
        <h1>🇨🇳 中文测试页面</h1>
        <div class="content">
            <h2>你好世界</h2>
            <p>这是一个中文测试页面。本页面用于测试UTF-8编码和简体中文字符的显示。</p>

            <div class="section">
                <h3>📝 中文特点</h3>
                <p><strong>简体中文:</strong> 欢迎来到中国</p>
                <p><strong>繁体中文:</strong> 歡迎來到中國</p>
                <p><strong>拼音:</strong> Nǐ hǎo (Hello)</p>
                <p><strong>声调:</strong> 妈麻马骂 (mā má mǎ mà)</p>
            </div>

            <div class="section">
                <h3>🏮 中国文化</h3>
                <p>中国是一个拥有五千年历史的文明古国。长城、故宫、兵马俑是著名的历史遗迹。</p>
                <p>中国美食：北京烤鸭、四川火锅、广东点心、上海小笼包。</p>
                <p>传统节日：春节、中秋节、端午节、清明节。</p>
            </div>

            <div class="section">
                <h3>🔢 数字和符号</h3>
                <p>阿拉伯数字: 0123456789</p>
                <p>中文数字: 零一二三四五六七八九十百千万亿</p>
                <p>货币: ¥ (人民币) | 价格: ¥100.00</p>
                <p>标点符号: ，。、；：？！""''《》【】</p>
            </div>

            <h3>📖 示例文本</h3>
            <p>学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？</p>
            <p style="font-style: italic;">— 《论语·学而》</p>

            <h3>🌏 中国地理</h3>
            <p>主要城市：北京、上海、广州、深圳、成都、杭州、西安、南京、重庆、天津。</p>
            <p>著名景点：长江三峡、桂林山水、黄山、泰山、张家界。</p>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← 返回首页 (Back to Home)</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/he/")
async def hebrew_page_alt():
    """Alternative route for Hebrew page (UTF-8, RTL)"""
    return await hebrew_page()

@app.get("/de/")
async def german_page():
    """German page with UTF-8 encoding"""
    html = """<!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Deutsche Seite - German Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #fff8e1; }
            h1 { color: #f57c00; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            .section { margin: 20px 0; padding: 15px; background: #ffebee; border-left: 4px solid #d32f2f; }
            a { color: #d32f2f; }
        </style>
    </head>
    <body>
        <h1>🇩🇪 Deutsche Testseite</h1>
        <div class="content">
            <h2>Guten Tag</h2>
            <p>Dies ist eine deutsche Testseite für UTF-8-Kodierung und Sonderzeichen.</p>

            <div class="section">
                <h3>📝 Deutsche Sonderzeichen</h3>
                <p><strong>Umlaute:</strong> ä, ö, ü, Ä, Ö, Ü</p>
                <p><strong>Eszett:</strong> ß (scharfes S)</p>
                <p><strong>Wörter:</strong> Mädchen, Größe, Füße, Käse, Bäcker</p>
            </div>

            <div class="section">
                <h3>🏰 Deutsche Kultur</h3>
                <p>Deutschland ist bekannt für seine Schlösser, Bier und Würstchen.</p>
                <p>Berühmte Städte: Berlin, München, Hamburg, Köln, Frankfurt.</p>
            </div>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← Zurück zur Startseite</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/ru/")
async def russian_page():
    """Russian page with UTF-8 encoding"""
    html = """<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Русская страница - Russian Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #e1f5fe; }
            h1 { color: #0277bd; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            .section { margin: 20px 0; padding: 15px; background: #fff3e0; border-left: 4px solid #ef6c00; }
            a { color: #0277bd; }
        </style>
    </head>
    <body>
        <h1>🇷🇺 Русская тестовая страница</h1>
        <div class="content">
            <h2>Привет мир</h2>
            <p>Это русская тестовая страница для проверки кодировки UTF-8 и кириллицы.</p>

            <div class="section">
                <h3>📝 Русский алфавит</h3>
                <p><strong>Гласные:</strong> А Е Ё И О У Ы Э Ю Я</p>
                <p><strong>Согласные:</strong> Б В Г Д Ж З К Л М Н П Р С Т Ф Х Ц Ч Ш Щ</p>
                <p><strong>Другие:</strong> Ь Ъ</p>
            </div>

            <div class="section">
                <h3>🏛️ Русская культура</h3>
                <p>Россия - страна с богатой историей и культурой.</p>
                <p>Известные города: Москва, Санкт-Петербург, Казань, Сочи.</p>
            </div>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← Вернуться на главную</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/fr/")
async def french_page():
    """French page with UTF-8 encoding"""
    html = """<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Page française - French Page</title>
        <style>
            body { font-family: Georgia, serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #e8eaf6; }
            h1 { color: #3f51b5; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            .section { margin: 20px 0; padding: 15px; background: #f3e5f5; border-left: 4px solid #7b1fa2; }
            a { color: #3f51b5; }
        </style>
    </head>
    <body>
        <h1>🇫🇷 Page de test française</h1>
        <div class="content">
            <h2>Bonjour le monde</h2>
            <p>Ceci est une page de test française pour l'encodage UTF-8 et les caractères accentués.</p>

            <div class="section">
                <h3>📝 Caractères français</h3>
                <p><strong>Accents aigus:</strong> é, É</p>
                <p><strong>Accents graves:</strong> è, à, ù</p>
                <p><strong>Circonflexes:</strong> ê, â, î, ô, û</p>
                <p><strong>Tréma:</strong> ë, ï, ü</p>
                <p><strong>Cédille:</strong> ç, Ç</p>
                <p><strong>Mots:</strong> Café, crème, naïve, Noël</p>
            </div>

            <div class="section">
                <h3>🗼 Culture française</h3>
                <p>La France est célèbre pour sa cuisine, son vin et sa culture.</p>
                <p>Villes connues: Paris, Lyon, Marseille, Nice, Toulouse.</p>
            </div>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← Retour à l'accueil</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8", "Content-Language": "fr"})

@app.get("/en/")
async def english_page():
    """English page with UTF-8 encoding"""
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>English Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #e8f5e9; }
            h1 { color: #2e7d32; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            a { color: #2e7d32; }
        </style>
    </head>
    <body>
        <h1>English Test Page</h1>
        <div class="content">
            <h2>Welcome</h2>
            <p>This is an English test page for UTF-8 encoding validation.</p>
            <p>The quick brown fox jumps over the lazy dog.</p>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← Back to Home</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8", "Content-Language": "en"})

@app.get("/es/")
async def spanish_page():
    """Spanish page with UTF-8 encoding"""
    html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Página en español</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #fff3e0; }
            h1 { color: #e65100; text-align: center; }
            .content { background: white; padding: 20px; border-radius: 5px; line-height: 1.8; }
            a { color: #e65100; }
        </style>
    </head>
    <body>
        <h1>🇪🇸 Página de prueba en español</h1>
        <div class="content">
            <h2>Hola mundo</h2>
            <p>Esta es una página de prueba en español para validar la codificación UTF-8.</p>
            <p><strong>Caracteres especiales:</strong> ñ, á, é, í, ó, ú, ü, ¿, ¡</p>
            <p>Palabras: niño, año, señor, España</p>
        </div>
        <p style="margin-top: 20px; text-align: center;"><a href="/">← Volver al inicio</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8", "Content-Language": "es"})

@app.get("/mixed/")
async def mixed_language_page():
    """Mixed language content page"""
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mixed Language Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .language-block { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }
            a { color: #3498db; }
        </style>
    </head>
    <body>
        <h1>Mixed Language Content</h1>
        <div class="language-block" lang="en">
            <h2>English</h2>
            <p>This is English content.</p>
        </div>
        <div class="language-block" lang="es">
            <h2>Español</h2>
            <p>Este es contenido en español.</p>
        </div>
        <div class="language-block" lang="fr">
            <h2>Français</h2>
            <p>Ceci est du contenu en français.</p>
        </div>
        <div class="language-block" lang="ja">
            <h2>日本語</h2>
            <p>これは日本語のコンテンツです。</p>
        </div>
        <p style="margin-top: 20px;"><a href="/">← Back to Home</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/symbols/")
async def symbols_page():
    """Page with various symbols and emoji"""
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Symbols and Emoji</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .symbol-group { margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 5px; }
            a { color: #3498db; }
        </style>
    </head>
    <body>
        <h1>Symbols and Emoji Test</h1>
        <div class="symbol-group">
            <h2>Currency Symbols</h2>
            <p>$ € £ ¥ ₹ ₽ ₩ ₪</p>
        </div>
        <div class="symbol-group">
            <h2>Mathematical Symbols</h2>
            <p>± × ÷ ≠ ≤ ≥ ∞ √ ∑ ∏</p>
        </div>
        <div class="symbol-group">
            <h2>Emoji</h2>
            <p>😀 😃 😄 😁 😆 😅 🤣 😂 🙂 🙃 😉 😊</p>
            <p>🎉 🎊 🎈 🎁 🎀 🎂 🍰 🧁 🍪 🍩</p>
        </div>
        <p style="margin-top: 20px;"><a href="/">← Back to Home</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

@app.get("/search")
async def search_page():
    """Search page with query parameters"""
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Search Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            a { color: #3498db; }
        </style>
    </head>
    <body>
        <h1>Search Results</h1>
        <p>This page accepts query parameters for testing URL-encoded special characters.</p>
        <p style="margin-top: 20px;"><a href="/">← Back to Home</a></p>
    </body>
    </html>"""
    return HTMLResponse(content=html, headers={"Content-Type": "text/html; charset=UTF-8"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
