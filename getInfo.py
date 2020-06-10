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

    def get_tradingviewbtc(self):
        url = 'https://br.tradingview.com/crypto-screener/'

        option = Options()
        option.headless = True
        driver = webdriver.Chrome()
        driver.get(url)

        tabela = driver.find_element_by_xpath('//*[@id="js-screener-container"]/div[4]/table')

        html_content = tabela.get_attribute('outerHTML')

        time.sleep(5)

        soup = BeautifulSoup(html_content, 'html.parser')
        tabela_estruturada = soup.find(name='table')

        df_full = pd.read_html(str(tabela_estruturada))[0]
        

        df_full = df_full.drop(columns=['Preço','% de mudança','Var', 'Мáx', 'Мín', 'Vol', 'Bolsa'])

        driver.quit()

        nomes = []

        for nome in df_full['Código4617 correspondências']:
            nomes.append(nome)
        
        df_full['Nome'] = nomes
        df_full = df_full.drop(columns=['Código4617 correspondências'])
        df_full['5 minutos'] = df_full['Classificação']
        df_full = df_full.drop(columns=['Classificação'])

        return df_full.to_dict()

    def get_tradingview(self):
        url = 'https://br.tradingview.com/forex-screener/'

        option = Options()
        option.headless = True
        driver = webdriver.Chrome(options=option)
        driver.get(url)

        tabela = driver.find_element_by_xpath('//*[@id="js-screener-container"]/div[4]/table')
        html_content = tabela.get_attribute('outerHTML')
        time.sleep(5)

        soup = BeautifulSoup(html_content, 'html.parser')
        tabela_estruturada = soup.find(name='table')

        df_full = pd.read_html(str(tabela_estruturada))[0]
        df_full = df_full.drop(columns=['Preço','% de variação','Var', 'Venda', 'Мáx', 'Мín', 'Oferta'])
        
        driver.quit()

        nomes = []

        for nome in df_full['Código49 resultados']:
            nomes.append(nome[0:6])
        
        df_full['Nome'] = nomes
        df_full = df_full.drop(columns=['Código49 resultados'])
        df_full['5 minutos'] = df_full['Classificação']
        df_full = df_full.drop(columns=['Classificação'])

        return df_full.to_dict()

def pegarSinais():
    dados = webrobot()
    investing = dados.get_investing()
    trading_view = dados.get_tradingview()

    dict_investing = {}
    dict_trading_view = {}

    sinais = {}

    count = 0
    for i in range(len(trading_view['Nome'])):
        dict_trading_view[str(count)] = {'moeda': trading_view['Nome'][i], 'status': trading_view['5 minutos'][i]}
        count += 1

    count = 0
    for i in range(len(investing['Nome'])):
        dict_investing[str(count)] = {'moeda': investing['Nome'][i], 'M5': investing['5 minutos'][i], 'M15': investing['15 minutos'][i]}
        count += 1

    sinais['investing'] = dict_investing
    sinais['tradingview'] = dict_trading_view
    sinais['horario'] = dados.utc_to_local()

    print(str(sinais))

    return sinais


while True:
    try:
        sinais_gill = pegarSinais()
        if (len(sinais_gill) > 0):
            try:
                requests.post('https://telegrambottrade.herokuapp.com/uploadsignal', json=json.dumps(sinais_gill))
            except:
                print('Houve um erro ao enviar')
        else:
            print('Não é maior que 0')
        print('Não foi')
        time.sleep(10)
    except:
        pass