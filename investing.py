import requests, time, json, requests, pytz, datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class webrobot:

    def __init__(self):
        pass

    def utc_to_local(self):
        local_tz = pytz.timezone('America/Sao_Paulo') 
        utc_dt = datetime.datetime.now()
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        dados = str(local_tz.normalize(local_dt))[0:19]
        data = dados[0:10]
        data = data[8:10] + '/' + data[5:7] + '/' + data[0:4]
        hora = dados[11:16]
        return data + ' -- ' + hora

    def get_investing(self):
        url = 'https://br.investing.com/technical/technical-summary'

        option = Options()
        option.headless = True
        driver = webdriver.Chrome(options=option)
        driver.get(url)

        tabela = driver.find_element_by_xpath('//*[@id="technical_summary_container"]/table')
        html_content = tabela.get_attribute('outerHTML')
        time.sleep(5)

        soup = BeautifulSoup(html_content, 'html.parser')
        tabela_estruturada = soup.find(name='table')

        df_full = pd.read_html(str(tabela_estruturada))[0]
        df_full = df_full.drop(columns=['Tipo','Hora','Diário'])

        #df_full = df_full.loc[range(2,len(df_full),3)]
        driver.quit()

        nomes = []

        for nome in df_full['Nome']:
            nomes.append(nome[0:7].replace('/',''))
        
        df_full['Nome'] = nomes

        return df_full.to_dict()

while True:
    w = webrobot()
    investing = w.get_investing()
    print(investing)