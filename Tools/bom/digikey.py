#!/usr/bin/env python3
"""Digi-Key Product Information V4. The keys come from Tools/.env, which git ignores: DIGIKEY_CLIENT_ID and DIGIKEY_SECRET."""
import json,os,re,time,urllib.parse,urllib.request
def _env():
    o={}
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','.env')):
        m=re.match(r'\s*(?:export\s+)?([A-Za-z_]+)\s*=\s*["\']?([^"\'\s]+)',l)
        if m:o[m.group(1)]=m.group(2)
    return o
E=_env();ID=E['DIGIKEY_CLIENT_ID'];SECRET=E['DIGIKEY_SECRET'];_t=[None,0]
def token():
    if _t[0] and time.time()<_t[1]: return _t[0]
    b=urllib.parse.urlencode(dict(client_id=ID,client_secret=SECRET,grant_type='client_credentials')).encode()
    r=json.load(urllib.request.urlopen(urllib.request.Request('https://api.digikey.com/v1/oauth2/token',b,{'Content-Type':'application/x-www-form-urlencoded'}),timeout=30));_t[0]=r['access_token'];_t[1]=time.time()+r.get('expires_in',500)-30;return _t[0]
def _h(): return {'Authorization':'Bearer '+token(),'X-DIGIKEY-Client-Id':ID,'X-DIGIKEY-Locale-Site':'US','X-DIGIKEY-Locale-Language':'en','X-DIGIKEY-Locale-Currency':'USD','Accept':'application/json','Content-Type':'application/json'}
def details(pn): return json.load(urllib.request.urlopen(urllib.request.Request('https://api.digikey.com/products/v4/search/'+urllib.parse.quote(pn,safe='')+'/productdetails',headers=_h()),timeout=40))['Product']
def keyword(q,n=10): return json.load(urllib.request.urlopen(urllib.request.Request('https://api.digikey.com/products/v4/search/keyword',json.dumps(dict(Keywords=q,Limit=n,Offset=0)).encode(),_h(),method='POST'),timeout=40))
def brief(p): return dict(mpn=p.get('ManufacturerProductNumber'),mfr=(p.get('Manufacturer') or {}).get('Name'),desc=(p.get('Description') or {}).get('ProductDescription'),stock=p.get('QuantityAvailable'),status=(p.get('ProductStatus') or {}).get('Status'),pn=[(v.get('DigiKeyProductNumber'),(v.get('PackageType') or {}).get('Name')) for v in p.get('ProductVariations') or []][:4])
