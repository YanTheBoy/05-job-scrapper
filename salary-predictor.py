import requests
from terminaltables import AsciiTable
from itertools import count
import os
from dotenv import load_dotenv


def get_response_hh(programming_language):
    hh_vacancies_substance = []
    url = 'https://api.hh.ru/vacancies'
    for page in count(0):
        params = {
            'text': 'NAME:({})'.format(programming_language),
            'area': '1',
            'period': '30',
            'only_with_salary': 'True',
            'page': page,
            'per_page': '100'
        }

        page_response = requests.get(url, params=params)
        page_content = page_response.json()
        hh_vacancies_substance = hh_vacancies_substance + page_content['items']
        if page >= page_content['pages']-1:
            break
    return hh_vacancies_substance


def get_salaries_hh(all_vacancies):
    jobs_salary = []
    for vacancy in all_vacancies:
        jobs_salary.append(vacancy['salary'])
    return jobs_salary


def predict_rub_salary_hh(salary_range):
    prediction_salary = []
    if not salary_range:
        return None
    for vacancy in salary_range:
        salary_from = vacancy['from']
        salary_to = vacancy['to']
        currency = vacancy['currency']
        rub_salary = predict_salary(salary_from, salary_to, currency)
        prediction_salary.append(rub_salary)
    return prediction_salary


def get_response_superjob(programming_language, application_id):
    app_id = application_id
    sj_vacancies_substance = []
    url = 'https://api.superjob.ru/2.30/vacancies/'

    for page in count(0):
        params = {
            'page': page,
            'count': '100',
            'town': '4',
            'no_agreement': '1',
            'catalogues[]': '48',
            'keywords[srws][]': '1',
            'keywords[keys][]': programming_language
        }

        page_response = requests.get(url, headers={'X-Api-App-Id': app_id}, params=params)
        page_content = page_response.json()
        sj_vacancies_substance = sj_vacancies_substance + page_content['objects']
        if page_content['more'] is False:
            break

    return list(filter(None, sj_vacancies_substance))


def predict_rub_salary_sj(salary_range):
    prediction_salary = []
    if not salary_range:
        return None
    for vacancy in salary_range:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        currency = vacancy['currency']
        rub_salary = predict_salary(salary_from, salary_to, currency)
        prediction_salary.append(rub_salary)
    return prediction_salary


def predict_salary(salary_from, salary_to, currency):
    if currency != 'rub' and currency != 'RUR':
        return None
    elif salary_from is None or salary_from == 0:
        return int(salary_to * 0.8)
    elif salary_to is None or salary_to == 0:
        return int(salary_from * 1.2)
    else:
        return int((salary_from + salary_to) / 2)


def get_average_salary(expected_salary):
    if expected_salary is None:
        return {
            'vacancies_found': 0,
            'vacancies_processed': 0,
            'average_salary': 0
        }
    salary_without_none = list(filter(None, expected_salary))
    vacancies_processed = len(salary_without_none)
    average_salary = sum(salary_without_none)/vacancies_processed
    return {
        'vacancies_found': len(expected_salary),
        'vacancies_processed': vacancies_processed,
        'average_salary': int(average_salary)
    }


def create_table(jobs_payroll):
    table = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for program_lang, salaries in jobs_payroll.items():
        table.append([
            program_lang,
            salaries['vacancies_found'],
            salaries['vacancies_processed'],
            salaries['average_salary']
        ]
        )
    return table


if __name__ == '__main__':
    load_dotenv()
    api_app_id = os.getenv('SUPERJOB_API_APP_ID')
    programming_languages = [
        '1C',
        'Java',
        'Javascript',
        'Python',
        'C++',
        'C#',
        'PHP',
        'Swift',
        'Scala'
    ]

    sj_predict_salary = {}
    hh_predict_salary = {}

    for language in programming_languages:
        sj_vacancies_description = get_response_superjob(language, api_app_id)
        sj_salary_range = predict_rub_salary_sj(sj_vacancies_description)
        sj_predict_salary[language] = get_average_salary(sj_salary_range)

        hh_vacancies_description = get_response_hh(language)
        hh_salary_range = get_salaries_hh(hh_vacancies_description)
        hh_expected_salary = predict_rub_salary_hh(hh_salary_range)
        hh_predict_salary[language] = get_average_salary(hh_expected_salary)

    sj_tabla_filling = create_table(sj_predict_salary)
    hh_table_filling = create_table(hh_predict_salary)

    sj_table_instance = AsciiTable(sj_tabla_filling, title='SuperJob Moscow')
    hh_table_instance = AsciiTable(hh_table_filling, title='HeadHunter Moscow')

    print(sj_table_instance.table)
    print(hh_table_instance.table)
