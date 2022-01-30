
import requests
import bs4
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

#Coloque aqui o filtro desejado para ROIC, EV/EBITD, e volume médio de negociação diária dos últimos 2 meses. Os três devem ser numeros(int ou float) e não strings.

roic_filtro = 0
evebtid = 0
vol2m = 100000

url_tickers = 'http://fundamentus.com.br/resultado.php'
header_t = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"  
 }
 
r_tickers = requests.get(url_tickers, headers=header_t)
 
soup_tickers = BeautifulSoup(r_tickers.content, 'html.parser')
 
tickers = pd.read_html(r_tickers.text, decimal=",", thousands=".")[0]
 
tickers_df = pd.DataFrame(tickers)

tickers_df = tickers_df.loc[ : ,'Papel':'Papel']
 
tickers_list = tickers_df.to_string()
 
tickers = tickers_df['Papel']
indicadores = ['Papel','P/L','P/VP','P/EBIT','PSR',
              'P/Ativos','P/Cap. Giro','P/Ativ Circ Liq',
              'Div. Yield','EV / EBITDA','EV / EBIT',
              'Cres. Rec (5a)','LPA','VPA','Marg. Bruta',
              'Marg. EBIT','Marg. Líquida','EBIT / Ativo',
              'ROIC','ROE','Liquidez Corr','Div Br/ Patrim',
              'Giro Ativos','Vol $ méd (2m)','Setor','Subsetor']
df_list = []
 
for i in tickers:
  url = 'http://www.fundamentus.com.br/detalhes.php?papel='+i
  header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"  
  }
 
  r = requests.get(url, headers=header)
  
  soup = BeautifulSoup(r.content, 'html.parser')
  temp = []
  df_list.append(temp)
  for i in indicadores:
    x = soup.find(text = i).next_element.next_element.text.strip()
    temp.append(x)
     
df = pd.DataFrame(data = df_list)
df.columns = ['Papel','P/L','P/VP','P/EBIT','PSR',
              'P/Ativos','P/Cap. Giro','P/Ativ Circ Liq',
              'Div. Yield','EV / EBITDA','EV / EBIT',
              'Cres. Rec (5a)','LPA','VPA','Marg. Bruta',
              'Marg. EBIT','Marg. Líquida','EBIT / Ativo',
              'ROIC','ROE','Liquidez Corr','Div Br/ Patrim',
              'Giro Ativos','Vol $ méd (2m)','Setor','Subsetor']
df2 = df.copy()
 
df2.fillna(0, inplace=True)
df2.replace('-','0', inplace=True)
 
for c in ['P/L','P/VP','P/EBIT','PSR',
              'P/Ativos','P/Cap. Giro','P/Ativ Circ Liq',
              'EV / EBITDA','EV / EBIT','LPA','VPA','Liquidez Corr','Div Br/ Patrim',
              'Giro Ativos','Vol $ méd (2m)']:
  df2[c] = df2[c].str.replace('.', '')
  df2[c] = df2[c].str.replace(',', '.')
 
for i in ['Div. Yield','Cres. Rec (5a)','Marg. Bruta','Marg. EBIT','Marg. Líquida','EBIT / Ativo','ROIC','ROE','EV / EBIT']:
  df2[i] = df2[i].str.replace('.','')
  df2[i] = df2[i].str.replace('%','')
  df2[i] = df2[i].str.replace(',','.')
  df2[i] = df2[i].str.rstrip('%').astype('float') / 100
 
df2['P/L'] = pd.to_numeric(df2['P/L'], errors = 'coerce')
df2['ROIC'] = pd.to_numeric(df2['ROIC'], errors = 'coerce')
df2['Vol $ méd (2m)'] = pd.to_numeric(df2['Vol $ méd (2m)'], errors = 'coerce')
 
df2 = df2[df2['EV / EBIT'] > evebtid]
df2 = df2[df2['ROIC'] > roic_filtro]
df2 = df2[df2['Vol $ méd (2m)'] > vol2m]
 
N = len(df2)
ranking = pd.DataFrame()
ranking['pos'] = (range(1, N + 1 ,1))
ranking['EV / EBIT'] = df2[ df2['EV / EBIT'] > 0 ].sort_values(by=['EV / EBIT'])['Papel'][:N].values
ranking['ROIC'] = df2.sort_values(by=['ROIC'], ascending=False)['Papel'][:N].values
 
a = ranking.pivot_table(columns='EV / EBIT', values='pos')
b = ranking.pivot_table(columns='ROIC', values='pos')
t = pd.concat([a,b])
rank = t.dropna(axis=1).sum()

print(f'O filtro escolhido para o ROIC foi de {roic_filtro}.\n')
print(f'O filtro escolhido para o EV/EBTID foi de {evebtid}\n.')
print(f'O filtro escolhido para o volume diário de 2 meses foi de {vol2m}.')
print(f'A lista do rank é: \n\n {rank.sort_values()[:60]}')