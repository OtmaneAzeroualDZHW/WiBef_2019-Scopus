import pandas as pd
import requests
import json

# static variables are defined here
api_key = '34e76d186db66dc6bf09dfd29c293707'
header = {'X-ELS-APIKey': api_key}
df = pd.read_csv('survbib-data_extract200.csv', sep=';',)
#adding empty columns for scopus titles
df['ScopusTitles'] = ''

author_url = 'https://api.elsevier.com/content/search/author'
scopus_url = 'https://api.elsevier.com/content/search/scopus'

# function to get the author id from their first and last name
def get_au_id(lstnm,frstnm):

    query_str = 'AUTHLASTNAME('+lstnm+') AND AUTHFIRST('+frstnm+')'
    par_author = {'query' : query_str}
    r = requests.get(url=author_url, headers=header, params=par_author)
    response = r.json()
    entry = pd.json_normalize(response['search-results']['entry'])
    au_id = str(entry['dc:identifier'])
    au_id = au_id[16:26]
    print(au_id)

    # TODO Catch empty Result here

    return au_id

def get_scopus_publications(au_id):
    q_str = 'AU-ID('+au_id+')'
    par_titles = {'query': q_str}
    title_request = requests.get(scopus_url, headers=header, params=par_titles)
    title_response = title_request.json()
    entries = pd.json_normalize(title_response['search-results']['entry'])
    print(entries)
    lst = entries['dc:title'].tolist()
    return lst


for i, row in df.iterrows():
    # first use Scopus Author Search to retrive Author_IDs for correct identification of papers
    au_id = get_au_id(row['nachname'],frstnm = row['vorname'])
    # todo: break here if no au-id can be found
    title_list = get_scopus_publications(au_id)
    row['ScopusTitles'] = title_list

df.to_csv('test.csv')

