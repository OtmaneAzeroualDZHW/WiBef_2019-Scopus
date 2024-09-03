import pandas as pd
import requests
import json
import re
import time
import numpy as np




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
def get_au_id(row, lstnm, frstnm, uni, header):
    author_url = 'https://api.elsevier.com/content/search/author'

    u = fix_university_name(row[uni])
    u, alias = seperate_uni_name_from_alias(u)
    # using full name + institution to avoid duplicates by other authors with identical names
    # todo: change this to try except
    if alias == None:
        query_str = 'AUTHLASTNAME(' + row[lstnm] + ') AND AUTHFIRST(' + row[frstnm] + ') AND AFFIL(' + u + ')'
    else:
        query_str = 'AUTHLASTNAME(' + lstnm + ') AND AUTHFIRST(' + frstnm + ') AND AFFIL(' + u + ' OR ' + alias + ')'

    par_author = {'query': query_str, 'count': 200, 'fields': 'dc:identifier, document-count'}
    time.sleep(0.1666666)
    r = requests.get(url=author_url, headers=header, params=par_author)

    response = r.json()

    try:
        au_id = clean_author_id(response['search-results']['entry'][0]['dc:identifier'])
        dc_count = response['search-results']['entry'][0]['document-count']

    except KeyError:
        return KeyError

    return au_id, dc_count







def get_scopus_publications(rslts,au_id, dc_count, row, header):
    scopus_url = 'https://api.elsevier.com/content/search/scopus'
    au_dic = {'authorID': au_id}


    dump_lst = ['@_fa', 'link', 'prism:url', 'dc:creator', 'prism:coverDisplayDate', 'affiliation', 'subtype',
                'source-id', 'openaccess', 'freetoread.value', 'freetoreadLabel.value', 'prism:issueIdentifier',
                'prism:isbn']

    q_str = 'AU-ID(' + str(au_id) + ')'
    par_titles = {'query': q_str, 'count': 200, 'start': 0}

    print('expected document count: ', dc_count)

    if int(dc_count) <= 200:
        title_request = requests.get(scopus_url, headers=header, params=par_titles)

        time.sleep(0.3333)
        title_response = title_request.json()
        try:
            for i in title_response['search-results']['entry']:
                i = {k: v for k, v in i.items() if k not in dump_lst}
                r = {**au_dic, **row, **i}
                rslts.loc[len(rslts)] = r
        except KeyError:
            return KeyError
    else:
        found = 0

        while found < int(dc_count):

            par_titles['start'] = found
            time.sleep(0.3333)
            tr = requests.get(scopus_url, headers=header, params=par_titles)
            res = tr.json()

            try:
                for i in res['search-results']['entry']:
                    i = {k: v for k, v in i.items() if k not in dump_lst}
                    r = {**au_dic, **row, **i}
                    rslts.loc[len(rslts)] = r
            except KeyError:
                return KeyError

            found = found + len(res['search-results']['entry'])
            print('currently found ', found, ' documents')


def clean_header(col):

    pf1 = r'^dc:'
    pf2 = r'^prism:'
    cc = r'([a-z])([A-Z])'
    cleaned_col_names ={}
    for h in col:
        x = re.sub(pf1, '', h)
        x = re.sub(pf2, '', x)
        x = re.sub(cc, r'\1 \2', x)
        cleaned_col_names[h] = x.lower()
    return cleaned_col_names

def clean_col(rslts):
    pf1 = r'SCOPUS_ID:'
    pf2 = r'2-s2.0-'
    for i in rslts['identifier']:
        i = re.sub(pf1, '', i)
    for i in rslts['eid']:
        i = re.sub(pf2, '',i)
    return

def clean_rslts(rslts):
    # dropping possible duplicates
    rslts.drop_duplicates()
    #replacing empty cells wit np.nan
    rslts.replace(r'^s*$', np.nan, regex=True, inplace=True)
    # renaming columns for proper spelling
    cleaned_col_names = clean_header(rslts.columns.values.tolist())
    rslts.rename(columns=cleaned_col_names, inplace=True)
    # cleaning up the data
    pf1 = r'SCOPUS_ID:'
    pf2 = r'2-s2.0-'
    rslts['identifier']=rslts['identifier'].replace(pf1, '', regex=True)
    rslts['eid'] = rslts['eid'].replace(pf2, '', regex=True)


    return rslts


def search_scopus(api_key,tosearch,rslts,rejects, frstnm, lstnm, uni,inst_tkn=None, progress_callback=None):


    if inst_tkn != None:
        hdr = {'X-ELS-APIKey': api_key, 'X-ELS-Insttoken': inst_tkn}
    else:
        hdr = {'X-ELS-APIKey': api_key}



    orig_head = tosearch.columns.values.tolist()
    # hardcoding fields from the scopus search into a keep and a dump list
    keep_lst = ['dc:identifier', 'eid', 'dc:title', 'prism:publicationName', 'prism:pageRange', 'prism:coverDate',
                'prism:doi', 'citedby-count', 'prism:aggregationType', 'subtypeDescription', 'openaccessFlag',
                'prism:issn', 'prism:eIssn', 'prism:volume', 'pubmed-id']

    a_id = ['authorID']
    # making a dataframe to store results
    col = a_id + orig_head + keep_lst

    rslts = pd.DataFrame(columns=col)

    rejects = pd.DataFrame(columns=orig_head)
    t = len(tosearch)
    for i, row in tosearch.iterrows():
        # first use Scopus Author Search to retrive Author_IDs for correct identification of papers
        try:
            au_id, dc_count = get_au_id(tosearch.loc[i].to_dict(), lstnm, frstnm, uni, hdr)
        except:
            rejects = rejects._append(row)
            continue

        try:
            get_scopus_publications(rslts,au_id, dc_count,tosearch.loc[i].to_dict(),hdr)
        except KeyError:
            continue
    if progress_callback:
        progress_callback(i+1, t)
    #rslts = clean_rslts(rslts=rslts)

    #rejects.to_csv('Rejects1208.csv', sep=';', index=False)

    return rslts, rejects





