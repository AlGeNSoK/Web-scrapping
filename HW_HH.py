import json
import requests
from bs4 import BeautifulSoup
import fake_headers

def gen_headers():
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()

currency = "$"

main_response = requests.get("https://spb.hh.ru/search/vacancy?text=python+flask&area=1&area=2&items_on_page=20&"
                             "page=0", headers=gen_headers())
main_html_data = main_response.text
main_soup = BeautifulSoup(main_html_data, "lxml")
page_count = int(main_soup.find('div', attrs={"class": "pager"}).find_all("span", recursive=False)[-1].
                 find("a").find("span").text)
parsed_data = []

for page in range(page_count):
    response = requests.get(f"https://spb.hh.ru/search/vacancy?text=python+flask&area=1&area=2&items_on_page=20&"
                            f"page={page}", headers=gen_headers())
    html_data = response.text
    soup = BeautifulSoup(html_data, "lxml")
    vacancy_list_tag = soup.find_all("div", attrs={"class": "serp-item"})

    for vacancy_tag in vacancy_list_tag:
        a_tag = vacancy_tag.find('a', attrs={"class": "bloko-link"})
        title_tag = a_tag.find('span', attrs={"class": "serp-item__title"})
        company_tag = vacancy_tag.find('a', attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        city_tag = vacancy_tag.find('div', attrs={"data-qa": "vacancy-serp__vacancy-address"})
        salary_tag = vacancy_tag.find('span', attrs={"data-qa": "vacancy-serp__vacancy-compensation"})

        if title_tag is None or a_tag is None:
            continue

        header = title_tag.text.strip()
        link = a_tag['href']
        try:
            company = company_tag.text.strip().replace(" ", " ")
        except:
            company = ""
        try:
            city = city_tag.text.strip().replace(" ", " ")
        except:
            city = ""
        try:
            salary = salary_tag.text.replace("\u202f", " ")
        except:
            salary = ""

        if currency in salary:
            parsed_data.append({
                "header": header,
                "link": link,
                "company": company,
                "city": city,
                "salary": salary
            })

    with open("vacancy_data.json", "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4, ensure_ascii=False)

print(len(parsed_data))