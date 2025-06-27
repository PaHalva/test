import urllib3
from urllib3.contrib.socks import SOCKSProxyManager
import warnings
from bs4 import BeautifulSoup

# Отключаем предупреждения
warnings.filterwarnings("ignore")
urllib3.disable_warnings()

# Настройки прокси
PROXIES = [
    "socks5://195.91.129.101:1337",
    "socks5://176.195.72.70:1"
]


def get_schedule(payload):
    url = 'https://edu.str.uust.ru/php/getShedule.php'

    try:
        # Пробуем все прокси по очереди
        for proxy_url in PROXIES:
            try:
                print(f"Пробуем подключиться через {proxy_url}...")

                proxy = SOCKSProxyManager(
                    proxy_url,
                    timeout=15,
                    retries=urllib3.Retry(2))

                response = proxy.request(
                    "POST",
                    url,
                    fields=payload,
                    headers={
                        'User-Agent': 'Mozilla/5.0'
                    }
                )

                if response.status == 200:
                    print("Успешное подключение!")
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
                    days = soup.find_all('div', class_='day')

                    if not days:
                        return "Нет данных на эту неделю"

                    result = []
                    for day in days:
                        day_name = day.find('h2').get_text(strip=True)
                        lessons = day.find_all('li', class_='lesson')

                        day_schedule = []
                        for lesson in lessons:
                            num = lesson.find('div', class_='number').get_text(strip=True)
                            name = lesson.find('div', class_='name').get_text(strip=True) if lesson.find('div',
                                                                                                         class_='name') else ""
                            time_ = lesson.find('div', class_='time').get_text(strip=True) if lesson.find('div',
                                                                                                          class_='time') else ""
                            cab = lesson.find('div', class_='cab')
                            cab_text = ', '.join([li.get_text(strip=True) for li in cab.find_all('li')]) if cab else ""

                            day_schedule.append(f"{num}. {name} ({time_}) - Каб: {cab_text}")

                        result.append(f"{day_name}:\n" + "\n".join(day_schedule))

                    return "\n\n".join(result)

            except Exception as e:
                print(f"Ошибка с прокси {proxy_url}: {str(e)[:100]}...")
                continue

        return "Не удалось подключиться через прокси"

    except Exception as e:
        print(f"Общая ошибка: {e}")
        return "Ошибка при получении расписания"


# Пример использования
if __name__ == "__main__":
    schedule = get_schedule({
        'type': 2,
        'id': 10385,
        'week': 0
    })

    print("\n=== Расписание ===")
    print(schedule)