import pandas as pd
import requests
import json

# static variables are defined here

header = {'X-ELS-APIKey': api_key}
df = pd.read_csv('survbib-data_extract200.csv', sep=';',)
#adding empty columns for scopus titles
#df['ScopusTitles'] = ''
list_of_title_lsts = []

author_url = 'https://api.elsevier.com/content/search/author'
scopus_url = 'https://api.elsevier.com/content/search/scopus'


def fix_university_name(uni):
    p = fr'^(U)(\s)'
    res = re.sub(p, fr'\1niversität\2', uni)
    return res

def seperate_uni_name_from_alias(uni):

    p = r'\(([^)]+)\)'

    m = re.search(p, uni)
    print('match: ', m)
    if m:
        alias = m.group(1)
        uni_cleaned = re.sub(p, '', uni)
        return uni_cleaned, alias
    else:
        return uni, None

# function to get the author id from their first and last name
def get_au_id(lstnm,frstnm,uni):

    u = fix_university_name(uni)
    u, alias = seperate_uni_name_from_alias(u)
    # using full name + institution to avoid duplicates by other authors with identical names
    if alias == None:
        query_str = 'AUTHLASTNAME('+lstnm+') AND AUTHFIRST('+frstnm+') AND AFFIL('+u+')'
    else:
        query_str = 'AUTHLASTNAME('+lstnm+') AND AUTHFIRST('+frstnm+') AND AFFIL('+u+' OR '+alias+')'
        print('query_str: ', query_str)
    par_author = {'query': query_str, 'count': 200}
    r = requests.get(url=author_url, headers=header, params=par_author)


    response = r.json()
    print('author response json created')
    if 'search-results' not in response.keys():
        print('funky error:',json.dumps(response, indent=4))
        print('related query string:', query_str)
        return 0
    if 'error' in response['search-results']['entry'][0].keys():
        print('empty author response for', frstnm, lstnm)
        return 0
    # TODO Aus mehreren Autoren den richtigen finden
    entry = pd.json_normalize(response['search-results']['entry'])
    au_id = str(entry['dc:identifier'])
    au_id = au_id[15:26]
    print(au_id)
    return au_id







def get_scopus_publications(au_id):
    q_str = 'AU-ID('+au_id+')'
    par_titles = {'query': q_str, 'count': 200}
    title_request = requests.get(scopus_url, headers=header, params=par_titles)

    title_response = title_request.json()
    print('title response json created')
    if 'search-results' not in title_response.keys():
        print('funky error:',json.dumps(title_response, indent=4))
        print('related query:', q_str)
        return 0
    if 'error' in title_response['search-results']['entry'][0].keys():
        print('empty title response for ', au_id)
        return 0
    entries = pd.json_normalize(title_response['search-results']['entry'])

    lst = entries['dc:title'].tolist()
    list_of_title_lsts.append(lst)
    print(lst)
    return lst



for i, row in df.iterrows():
    # first use Scopus Author Search to retrive Author_IDs for correct identification of papers

    au_id = get_au_id(row['nachname'],frstnm = row['vorname'], uni=row['uni'])
    if au_id == 0:
        continue
    title_list = get_scopus_publications(au_id)
    if title_list == 0:
        continue

df.insert(column='scopus titles',value=pd.Series(list_of_title_lsts))

df.to_csv('test.csv', sep=';')