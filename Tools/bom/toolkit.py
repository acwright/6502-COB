#!/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
"""Runs the Fabrication Toolkit headlessly: toolkit.py BOARD.kicad_pcb ARCHIVE_NAME. Writes production/ beside a scratch copy of the board.
The toolkit calls pcbnew.GetBoard(), which only works in the GUI, so this supplies it."""
import sys,os,importlib
sys.path.insert(0,os.path.expanduser('~/Documents/KiCad/9.0/3rdparty/plugins'))
import pcbnew
board=pcbnew.LoadBoard(sys.argv[1]);pcbnew.GetBoard=lambda:board;pcbnew.LoadBoard=lambda p:board
pk='com_github_bennymeg_JLC-Plugin-for-KiCad'
o=importlib.import_module(pk+'.options');t=importlib.import_module(pk+'.thread')
opts={o.AUTO_TRANSLATE_OPT:False,o.AUTO_FILL_OPT:False,o.EXCLUDE_DNP_OPT:True,o.EXTEND_EDGE_CUT_OPT:False,o.ALTERNATIVE_EDGE_CUT_OPT:False,o.ALL_ACTIVE_LAYERS_OPT:False,o.ARCHIVE_NAME:sys.argv[2],o.EXTRA_LAYERS:None,o.NO_BACKUP_OPT:True}
th=t.ProcessThread(wx=None,cli=sys.argv[1],options=opts,openBrowser=False,nonInteractive=True)
th.join()
print('toolkit done')
