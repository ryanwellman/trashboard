from glob import glob
import os
import re

pdfs = glob('*.pdf')
states = set()
rename_dict = {}
for pdf in pdfs:
    new_pdf = re.sub(r'permit (.*).pdf', r'\1', pdf)
    if new_pdf.find('residential') != -1:
        res_com = 'residential'
    elif new_pdf.find('commercial') != -1:
        res_com = 'commercial'
    else:
        res_com = 'all'
    new_pdf = re.sub(r'residential|commercial', r'', new_pdf)
    if new_pdf.find('county') != -1:
        county_or_city = 'county'
    else:
        county_or_city = 'city'
    new_pdf = re.sub(r'county', r'', new_pdf)
    state = re.sub(r'.*(\w\w) *', r'\1', new_pdf).upper()
    states.add(state)
    new_pdf = re.sub(r'(.*)(\w\w) *', r'\1', new_pdf).strip()
    new_pdf = re.sub(r' +', r'-', new_pdf)
    county_or_city_name = new_pdf
    new_name = '%s/%s-%s-%s.pdf' % (state, county_or_city, county_or_city_name, res_com)
    rename_dict[pdf] = new_name
for state in states:
    os.mkdir(state)
for name in rename_dict:
    os.rename(name, rename_dict[name])