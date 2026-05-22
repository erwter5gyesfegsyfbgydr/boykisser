import os
import requests
from bs4 import BeautifulSoup

# Фиксированный фиолетовый для баннера и заголовков источников
PURPLE = "\033[38;2;179;102;255m"
RESET = "\033[0m"


def clear_console():
    """Очищает консоль в зависимости от операционной системы."""
    os.system("cls" if os.name == "nt" else "clear")


def get_gradient_color(step, total_steps):
    """Генерирует ANSI-код для градиента от фиолетового к белому."""
    # Светло-фиолетовый: #B366FF (179, 102, 255)
    start_r, start_g, start_b = 179, 102, 255
    # Белый: #FFFFFF (255, 255, 255)
    end_r, end_g, end_b = 255, 255, 255

    if total_steps <= 1:
        return f"\033[38;2;{start_r};{start_g};{start_b}m"

    # Интерполяция цветов
    r = int(start_r + (end_r - start_r) * (step / (total_steps - 1)))
    g = int(start_g + (end_g - start_g) * (step / (total_steps - 1)))
    b = int(start_b + (end_b - start_b) * (step / (total_steps - 1)))

    return f"\033[38;2;{r};{g};{b}m"


def parse_getscam(phone_number, headers):
    """Парсинг первого сайта (getscam.com)"""
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
    """Парсинг второго сайта (кто-звонил.рф)"""
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
    """Парсинг третьего сайта (mysmsbox.ru)"""
    url = f"https://mysmsbox.ru/phone-search/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        result = {}

        # 1. Парсинг категорий звонка
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

        # 2. Парсинг оценок/рекомендаций
        rating_p = None
        for p in soup.find_all("p"):
            if p.get_text().strip().startswith("Оценки"):
                rating_p = p
                break
        
        if rating_p:
            result["rating"] = rating_p.get_text(" ", strip=True)

        # 3. Парсинг отзывов
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


def main():
    clear_console()

    # Фиолетовый баннер
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
⠀⠀⠀⠀⠀⠀⠀⠀⠘⢧⡈⡿⣄⣀⣀⣀⣀⣀⣈⣳⣍⠉⠉⠛⢿⡛⢦⡼⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠻⠶⠿⠿⠷⠷⠿⠿⠾⠶⠶⠶⠶⠿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
{RESET}
    """
    print(banner)

    phone_number = input("enter phone >> ").strip()
    if not phone_number:
        print("Номер не может быть пустым.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"\nЗагрузка данных для номера {phone_number}...")
    
    scam_data = parse_getscam(phone_number, headers)
    reviews_data = parse_reviews_site(phone_number, headers)
    smsbox_data = parse_mysmsbox(phone_number, headers)

    if not scam_data and not reviews_data and not smsbox_data:
        print("Информация по номеру не найдена ни на одном из сайтов.")
        return

    # Подсчитываем общее число строк результатов для правильного шага градиента
    total_lines = 0
    if scam_data:
        total_lines += len(scam_data)
    if reviews_data:
        # Для второго источника считаем заголовок отзыва и текст (если он есть) как отдельные строки
        for r in reviews_data:
            total_lines += 2 if r['text'] else 1
    if smsbox_data:
        if "categories" in smsbox_data: total_lines += 1
        if "rating" in smsbox_data: total_lines += 1
        if "comments" in smsbox_data: total_lines += 1 + len(smsbox_data["comments"])

    current_step = 0

    # --- Источник 1: GetScam ---
    print(f"\n{PURPLE}=== ИСТОЧНИК 1: getscam.com ==={RESET}")
    if scam_data:
        for field, value in scam_data:
            color = get_gradient_color(current_step, total_lines)
            separator = ":" if field == "Тип" else " ->"
            print(f"{color}[+] {field}{separator} {value}{RESET}")
            current_step += 1
    else:
        print("Нет данных на этом сайте.")

    # --- Источник 2: Кто-звонил.рф ---
    print(f"\n{PURPLE}=== ИСТОЧНИК 2: кто-звонил.рф ==={RESET}")
    if reviews_data:
        for review in reviews_data:
            color = get_gradient_color(current_step, total_lines)
            print(f"{color}[+] Отзыв ({review['date']}) | Автор: {review['name']} -> Категория: {review['badge']}{RESET}")
            current_step += 1
            
            if review['text']:
                color = get_gradient_color(current_step, total_lines)
                print(f"{color}    Текст: {review['text']}{RESET}")
                current_step += 1
    else:
        print("Отзывы на этом сайте не найдены.")

    # --- Источник 3: MySmsBox ---
    print(f"\n{PURPLE}=== ИСТОЧНИК 3: mysmsbox.ru ==={RESET}")
    if smsbox_data:
        if "categories" in smsbox_data:
            color = get_gradient_color(current_step, total_lines)
            print(f"{color}[+] Вероятная категория звонка -> {smsbox_data['categories']}{RESET}")
            current_step += 1
        
        if "rating" in smsbox_data:
            color = get_gradient_color(current_step, total_lines)
            print(f"{color}[+] Вердикт -> {smsbox_data['rating']}{RESET}")
            current_step += 1
            
        if "comments" in smsbox_data:
            color = get_gradient_color(current_step, total_lines)
            print(f"{color}[+] Отзывы пользователей:{RESET}")
            current_step += 1
            for comment in smsbox_data["comments"]:
                color = get_gradient_color(current_step, total_lines)
                print(f"{color}    - {comment}{RESET}")
                current_step += 1
    else:
        print("Нет данных на этом сайте.")


if __name__ == "__main__":
    main()
