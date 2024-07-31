import pandas as pd
import requests
import json
import re
import time
# static variables are defined here

api_key # = <insert your api key here>


auth_token = get_authToken(api_key)
header = {'X-ELS-APIKey': api_key}
df = pd.read_csv('survbib-data_extract200.csv', sep=';',)

list_of_title_lsts = []
rejects = pd.DataFrame(columns= ['Vorname', 'Nachname', 'Uni', 'Alias'])

author_url = 'https://api.elsevier.com/content/search/author'
scopus_url = 'https://api.elsevier.com/content/search/scopus'



def fix_university_name(uni):
    p = fr'^(U)(\s)'
    p1 = r'(?<!\S)H\s'
    res = re.sub(p, fr'\1niversität\2', uni)
    fixed = re.sub(p1, r'H'+'ochschule', res)
    print(fixed)
    return fixed

def seperate_uni_name_from_alias(uni):

    p = r'\(([^)]+)\)'

    m = re.search(p, uni)
    if m:
        alias = m.group(1)
        uni_cleaned = re.sub(p, '', uni)
        return uni_cleaned, alias
    else:
        return uni, None

# function to get the author id from their first and last name
def clean_author_id(au_id):
    p = r'^AUTHOR_ID:'
    clean = re.sub(p, '', au_id)
    return clean


# function to get the author id from their first and last name
def get_au_id(lstnm, frstnm, uni):
    u = fix_university_name(uni)
    u, alias = seperate_uni_name_from_alias(u)
    # using full name + institution to avoid duplicates by other authors with identical names
    if alias == None:
        query_str = 'AUTHLASTNAME(' + lstnm + ') AND AUTHFIRST(' + frstnm + ') AND AFFIL(' + u + ')'
    else:
        query_str = 'AUTHLASTNAME(' + lstnm + ') AND AUTHFIRST(' + frstnm + ') AND AFFIL(' + u + ' OR ' + alias + ')'

    par_author = {'query': query_str, 'count': 200, 'fields': 'dc:identifier, document-count'}
    time.sleep(0.1666666)
    r = requests.get(url=author_url, headers=header, params=par_author)

    response = r.json()
    #print('author response json created', json.dumps(response, indent=4))

    if 'search-results' not in response.keys():
        print('funky error:', json.dumps(response, indent=4))
        print('related query string:', query_str)
        return 0,0
    if 'error' in response['search-results']['entry'][0].keys():
        tmp = {'Vorname': frstnm, 'Nachname': lstnm, 'Uni': u, 'Alias': alias}
        rejects.loc[len(rejects)] = tmp
        print('empty author response for', query_str)
        return 0,0

    au_id = clean_author_id(response['search-results']['entry'][0]['dc:identifier'])
    dc_count = response['search-results']['entry'][0]['document-count']
    return au_id, dc_count







def get_scopus_publications(au_id, dc_count, row):
    q_str = 'AU-ID('+str(au_id)+')'
    par_titles = {'query': q_str, 'count': 200, 'start':0}
    title_request = requests.get(scopus_url, headers=header, params=par_titles)

    time.sleep(0.3333)
    title_response = title_request.json()
    if 'search-results' not in title_response.keys():
        print('funky error with title response:',json.dumps(title_response, indent=4))
        print('related query:', q_str)
        return
    if 'error' in title_response['search-results']['entry'][0].keys():
        print('empty title response for ', au_id)
        return



    print('expected document count: ', dc_count)
    print('lenght response  ',len(title_response['search-results']['entry']) )
    if len(title_response['search-results']['entry']) == int(dc_count):
        for i in title_response['search-results']['entry']:
            i = {k: v for k, v in i.items() if k not in dump_lst}
            r = {**row, **i}
            rslts.loc[len(rslts)] = r
    else:
        for i in title_response['search-results']['entry']:
            i = {k: v for k, v in i.items() if k not in dump_lst}
            r = {**row, **i}
            rslts.loc[len(rslts)] = r
        print('starting loop to look for more publications')
        print('looking for ' + dc_count + ' publications in total')
        ## for the while loop
        j = 1
        ## counter for the found documents
        found = len(title_response['search-results']['entry'])

        while found < int(dc_count):

            par_titles['start'] = found
            time.sleep(0.3333)
            tr = requests.get(scopus_url, headers=header, params=par_titles)
            res = tr.json()
            found = found + len(res['search-results']['entry'])

            if 'search-results' not in res.keys():
                print('funky error with title response in while loop:', json.dumps(r, indent=4), found,
                      dc_count)
                print('related query:', q_str)
                return 0
            if 'error' in res['search-results']['entry'][0].keys():
                print('empty title response for in while loop', au_id, found, dc_count)
                return 0
            for i in res['search-results']['entry']:
                i = {k: v for k, v in i.items() if k not in dump_lst}
                r = {**row, **i}
                rslts.loc[len(rslts)] = r

            j += 1


    return



for i, row in df.iterrows():
    # first use Scopus Author Search to retrive Author_IDs for correct identification of papers

    au_id, dc_count = get_au_id(row['nachname'],frstnm = row['vorname'], uni=row['uni'])
    if au_id == 0:
        continue
    title_list = get_scopus_publications(au_id, dc_count,row=df.loc[i].to_dict())
    if title_list == 0:
        continue



rslts.replace(r'^s*$', np.nan, regex=True, inplace=True)


rslts.to_csv('BigTest.csv', sep=';')
rejects.to_csv('AuthorsWithEmptyResp.csv', sep=';')