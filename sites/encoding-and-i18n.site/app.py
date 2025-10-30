from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from faker import Faker
import random

app = FastAPI()

# Initialize Faker for different locales
fake_en = Faker('en_US')
fake_ar = Faker('ar_SA')
fake_he = Faker('he_IL')

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
        <h1>☕ Café de Paris</h1>
        <p><strong>Adresse:</strong> {address}</p>
        <h2>Menu du Jour</h2>
        <div class="menu-item">
            <span class="price">€8.50</span>
            <strong>Café au lait</strong><br>
            Café noir mélangé avec du lait chaud et mousseux
        </div>
        <div class="menu-item">
            <span class="price">€12.00</span>
            <strong>Crêpe Française</strong><br>
            Crêpe traditionnelle avec confiture de fraises et crème fraîche
        </div>
        <div class="menu-item">
            <span class="price">€6.50</span>
            <strong>Croissant Beurré</strong><br>
            Croissant frais avec beurre de Normandie
        </div>
        <div class="menu-item">
            <span class="price">€15.00</span>
            <strong>Spécialité du Chef</strong><br>
            Soufflé au fromage avec salade niçoise
        </div>
        <p style="margin-top: 30px; font-style: italic;">
            «La vie est trop courte pour boire du mauvais café!» - Napoléon
        </p>
        <p><a href="/">← Retour à l'accueil</a></p>
    </body>
    </html>
    """
    # Return with ISO-8859-1 encoding
    return Response(content=html.encode('iso-8859-1'), media_type="text/html; charset=iso-8859-1")

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
        <h1>⚠️ Content-Type Mismatch Test</h1>
        <div class="warning">
            <h2>Warning: Encoding Mismatch!</h2>
            <p>This page declares <code>charset=utf-8</code> in the HTTP header but the content is actually encoded as <code>ISO-8859-1</code>.</p>
        </div>

        <h2>Test Characters</h2>
        <p>These characters may display incorrectly:</p>
        <ul>
            <li>Euro sign: €</li>
            <li>French: café, crème, naïve</li>
            <li>German: Mädchen, Größe, Füße</li>
            <li>Spanish: niño, año, señor</li>
            <li>Quotes: "smart quotes" and 'apostrophes'</li>
        </ul>

        <p>If your crawler properly detects encoding, it should notice this mismatch and handle it appropriately.</p>

        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    # Declare UTF-8 in header but encode as ISO-8859-1
    return Response(content=html.encode('iso-8859-1'), media_type="text/html; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5009)
