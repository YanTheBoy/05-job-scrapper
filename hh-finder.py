import requests
import json

def get_response(programming_languages):
    url = 'https://api.hh.ru/vacancies'

    for lang in programming_languages:
        params = {
            'text': 'NAME:({})'.format(lang),
            'area': '1',
            'period': '30',
            'only_with_salary': 'True'
        }
        response = requests.get(url, params=params).json()
        print(lang, response['found'])
        for vacancy in response['items']:
            print(vacancy['salary'])


def get_ 

if __name__ == '__main__':
    languages_for_programming = [
        'Python',
        'Java',
        'Javascript',
        'Ruby on Rails',
        'C++',
        'C#',
        'PHP',
        'Swift',
        'Scala'
    ]
    get_response(languages_for_programming)