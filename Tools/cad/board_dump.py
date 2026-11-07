#!/usr/bin/env python3
"""Writes what the CAD tools need from one PCB as JSON on stdout. Run with KiCad's bundled Python, which has pcbnew:

  board_dump.py BOARD.kicad_pcb

Everything is in mm, in the PCB file's own frame (x right, y down).
  edge      the board's outline as one polygon, and its bounding box (without the edge line's width)
  holes     every mounting hole: reference, centre, drill
  radius    the largest arc on the outline: the corner radius
  zones     every named rule area: its name and box
  parts     every footprint: reference, value, side, position, rotation, the box round its pads, its courtyard's box,
            and the box round everything it draws on the fab and silkscreen layers
"""
import json, sys
import pcbnew

keep = []


def box(b):
    return [round(b.GetLeft() / 1e6, 4), round(b.GetTop() / 1e6, 4), round(b.GetRight() / 1e6, 4), round(b.GetBottom() / 1e6, 4)]


def main(path):
    b = pcbnew.LoadBoard(path)
    keep.append(b)
    w0 = max([d.GetWidth() for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts] or [0])
    e = b.GetBoardEdgesBoundingBox()
    edge_box = [round((e.GetLeft() + w0 / 2) / 1e6, 4), round((e.GetTop() + w0 / 2) / 1e6, 4),
                round((e.GetRight() - w0 / 2) / 1e6, 4), round((e.GetBottom() - w0 / 2) / 1e6, 4)]
    sps = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(sps, True)
    outlines = []
    for i in range(sps.OutlineCount()):
        ol = sps.Outline(i)
        outlines.append([[round(ol.CPoint(j).x / 1e6, 4), round(ol.CPoint(j).y / 1e6, 4)] for j in range(ol.PointCount())])
    holes, parts = [], []
    for f in b.GetFootprints():
        ref = f.GetReference()
        lib = str(f.GetFPID().GetLibNickname())
        pads = list(f.Pads())
        big = [p for p in pads if 2.9e6 <= p.GetDrillSize().x <= 3.6e6
               and p.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH)]
        if lib == 'MountingHole' or (ref.upper().startswith(('H', 'MH')) and len(big) == 1 and len(pads) <= 9):
            p = f.GetPosition()
            d = max([q.GetDrillSize().x for q in pads] or [0])
            holes.append({'ref': ref, 'x': round(p.x / 1e6, 4), 'y': round(p.y / 1e6, 4), 'drill': round(d / 1e6, 4)})
            continue
        pb = None
        for q in pads:
            bb = q.GetBoundingBox()
            if pb is None:
                pb = bb
            else:
                pb.Merge(bb)
        cy = None
        for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            try:
                c = f.GetCourtyard(layer)
                if c.OutlineCount():
                    cb = c.BBox()
                    cy = [round(cb.GetLeft() / 1e6, 4), round(cb.GetTop() / 1e6, 4), round(cb.GetRight() / 1e6, 4), round(cb.GetBottom() / 1e6, 4)]
                    break
            except Exception:
                pass
        drawn = None
        for g in f.GraphicalItems():
            if g.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab, pcbnew.F_SilkS, pcbnew.B_SilkS) and g.GetClass() != 'PCB_TEXT':
                bb = g.GetBoundingBox()
                if drawn is None:
                    drawn = bb
                else:
                    drawn.Merge(bb)
        p = f.GetPosition()
        parts.append({'ref': ref, 'value': f.GetValue(), 'fpid': f.GetFPIDAsString(), 'side': 'B' if f.IsFlipped() else 'F',
                      'x': round(p.x / 1e6, 4), 'y': round(p.y / 1e6, 4), 'rot': round(f.GetOrientationDegrees(), 3),
                      'pads': box(pb) if pb else None, 'courtyard': cy, 'drawn': box(drawn) if drawn else None,
                      'models': [m.m_Filename for m in f.Models() if m.m_Show]})
    zones = []
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName():
            zb = z.GetBoundingBox()
            zones.append({'name': z.GetZoneName(), 'box': box(zb)})
    radius = max([round(d.GetRadius() / 1e6, 4) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_ARC] or [0])
    thick = round(b.GetDesignSettings().GetBoardThickness() / 1e6, 4)
    json.dump({'path': path, 'edge_box': edge_box, 'outlines': outlines, 'thickness': thick, 'radius': radius, 'zones': zones, 'holes': holes, 'parts': parts}, sys.stdout)


main(sys.argv[1])
