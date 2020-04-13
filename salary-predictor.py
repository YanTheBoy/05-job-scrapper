import requests
from terminaltables import AsciiTable
from itertools import count


def get_response_from_hh(prog_language):
    data_for_all_vacancies = []
    url = 'https://api.hh.ru/vacancies'
    for page in count(0):
        params = {
            'text': 'NAME:({})'.format(prog_language),  # strict requirement for job name
            'area': '1',
            'period': '30',
            'only_with_salary': 'True',
            'page': page,
            'per_page': '100'
        }

        page_response = requests.get(url, params=params)
        page_data = page_response.json()
        data_for_all_vacancies = data_for_all_vacancies + page_data['items']
        if page >= page_data['pages']-1:
            break
    return data_for_all_vacancies


def get_salary_data_hh(all_vacancies_data):
    jobs_salary_data = []
    for vacancy_data in all_vacancies_data:
        jobs_salary_data.append(vacancy_data['salary'])
    return jobs_salary_data


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


def get_response_from_superjob(programming_language):
    api_app_id = 'v3.r.132210005.c41212ae279030508ca55841058cf52f9bccc0ff.5d64230d7fd9c48069d3260b0f3cca85b9266cf1'
    data_for_all_vacancies = []
    url = 'https://api.superjob.ru/2.30/vacancies/'

    for page in count(0):
        params = {
            'page': page,
            'count': '100',
            'town': '4',    # id4 for Moscow
            'no_agreement': '1',    # not show vacancies without salary
            'catalogues[]': '48',    # professional code id
            'keywords[srws][]': '1',    # keywords find only in vacancy name
            'keywords[keys][]': programming_language
        }

        page_response = requests.get(url, headers={'X-Api-App-Id': api_app_id}, params=params)
        page_data = page_response.json()
        data_for_all_vacancies = data_for_all_vacancies + page_data['objects']
        if page_data['more'] is False:
            break

    return list(filter(None, data_for_all_vacancies))


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


def create_table_data(jobs_data):
    table_data = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for program_lang, salaries in jobs_data.items():
        table_data.append([
            program_lang,
            salaries['vacancies_found'],
            salaries['vacancies_processed'],
            salaries['average_salary']
        ]
        )
    return table_data


if __name__ == '__main__':
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

    sj_salary_data = {}    # create dicts for final salary data
    hh_salary_data = {}    # -//-

    for language in programming_languages:
        sj_vacancies_data = get_response_from_superjob(language)
        sj_salary_range = predict_rub_salary_sj(sj_vacancies_data)    # get salary list
        sj_salary_data[language] = get_average_salary(sj_salary_range)

        hh_vacancies_data = get_response_from_hh(language)
        hh_salary_range = get_salary_data_hh(hh_vacancies_data)    # get salary list
        hh_expected_salary = predict_rub_salary_hh(hh_salary_range)
        hh_salary_data[language] = get_average_salary(hh_expected_salary)

    salary_data_for_table_sj = create_table_data(sj_salary_data)    # create data for table
    salary_data_for_table_hh = create_table_data(hh_salary_data)    # -//-

    sj_table_instance = AsciiTable(salary_data_for_table_sj, title='SuperJob Moscow')
    hh_table_instance = AsciiTable(salary_data_for_table_hh, title='HeadHunter Moscow')

    print(sj_table_instance.table)
    print(hh_table_instance.table)
