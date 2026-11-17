"""The label each revision carries (KICAD.md K16): Tested, Proven design or Untested, with a one-line reason.

The data is `labels` in Tools/data/orders.json. A revision whose `tested` entry starts with "Yes" is Tested unless `labels` says
otherwise; every other revision must be in `labels`. register.py (REVISIONS.md and the README's "Which revision to
make") and Tools/bom/gen_bom.py (BOM.md) read it through this module, so the three can't disagree. A reason is public
text, so it may not cite the owner's plans (common.PLAN_REF)."""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,PLAN_REF,files,load,save
O=load('orders.json')
NAMES=('Tested','Proven design','Untested')
DEFINE={
    'Tested':'This revision was built and tested.',
    'Proven design':"Not built at this revision, but its circuit is proven. Either it is a tested revision's circuit, or each change copies a circuit built and tested on another board or on the bench, or is a textbook circuit that leaves everything the tested revision does as it was. Any other change is silkscreen text, part values, mounting holes, outline clean-up, parts moved a fraction of a millimetre onto their grid, capacitor pitch, socket outlines, a footprint swap with the same holes, a solder jumper's default, the solder mask or paste at a card edge, or tracks rerouted or pours refilled with DRC and the netlist check passing. A builder can treat it as tested.",
    'Untested':'The circuit, the power path or the layout changed in a way that only a built board proves, or the board has never been built at all.',
}
TESTED='Built and tested'
def label(repo,board,rev):
    """(label, reason). Raises KeyError for a revision with no label."""
    k=f'{repo}|{board}|{rev}';e=O.get('labels',{}).get(k)
    t=O.get('tested',{}).get(k,'')
    if e:
        if e[0] not in NAMES: raise ValueError(f'{k}: {e[0]!r} is not one of {NAMES}')
        if PLAN_REF.search(e[1]): raise ValueError(f'{k}: the reason {e[1]!r} cites the owner\'s plans, which builders can\'t read: say what changed instead')
        if t.startswith('Yes') and e[0]!='Tested':
            raise ValueError(f'{k}: "tested" says {t!r}, but "labels" says {e[0]}. A test that passed makes it Tested: remove its entry from "labels" in Tools/data/orders.json, or say there why not')
        return e[0],e[1]
    if t.startswith('Yes'): return 'Tested',TESTED
    raise KeyError(f'{k} has no label: add it to "labels" in Tools/data/orders.json')
def cell(repo,board,rev):
    """The label in bold, and its reason unless that only repeats the label."""
    n,why=label(repo,board,rev)
    return f'**{n}**' if why==TESTED else f'**{n}**: {lower(why)}'
def lower(s):
    """A reason inside a sentence: 'Mounting holes' becomes 'mounting holes', but 'JP1' and 'A1' stay."""
    return s[0].lower()+s[1:] if len(s)>1 and s[0].isupper() and (s[1].islower() or s[1]==' ') else s
