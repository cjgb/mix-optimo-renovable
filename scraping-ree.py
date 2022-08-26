import pandas as pd
import requests
import json


cookies = {
    'visid_incap_257780': 'jc28dyHpQzWndVySBH3efkKVn2IAAAAAQUIPAAAAAABbIZnfEcl/jLCTtncIWNvS',
    'visid_incap_1863806': 'C/tZlrhlSRyu5T/zgqoAhhejyWIAAAAAQUIPAAAAAACfU/4FREH4fkd1Sm8YSVZw',
    'incap_ses_1484_257780': 'xeeYIMzTQBv48xV8QTqYFGIh1GIAAAAAn2q8n2HZPmQdj2EwL7Yv4A==',
    'incap_ses_1484_1863806': '4oF1YhQzN1j6/BV8QTqYFGsh1GIAAAAAUqEZjUhiRZGSe22Zbr8INQ==',
}

headers = {
    'authority': 'demanda.ree.es',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'visid_incap_257780=jc28dyHpQzWndVySBH3efkKVn2IAAAAAQUIPAAAAAABbIZnfEcl/jLCTtncIWNvS; visid_incap_1863806=C/tZlrhlSRyu5T/zgqoAhhejyWIAAAAAQUIPAAAAAACfU/4FREH4fkd1Sm8YSVZw; incap_ses_1484_257780=xeeYIMzTQBv48xV8QTqYFGIh1GIAAAAAn2q8n2HZPmQdj2EwL7Yv4A==; incap_ses_1484_1863806=4oF1YhQzN1j6/BV8QTqYFGsh1GIAAAAAUqEZjUhiRZGSe22Zbr8INQ==',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
}

params = {
    'callback': 'angular.callbacks._7',
    'curva': 'DEMANDAQH',
    'fecha': '2022-07-16',
}

response = requests.get('https://demanda.ree.es/WSvisionaMovilesPeninsulaRest/resources/demandaGeneracionPeninsula', params=params, cookies=cookies, headers=headers)


my_dates = [x.strftime("%Y-%m-%d") for x in pd.date_range(start = "2021-01-01", end = "2022-07-16")]


def get_date(my_date):
    params['fecha'] = my_date
    response = requests.get('https://demanda.ree.es/WSvisionaMovilesPeninsulaRest/resources/demandaGeneracionPeninsula', params=params, cookies=cookies, headers=headers)
    return response.text

my_data = [get_date(x) for x in my_dates]

def process_data(x):
    tmp = x
    tmp = tmp[21:-2]
    tmp = json.loads(tmp)
    tmp = tmp['valoresHorariosGeneracion']
    return pd.DataFrame(tmp)

tmp = [process_data(x) for x in my_data]

res = pd.concat(tmp)
res = res.groupby('ts').mean().reset_index()
res.to_csv("hueco-termico.csv", index=False)