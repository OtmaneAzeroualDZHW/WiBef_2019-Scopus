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
def clean_author_id(au_id):
    p = r'^AUTHOR_ID:'
    clean = re.sub(p, '', au_id)
    print(clean)
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
        print('empty author response for', query_str)
        return 0,0

    au_id = clean_author_id(response['search-results']['entry'][0]['dc:identifier'])
    dc_count = response['search-results']['entry'][0]['document-count']
    return au_id, dc_count







def get_scopus_publications(au_id, dc_count, lstn,frstn):
    q_str = 'AU-ID('+au_id+')'
    par_titles = {'query': q_str, 'count': 200, 'start':0}
    title_request = requests.get(scopus_url, headers=header, params=par_titles)

    time.sleep(0.3333)
    title_response = title_request.json()
    print('title response json created')
    if 'search-results' not in title_response.keys():
        print('funky error with title response:',json.dumps(title_response, indent=4))
        print('related query:', q_str)
        return 0
    if 'error' in title_response['search-results']['entry'][0].keys():
        print('empty title response for ', au_id, lstn, frstn)
        return 0
    entries = pd.json_normalize(title_response['search-results']['entry'])

    lst = entries['dc:title'].tolist()
    if len(lst) == int(dc_count):
        print('i think my list is complete')
        list_of_title_lsts.append(lst)
    else:
        print('starting loop to look for more publications')
        print('looking for '+dc_count+'publications in total')
        i=1
        while len(lst) < int(dc_count):
            par_titles['start'] = len(lst)
            time.sleep(0.3333)
            tr = requests.get(scopus_url, headers=header, params=par_titles)
            r = tr.json()
            if 'search-results' not in title_response.keys():
                print('funky error with title response in while loop:', json.dumps(title_response, indent=4),len(lst), dc_count)
                print('related query:', q_str)
                return 0
            if 'error' in title_response['search-results']['entry'][0].keys():
                print('empty title response for in while loop', au_id, len(lst), dc_count ,lstn, frstn)
                return 0
            e = pd.json_normalize(r['search-results']['entry'])

            #lst.extend(e['dc:title'].tolist())
            for title in e['dc:title'].tolist():
                if title not in lst:
                    lst.append(title)

            #print('list at len',len(lst))
            #print('step', i)
            #print(lst)
            i+=1
            if len(e['dc:title'].tolist()) < 200:
                list_of_title_lsts.append(lst)
                break


    #print(lst)
    return lst



for i, row in df.iterrows():
    # first use Scopus Author Search to retrive Author_IDs for correct identification of papers

    au_id, dc_count = get_au_id(row['nachname'],frstnm = row['vorname'], uni=row['uni'])
    if au_id == 0:
        continue
    title_list = get_scopus_publications(au_id, dc_count,lstn= row['nachname'],frstn = row['vorname'])
    if title_list == 0:
        continue

df.insert(loc = 11,column='scopus titles',value=pd.Series(list_of_title_lsts))

df.to_csv('test.csv', sep=';')