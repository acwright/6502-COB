#!/usr/bin/env python3
"""Mouser Search API. The key comes from Tools/.env, which git ignores (MOUSER_API_KEY or any variable with MOUSER in its name)."""
import json,os,re,urllib.request
def _key():
    p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','.env')
    for l in open(p):
        m=re.match(r'\s*(?:export\s+)?([A-Za-z_]*MOUSER[A-Za-z_]*)\s*=\s*["\']?([^"\'\s]+)',l,re.I)
        if m: return m.group(2)
    raise SystemExit('no Mouser key in .env')
def part(pn,exact=True):
    b=json.dumps(dict(SearchByPartRequest=dict(mouserPartNumber=pn,partSearchOptions='Exact' if exact else 'None'))).encode()
    r=urllib.request.Request('https://api.mouser.com/api/v1/search/partnumber?apiKey='+_key(),b,{'Content-Type':'application/json','Accept':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=30))
def brief(p): return dict(mouser=p.get('MouserPartNumber'),mpn=p.get('ManufacturerPartNumber'),mfr=p.get('Manufacturer'),desc=p.get('Description'),stock=p.get('Availability'),life=p.get('LifecycleStatus'))
