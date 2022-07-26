from bs4 import BeautifulSoup
from dataclasses import dataclass
from collections import Counter
from operator import itemgetter
import time

# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# custom
from client import FFClient
from config import CLIENT_ID, CLIENT_SECRET
from report import Report
from enums import Encounter
from data import Event


def pulls(total_wipes, list_of_p1):
    ret = list(range(1, total_wipes+1))
    for i in list_of_p1:
        ret.remove(i)

    return ret

DANCE_PARTNER_URL = 'https://partnercalc.herokuapp.com/'
dataset = [
    # '19M43vwFh6GtAcCp',
    'Tm8K39AaBpYwD4MR',
    ]

@dataclass
class Dance:
    bins = [
        ('00:00', '02:40', 'Thordan'),
        ('03:10', '04:40', 'Nidhogg'),
        ('05:30', '06:50', 'Eyes'),
        ('07:00', '08:05', 'Intermission'),
        ('08:05', '10:00', 'Thordan Returns')
    ]
    time: str
    target: str
    optimal: str
    table: dict
    phase: int

    def __init__(self, tag):
        summary = tag.contents[0].contents[0].contents[2:]

        if 'badge-success' in summary[0].attrs['class']:
            self.target = summary[0].text
            self.optimal = self.target
        else:
            self.target = summary[0].text
            self.optimal = summary[1].strip()[18:-1]
            
        self.time = tag.contents[0].contents[2].contents[0].text
        tds = tag.find('tbody').find_all('td')

        self.table = dict()
        for i in range(len(tds) // 6):
            self.table[tds[i*6].text] = int(tds[i*6+5].text)



    def __str__(self):
        return f'[{self.time}]/[{self.bin_time()}]:{self.target} => {self.optimal}'

    def bin_time(self):
        for b in self.bins:
            if b[0] <= self.time <= b[1]:
                return f'{b[0]}-{b[1]} {b[2]}'

        return self.time


def process(client: FFClient):
    all_dances = list()
    SECTION_CLASS_NAME = 'card border-primary mb-3'
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:

        for report_code in dataset:
            print(f'{report_code=}')
            report = Report(report_code, client, Encounter.DSU)
            pm = report.get_phase_model()

            for fight_id, fight in report._fights.items():
                print(f'{fight_id=}')

                driver.get(f'{DANCE_PARTNER_URL}{report_code}/{fight_id}')
                try:
                    WebDriverWait(driver, 10) \
                        .until(EC.title_contains('Dragonsong\'s Reprise'))
                except Exception:
                    print(f'timeout:{pull}')
                    continue

                html_text = driver.page_source
                soup = BeautifulSoup(html_text, 'html5lib')
                dances_html = soup.find_all('div', {'class': SECTION_CLASS_NAME})

                dances = [Dance(tag) for tag in dances_html]

                for dance in dances:
                    # time in dance is relative to the start of the fight
                    minute, second = dance.time.split(':')
                    ms = int(minute)*60*1000 + float(second)*1000 + fight.start_time
                    ms = int(ms)
                    phase = pm.phase_name(Event.from_time(ms, fight_id))
                    print(f'{phase=}')
                    dance.phase = phase

                all_dances = all_dances + dances

    return all_dances

client = FFClient(CLIENT_ID, CLIENT_SECRET)

all_dances = process(client)
all_dances.sort(key=lambda x: x.time)

with open('list.txt', 'w') as f:
    for dance in all_dances:
        f.write(str(dance) + '\n')

tables = dict()
    
for dance in all_dances:
    # tables.setdefault(dance.bin_time(), list()).append(dance.table)
    tables.setdefault(dance.phase, list()).append(dance.table)

# tables is time: list of tables

for time, ls in tables.items():
    counter = Counter()
    for table in ls:
        counter.update(table)
    tables[time] = {k:v/len(ls) for k,v in dict(counter).items()}
    tables[time]['events'] = len(ls)

# tables is time: average damage table
with open('output.txt', 'w', encoding='utf-8') as f:
    for phase, table in tables.items():
        f.write(f'{phase=}\n')
        sorted_table = sorted(table.items(), key=itemgetter(1), reverse=True)
        for name, damage in sorted_table:
            f.write(f'\t{name}:{int(damage)}\n')
