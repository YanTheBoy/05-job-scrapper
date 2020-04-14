# Salary Predictor
The script was written for salary prediction based on HH and SuperJob data.

# How to install
Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```bash
$ pip install -r requirements.txt
```
For script correct working you should get your personal API APP ID from [SuperJob](https://api.superjob.ru/) 
and put this APP ID into .env file in local folder.
```text
SUPERJOB_API_APP_ID=your_app_id
```

Run salary-predictor.py for creating tables with all needed data:
```bash
$ python3 salary-predictor.py
$ +SuperJob Moscow--------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| 1C                    | 30               | 30                  | 107046           |
| Java                  | 2                | 2                   | 154000           |
| Javascript            | 2                | 2                   | 160750           |
...
```

# Project Goals
The code is written for educational purposes on online-course for web-developers [DEVMAN.org](https://devman.org)