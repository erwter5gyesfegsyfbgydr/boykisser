import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*")

import os
import sys
import subprocess

SPINNER = ["/", "-", "\\"]
MODULES = ["requests", "bs4"]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def spinner_animation(duration=1.0):
    import time
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(SPINNER[i % len(SPINNER)])
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\b")
        i += 1

def check_modules():
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)
        has_colorama = True
    except ImportError:
        has_colorama = False
        print("colorama not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "-q"])
        from colorama import init, Fore, Style
        init(autoreset=True)
        has_colorama = True

    clear()
    missing_modules = []

    for module in MODULES:
        prefix = "Checking module >> "
        for char in prefix:
            sys.stdout.write(char)
            sys.stdout.flush()
            import time
            time.sleep(0.01)

        for char in module:
            if has_colorama:
                sys.stdout.write(Fore.MAGENTA + char)
            else:
                sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)

        sys.stdout.write(" ")
        sys.stdout.flush()

        spinner_animation(0.7)

        try:
            __import__(module)
            print("[ OK ]")
        except ImportError:
            if has_colorama:
                print(Fore.RED + "[ MISSING ]")
            else:
                print("[ MISSING ]")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n\nMissing modules detected: {', '.join(missing_modules)}")
        print("Installing missing modules...")
        for module in missing_modules:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module, "-q"])
                print(f"  [+] {module} installed successfully")
            except Exception as e:
                print(f"  [!] Failed to install {module}: {e}")
                print(f"\nPlease install manually: pip install {' '.join(missing_modules)}")
                input("\nPress Enter to exit...")
                sys.exit(1)
        print("\nAll modules installed successfully!")
        input("\nPress Enter to continue...")
    else:
        print("\nModule checking completed")
        input('To continue press "Enter" >> ')

check_modules()

import re
import time
import requests
from bs4 import BeautifulSoup

PURPLE = "\u001b[38;2;179;102;255m"
RESET = "\u001b[0m"
b = "\u001b[1m"
under = "\u001b[4m"

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def parse_htmlweb(phone_number):
    url = f"https://htmlweb.ru/geo/api.php?json&telcod={phone_number}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None

def parse_getscam(phone_number, headers):
    url = f"https://getscam.com/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="top__info-item")
        if not table:
            return None

        target_fields = [
            "Номер", "Язык устройства", "Состояние", "Тип", 
            "IP адрес", "Сайт оператора", "Оператор", "Код", 
            "Страна", "Город"
        ]

        cells = table.find_all("td")
        parsed_data = {}
        for cell in cells:
            p_tag = cell.find("p", class_="grey")
            span_tag = cell.find("span")
            if p_tag and span_tag:
                title = p_tag.get_text(strip=True)
                value = span_tag.get_text(strip=True)
                if title in target_fields:
                    parsed_data[title] = value

        return [(field, parsed_data[field]) for field in target_fields if field in parsed_data]
    except Exception:
        return None

def parse_reviews_site(phone_number, headers):
    url = f"https://xn---7-elctgilofd3b.xn--p1ai/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        review_headers = soup.find_all("div", class_="review-header")

        reviews_list = []
        for header in review_headers:
            name_tag = header.find("span", class_="review-name")
            date_tag = header.find("span", class_="review-date")
            badge_tag = header.find("div", class_="review-rating-badge")

            name = name_tag.get_text(strip=True) if name_tag else "Аноним"
            date = date_tag.get_text(strip=True) if date_tag else "Не указана"
            badge = badge_tag.get_text(strip=True) if badge_tag else "Без категории"

            text_tag = header.find_next_sibling("p", class_="review-text")
            text = text_tag.get_text(strip=True) if text_tag else None

            reviews_list.append({
                "name": name,
                "date": date,
                "badge": badge,
                "text": text
            })

        return reviews_list
    except Exception:
        return None

def parse_mysmsbox(phone_number, headers):
    url = f"https://mysmsbox.ru/phone-search/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        result = {}

        categories_ul = soup.find("ul", class_="blog-tags")
        if categories_ul:
            categories = []
            for li in categories_ul.find_all("li"):
                a_tag = li.find("a")
                badge_tag = li.find("span", class_="badge-for-button")
                if a_tag:
                    cat_name = a_tag.get_text(strip=True)
                    votes = badge_tag.get_text(strip=True) if badge_tag else "0"
                    categories.append(f"{cat_name} ({votes})")
            if categories:
                result["categories"] = ", ".join(categories)

        rating_p = None
        for p in soup.find_all("p"):
            if p.get_text().strip().startswith("Оценки"):
                rating_p = p
                break

        if rating_p:
            result["rating"] = rating_p.get_text(" ", strip=True)

        comments_div = soup.find("div", class_="item-list")
        if comments_div:
            comments = []
            for li in comments_div.find_all("li", class_="comment"):
                comments.append(li.get_text(strip=True))
            if comments:
                result["comments"] = comments

        return result if result else None
    except Exception:
        return None

def parse_whatsapp(phone_number, headers):
    url = f"https://umnico.com/api/tools/checker?phone={phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("exists", False)
        return False
    except Exception:
        return False

def parse_leakcheck(phone_number, headers):
    url = f"https://leakcheck.io/api/public?check={phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def generate_html_report(phone_number, htmlweb_data, scam_data, reviews_data, smsbox_data, whatsapp_exists, leakcheck_data):
    htmlweb_html = ""
    if htmlweb_data:
        country = htmlweb_data.get("country", {})
        region = htmlweb_data.get("region", {})
        city = htmlweb_data.get("0", {})
        capital = htmlweb_data.get("capital", {})
        telcod = htmlweb_data.get("country_telcod", "")
        phone_body = phone_number.lstrip(str(telcod))

        htmlweb_html += f'<div class="data-line"><span class="label">Номер:</span> <span class="value">+{telcod}{phone_body}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Страна:</span> <span class="value">{country.get("name", "")} ({country.get("english", "")})</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Регион:</span> <span class="value">{region.get("name", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Округ:</span> <span class="value">{htmlweb_data.get("okrug", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Город:</span> <span class="value">{city.get("name", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Оператор:</span> <span class="value">{city.get("oper_brand", "")} ({city.get("oper", "")})</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Мобильный:</span> <span class="value">{"Да" if city.get("mobile") else "Нет"}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Часовой пояс:</span> <span class="value">{htmlweb_data.get("tz", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Координаты:</span> <span class="value">{city.get("latitude", "")}, {city.get("longitude", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Столица:</span> <span class="value">{capital.get("name", "")}</span></div>'
        htmlweb_html += f'<div class="data-line"><span class="label">Диапазон:</span> <span class="value">{city.get("def", "")}</span></div>'
    else:
        htmlweb_html = '<div class="data-line"><span class="value">Нет данных на этом сайте.</span></div>'

    scam_html = ""
    if scam_data:
        for field, value in scam_data:
            scam_html += f'<div class="data-line"><span class="label">{field}:</span> <span class="value">{value}</span></div>'
    else:
        scam_html = '<div class="data-line"><span class="value">Нет данных на этом сайте.</span></div>'

    reviews_html = ""
    if reviews_data:
        for r in reviews_data:
            text_str = f'<span class="label">Текст:</span> <span class="value">{r.get("text", "")}</span>' if r.get('text') else ''
            reviews_html += f"""
            <div class="data-line" style="margin-bottom: 12px; border-bottom: 1px solid #2a2a2a; padding-bottom: 8px;">
                <span class="label">Автор:</span> <span class="value">{r['name']} ({r['date']})</span><br>
                <span class="label">Категория:</span> <span class="value">{r['badge']}</span><br>
                {text_str}
            </div>
            """
    else:
        reviews_html = '<div class="data-line"><span class="value">Отзывы на этом сайте не найдены.</span></div>'

    smsbox_html = ""
    if smsbox_data:
        if "categories" in smsbox_data:
            smsbox_html += f'<div class="data-line"><span class="label">Категории:</span> <span class="value">{smsbox_data["categories"]}</span></div>'
        if "rating" in smsbox_data:
            smsbox_html += f'<div class="data-line"><span class="label">Вердикт:</span> <span class="value">{smsbox_data["rating"]}</span></div>'

        if "comments" in smsbox_data and smsbox_data["comments"]:
            comments_list = [f"- {comment.strip()}" for comment in smsbox_data["comments"] if comment.strip()]
            comments_str = "<br>".join(comments_list)
            smsbox_html += f'<div class="data-line"><span class="label">Комментарии:</span><br><span class="value">{comments_str}</span></div>'
    else:
        smsbox_html = '<div class="data-line"><span class="value">Нет данных на этом сайте.</span></div>'

    whatsapp_status = "Зарегистрирован" if whatsapp_exists else "Не зарегистрирован"
    whatsapp_html = f'<div class="data-line"><span class="label">Статус:</span> <span class="value">{whatsapp_status}</span></div>'

    leakcheck_html = ""
    if leakcheck_data and leakcheck_data.get("success"):
        sources = leakcheck_data.get("sources", [])
        found_databases_count = len(sources)
        leakcheck_html += f'<div class="data-line" style="margin-bottom: 15px;"><span class="label">Всего найдено баз с утечками:</span> <span class="value" style="color: #bb86fc; font-weight: bold;">{found_databases_count}</span></div>'

        if sources:
            leakcheck_html += '<div class="label" style="margin-bottom: 8px; font-weight: bold;">Источники (База и Дата):</div>'
            for src in sources:
                name = src.get("name", "Неизвестно")
                date = src.get("date", "Не указана")
                if not date:
                    date = "Не указана"
                leakcheck_html += f"""
                <div class="data-line" style="margin-bottom: 6px; padding-left: 10px; border-left: 2px solid #9b51e0;">
                    <span class="label">База:</span> <span class="value">{name}</span> | <span class="label">Дата:</span> <span class="value">{date}</span>
                </div>
                """
        else:
            leakcheck_html += '<div class="data-line"><span class="value">Конкретные источники не указаны.</span></div>'
    else:
        leakcheck_html = '<div class="data-line"><span class="value">Данные в базах утечек не обнаружены или ошибка API.</span></div>'

    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по номеру {phone_number}</title>
    <style>
        body {{
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
        }}
        h1 {{
            color: #ffffff;
            text-align: center;
            margin-bottom: 30px;
            font-size: 24px;
            letter-spacing: 1px;
        }}
        .phone-number {{
            color: #9b51e0;
            font-weight: bold;
        }}
        .masonry-wrapper {{
            column-count: 2;
            column-gap: 20px;
            width: 100%;
        }}
        @media (max-width: 768px) {{
            .masonry-wrapper {{
                column-count: 1;
            }}
        }}
        .source-block {{
            background-color: #1e1e1e;
            border: 2px solid #9b51e0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(155, 81, 224, 0.05);
            margin-bottom: 20px;
            break-inside: avoid;
            display: inline-block;
            width: 100%;
            box-sizing: border-box;
        }}
        .source-title {{
            color: #bb86fc;
            font-size: 18px;
            margin-top: 0;
            margin-bottom: 15px;
            border-bottom: 1px solid #333;
            padding-bottom: 8px;
            text-transform: lowercase;
            letter-spacing: 0.5px;
        }}
        .data-line {{
            margin: 10px 0;
            font-size: 14px;
            line-height: 1.5;
        }}
        .label {{
            color: #a0a0a0;
        }}
        .value {{
            color: #e0e0e0;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Сводный отчет по номеру: <span class="phone-number">{phone_number}</span></h1>
        <div class="masonry-wrapper">
            <div class="source-block">
                <div class="source-title">htmlweb.ru</div>
                {htmlweb_html}
            </div>
            <div class="source-block">
                <div class="source-title">getscam.com</div>
                {scam_html}
            </div>
            <div class="source-block">
                <div class="source-title">mysmsbox.ru</div>
                {smsbox_html}
            </div>
            <div class="source-block">
                <div class="source-title">кто-звонил.рф</div>
                {reviews_html}
            </div>
            <div class="source-block">
                <div class="source-title">WhatsApp</div>
                {whatsapp_html}
            </div>
            <div class="source-block">
                <div class="source-title">leakcheck.io</div>
                {leakcheck_html}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_template


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        clear_console()

        banner = f"""{PURPLE}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠛⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠛⢠⡀⠸⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⡁⢰⣋⡇⠀⡿⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⣏⠉⠛⠳⢤⣟⠀⢧⠀⠀⣀⣤⣠⣤⣄⣀⠀⠀⢷⠀⠀⠈⠙⠢⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡔⠃⣀⠘⢆⣀⠀⠀⠉⠀⠘⠚⠉⠀⠀⢀⡀⠀⢸⠇⣀⢸⡀⠀⠀⠀⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠙⡾⠟⣷⠂⠉⠀⠀⠀⠀⠀⠀⠀⢶⢚⣹⠃⢠⡏⠀⡏⠹⠃⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣼⠇⣰⠀⠀⠀⠠⠶⠳⣦⠀⠀⠀⠘⠲⠃⢠⠟⠁⠀⡏⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⡟⠷⠟⠁⠀⠀⣴⡆⠀⢸⡇⠀⠀⢠⣄⡴⠏⠀⡀⢰⠇⠀⠀⠀⠀⠀⠀⢠⡾⠚⠋⠉⠉⢳⡀⠀⠀⠀⠀⠀
⠀⢹⡌⠙⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢧⡐⠶⠄⠀⠀⠻⣃⡀⠸⡷⠀⠀⠀⠹⣆⠀⢀⡿⡏⠀⠀⠀⠀⠀⠀⣠⡾⠀⠀⠀⢀⡴⠟⠁⠀⠀⠀⠀⠀
⠀⠀⢷⠀⠀⠻⣷⣄⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠙⠦⣤⣀⡀⠀⠘⠿⠇⠀⣤⠴⣶⣞⣁⣠⣾⡀⠀⠀⣤⣠⣴⠶⢾⣁⣧⠀⠀⠀⠈⢧⡤⠖⠚⠦⣄⡀⠀
⠀⠀⠘⡇⠀⠀⠈⠻⣷⡀⠀⠀⣠⢾⡉⢉⡍⠙⠳⣶⢟⣯⣭⠿⠷⣤⡀⣠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⠚⠻⠀⠀⠀⠀⠈⣇⠀⠀⠀⠀⠙⣦
⠀⠀⠀⢹⡀⠀⠀⠀⢿⣧⠀⠀⢧⣸⡀⠘⣇⣴⠀⠀⢘⠛⠛⠀⣰⠊⠻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣤⣄⣄⡓⣶⠏
⠀⠀⠀⠀⣧⠀⠀⠀⠈⣿⣆⣠⣤⣭⡭⠿⣹⣿⡋⠉⠛⠓⠒⠴⠃⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣇⠈⠙⠛⠁⠀
⠀⠀⠀⠀⠈⠳⣄⠀⠀⠸⣿⠉⠀⠈⢻⠞⠙⡾⠁⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣀⣀⣀⣀⣀⣀⣀⣬⠷⠶⠤⢤⣤⣄⣀⣀⣤⣄⡀⣰⠤⢽⠆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀⢿⣧⠀⠀⠘⠷⠾⠷⣼⣅⣀⣀⠀⠀⠀⠀⠀⠀⠸⡅⠀⠀⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⢧⡈⡿⣄⣀⣀⣀⣀⣀⣀⣈⣳⣍⠉⠉⠛⢿⡛⢦⡼⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠻⠶⠿⠿⠷⠷⠿⠿⠾⠶⠶⠶⠶⠿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

          ┌──────────────────────────────────────┐
          │ {RESET}{b}{under}info / информация{RESET}{PURPLE}                    │
          │ Dev -> @BrutXray & @waruma           │
          │ Version -> alpha 0.0.4               │
          │ Channel -> t.me/BoykisserLinks       │
          └──────────────────────────────────────┘{RESET}
    """

        print(banner)

        phone_number = input(f"{PURPLE} enter phone{RESET} (или '{PURPLE}exit{RESET}' для выхода) >> ").strip()

        if phone_number.lower() in ['exit', 'quit', 'выход']:
            print("Выход из программы...")
            break

        if not phone_number:
            print("Номер не может быть пустым.")
            input("\nНажмите Enter для продолжения...")
            continue

        print(f"""\n┌───────────────────────────────────┐
│{PURPLE} Идет поиск... Пожалуйста ожидайте {RESET}│
└───────────────────────────────────┘""")

        htmlweb_data = parse_htmlweb(phone_number)
        scam_data = parse_getscam(phone_number, headers)
        reviews_data = parse_reviews_site(phone_number, headers)
        smsbox_data = parse_mysmsbox(phone_number, headers)
        whatsapp_exists = parse_whatsapp(phone_number, headers)
        leakcheck_data = parse_leakcheck(phone_number, headers)

        html_content = generate_html_report(
            phone_number, htmlweb_data, scam_data, reviews_data, smsbox_data, whatsapp_exists, leakcheck_data
        )

        safe_filename = re.sub(r'[^\w\s-]', '', phone_number).replace(' ', '_')
        if not safe_filename:
            safe_filename = "report"
        filename = f"report_{safe_filename}.html"

        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"\n{PURPLE}[+] Успешно! Данные сохранены в файл: {RESET}{filename}")
        except Exception as e:
            print(f"\nОшибка при создании HTML-файла: {e}")

        input(f"\n\n{PURPLE}Нажмите Enter для продолжения и нового поиска...{RESET}")


if __name__ == "__main__":
    main()
