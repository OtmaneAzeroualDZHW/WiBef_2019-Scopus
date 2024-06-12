import pandas as pd
import requests
import json
import Key # file that stores API Key
# static variables are defined here

header = {'X-ELS-APIKey': api_key}
df = pd.read_csv(<file>, sep=';',)
#adding empty columns for scopus titles
df['ScopusTitles'] = ''

author_url = 'https://api.elsevier.com/content/search/author'
scopus_url = 'https://api.elsevier.com/content/search/scopus'




# function to get the author id from their first and last name
def get_au_id(lstnm,frstnm):

    # using full name + institution to avoid duplicates by other authors with identical names
    query_str = 'AUTHLASTNAME('+lstnm+') AND AUTHFIRST('+frstnm+')'
    par_author = {'query': query_str, 'count': 200}
    r = requests.get(url=author_url, headers=header, params=par_author)


    response = r.json()
    print('author response json created')
    print(json.dumps(response, indent=4))
    if 'error' in response['search-results']['entry'][0].keys():
        print('empty author response')
        return 0
    # TODO Aus mehreren Autoren den richtigen finden
    entry = pd.json_normalize(response['search-results']['entry'])
    au_id = str(entry['dc:identifier'])
    au_id = au_id[16:26]
    print(au_id)
    return au_id







def get_scopus_publications(au_id):
    q_str = 'AU-ID('+au_id+')'
    par_titles = {'query': q_str, 'count': 200}
    title_request = requests.get(scopus_url, headers=header, params=par_titles)

    title_response = title_request.json()
    print('title response json created')
    print(json.dumps(title_response, indent=4))
    if 'error' in title_response['search-results']['entry'][0].keys():
        print('empty title response')
        return 0
    entries = pd.json_normalize(title_response['search-results']['entry'])
    print(entries)
    lst = entries['dc:title'].tolist()
    return lst



for i, row in df.iterrows():
    # first use Scopus Author Search to retrive Author_IDs for correct identification of papers

    au_id = get_au_id(row['nachname'],frstnm = row['vorname'])
    if au_id == 0:
        continue
    title_list = get_scopus_publications(au_id)
    if title_list == 0:
        continue
    row['ScopusTitles'] = title_list

df.to_csv('test.csv')