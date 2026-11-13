#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
"""Runs the Fabrication Toolkit headlessly: toolkit.py BOARD.kicad_pcb

Writes production/ beside the board (run it on a scratch copy, as Tools/regen.py does): the zip, named by the plugin
from the title block, and bom.csv, positions.csv, designators.csv and netlist.ipc.

It runs exactly what the plugin's window runs: the copy KiCad 10 uses, with the settings in options.json, which is
also the fabrication-toolkit-options.json in every revision's folder (production.py --sync). So the window and this
give the same files. It refuses to run if the plugin's files differ from plugin.json. See README.md.
The toolkit calls pcbnew.GetBoard(), which only works in the GUI, so this supplies it."""
import sys, os, json, hashlib, importlib
H = os.path.dirname(os.path.abspath(__file__))
PIN = json.load(open(os.path.join(H, 'plugin.json')))
PLUGIN = os.path.expanduser(PIN['folder'])
bad = [f for f, h in PIN['sha256'].items()
       if not os.path.exists(os.path.join(PLUGIN, f)) or hashlib.sha256(open(os.path.join(PLUGIN, f), 'rb').read()).hexdigest() != h]
if bad:
    raise SystemExit(f'Fabrication Toolkit in {PLUGIN} differs from Tools/production/plugin.json ({", ".join(bad)}): '
                     'see Tools/production/README.md, "Updating the plugin"')
sys.path.insert(0, os.path.dirname(PLUGIN))
import pcbnew
board = pcbnew.LoadBoard(sys.argv[1]); pcbnew.GetBoard = lambda: board; pcbnew.LoadBoard = lambda p: board
pk = os.path.basename(PLUGIN)
t = importlib.import_module(pk + '.thread')
opts = json.load(open(os.path.join(H, 'options.json')))
th = t.ProcessThread(wx=None, cli=sys.argv[1], options=opts, openBrowser=False, nonInteractive=True)
th.join()
print('toolkit done')
sys.stdout.flush()
os._exit(0)   # skip pcbnew's teardown, which can crash outside the app (Tools/README.md, "Scripting a board with pcbnew")
