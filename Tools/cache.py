"""A result cache for the slow checks, keyed by the bytes of every file a result depends on.

A result is reused only while every input file, the checking script's own source and the KiCad version are
byte-for-byte the same, so a cached answer is the answer a fresh run would give. Delete cache.json, or pass
--no-cache to derived-check.py or audit.py, to recompute everything."""
import os,json,hashlib,subprocess,sys
H=os.path.dirname(os.path.abspath(__file__));FILE=os.path.join(H,'work','cache.json')
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
_kicad=None
def kicad_version():
    global _kicad
    if _kicad is None: _kicad=subprocess.run([KC,'version'],capture_output=True,text=True).stdout.strip()
    return _kicad
def digest(*paths,extra=''):
    h=hashlib.sha1(extra.encode())
    for p in paths:
        h.update(p.encode())
        try: h.update(open(p,'rb').read())
        except OSError: h.update(b'<missing>')
    return h.hexdigest()
class Cache:
    def __init__(self,name,script):
        self.off='--no-cache' in sys.argv;self.name=name
        self.salt=hashlib.sha1(open(script,'rb').read()).hexdigest()+kicad_version()
        try: self.all=json.load(open(FILE))
        except (OSError,ValueError): self.all={}
        self.d=self.all.setdefault(name,{});self.hits=self.misses=0
    def get(self,key,fn):
        """fn() computes the value when the key is new; values must be JSON."""
        k=hashlib.sha1((self.salt+key).encode()).hexdigest()
        if not self.off and k in self.d: self.hits+=1;return self.d[k]
        self.misses+=1;v=fn();self.d[k]=v;return v
    def save(self):
        try: cur=json.load(open(FILE))
        except (OSError,ValueError): cur={}
        cur[self.name]=self.d;os.makedirs(os.path.dirname(FILE),exist_ok=True);json.dump(cur,open(FILE+'.tmp','w'));os.replace(FILE+'.tmp',FILE)
