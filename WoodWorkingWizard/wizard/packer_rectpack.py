# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   
from typing import List, Tuple, Optional, Any
import os
import sys

try:
    import importlib
    rectpack = importlib.import_module('rectpack')
except Exception:              
                             
    rectpack = None                
    try:
        vendor = os.path.join(os.path.dirname(__file__), '_vendor')
        if os.path.isdir(vendor) and vendor not in sys.path:
            sys.path.insert(0, vendor)
            rectpack = importlib.import_module('rectpack')
    except Exception:
        rectpack = None                

from .nesting import Rectangle, Sheet


def is_rectpack_available() -> bool:
                                                                 
    return True


class RectpackAdapter:
    def __init__(self, sheet_width: float, sheet_height: float, kerf: float, edge_margin: float):
        self.sheet_width = float(sheet_width)
        self.sheet_height = float(sheet_height)
        self.kerf = float(kerf)
        self.edge_margin = float(edge_margin)

    def _build_packer(self, usable_w: float, usable_h: float, rotation_allowed: bool, sort_algo: Optional[Any]):
                                                                                            
        packer = rectpack.Packer(
            mode=rectpack.PackingMode.Offline,
            bin_algo=rectpack.BinAlgorithm.BBF,                      
            pack_algo=rectpack.MaxRectsBssf if hasattr(rectpack, 'MaxRectsBssf') else rectpack.SkylineBl,
            rotation=rotation_allowed
        )
                                 
        packer.add_bin(usable_w, usable_h, float('inf'))
                                                                                             
        return packer

    def pack(self, rects: List[Rectangle], rotation_allowed: bool, attempts: int = 12) -> List[Sheet]:
                                                                                 
        if rectpack is not None:
            return self._pack_with_rectpack(rects, rotation_allowed, attempts)
        else:
            return self._pack_with_shelf(rects, rotation_allowed, attempts)

    def _pack_with_rectpack(self, rects: List[Rectangle], rotation_allowed: bool, attempts: int) -> List[Sheet]:
        usable_w = self.sheet_width - 2 * self.edge_margin
        usable_h = self.sheet_height - 2 * self.edge_margin
        if usable_w <= 0 or usable_h <= 0:
            return []

                                                                        
        base: List[Tuple[float, float, int]] = []
        for i, r in enumerate(rects):
            w = max(0.0, float(r.width)) + self.kerf
            h = max(0.0, float(r.height)) + self.kerf
            base.append((w, h, i))

                               
        def by_area(x):
            return x[0] * x[1]

        def by_max_side(x):
            return max(x[0], x[1])

        def by_width(x):
            return x[0]

        def by_height(x):
            return x[1]

        orderings = [
            sorted(base, key=by_area, reverse=True),
            sorted(base, key=by_max_side, reverse=True),
            sorted(base, key=by_width, reverse=True),
            sorted(base, key=by_height, reverse=True),
        ]

                                                                                            
        while len(orderings) < attempts:
            orderings.extend(orderings[: max(0, attempts - len(orderings))])

        best_bins = None
        best_score = (10**9, float('inf'))                              
        sheet_area = usable_w * usable_h

        for order in orderings[:attempts]:
            packer = self._build_packer(usable_w, usable_h, rotation_allowed, sort_algo=None)
            for (w, h, idx) in order:
                packer.add_rect(w, h, rid=idx)
            try:
                packer.pack()
            except Exception:
                continue

                                              
            bins = packer.bin_list()
            scrap = 0.0
            for b in bins:
                placed = getattr(b, 'rect_list')() if hasattr(b, 'rect_list') else []
                used = 0.0
                for (x, y, w, h, rid) in placed:
                    used += (w * h)
                scrap += max(0.0, sheet_area - used)
            score = (len(bins), scrap)
            if score < best_score:
                best_score = score
                best_bins = bins

        if not best_bins:
            return []

                                       
        sheets_out: List[Sheet] = []
        for b in best_bins:
            sh = Sheet(self.sheet_width, self.sheet_height)
            sh.free_rectangles = []
            sh.rectangles = []
            placed = getattr(b, 'rect_list')() if hasattr(b, 'rect_list') else []
            for (x, y, w_inf, h_inf, rid) in placed:
                src = rects[rid]
                r = Rectangle(src.width, src.height, src.name, src.component, src.rotation_allowed and rotation_allowed, src.original_body)
                                                                                                       
                rotated = False
                                                                                      
                                                                              
                if abs((w_inf - self.kerf) - src.height) < 1e-6 and abs((h_inf - self.kerf) - src.width) < 1e-6:
                    rotated = True
                r.rotated = rotated
                if rotated:
                    r.width, r.height = src.height, src.width
                                                                                   
                r.x = float(x) + self.edge_margin
                r.y = float(y) + self.edge_margin
                sh.add_rectangle(r)
            sheets_out.append(sh)

        return sheets_out

    def _pack_with_shelf(self, rects: List[Rectangle], rotation_allowed: bool, attempts: int) -> List[Sheet]:
                                                                                              
        usable_w = self.sheet_width - 2 * self.edge_margin
        usable_h = self.sheet_height - 2 * self.edge_margin
        if usable_w <= 0 or usable_h <= 0:
            return []

        base: List[Tuple[float, float, int]] = []
        for i, r in enumerate(rects):
            base.append((max(0.0, float(r.width)), max(0.0, float(r.height)), i))

        def by_area(x):
            return x[0] * x[1]
        def by_max_side(x):
            return max(x[0], x[1])
        def by_width(x):
            return x[0]
        def by_height(x):
            return x[1]

        orders = [
            sorted(base, key=by_area, reverse=True),
            sorted(base, key=by_max_side, reverse=True),
            sorted(base, key=by_width, reverse=True),
            sorted(base, key=by_height, reverse=True),
        ]
        while len(orders) < attempts:
            orders.extend(orders[: max(0, attempts - len(orders))])

        def pack_once(order: List[Tuple[float, float, int]]):
            sheets: List[dict] = []
                                                                  
            current = None
            for (w0, h0, idx) in order:
                placed = False
                for s in sheets:
                                                                          
                    for shelf in s['shelves']:
                                                          
                        candidates = [(w0, h0, False)]
                        if rotation_allowed:
                            candidates.append((h0, w0, True))
                        best = None
                        for (w, h, rot) in candidates:
                            if w + (self.kerf if shelf['x'] > 0 else 0) <= usable_w - shelf['x'] and h <= shelf['height']:
                                               
                                best = (w, h, rot)
                                break
                        if best:
                            w, h, rot = best
                            x = shelf['x'] + (self.kerf if shelf['x'] > 0 else 0)
                            y = shelf['y']
                            shelf['x'] = x + w
                            s['items'].append((x, y, w, h, idx, rot))
                            placed = True
                            break
                    if placed:
                        break
                                                  
                                                    
                    y_new = 0.0
                    for sh in s['shelves']:
                        y_new = max(y_new, sh['y'] + sh['height'] + self.kerf)
                                                                                     
                    candidates = [(w0, h0, False)]
                    if rotation_allowed:
                        candidates.append((h0, w0, True))
                    for (w, h, rot) in candidates:
                        if y_new + h <= usable_h and w <= usable_w:
                            s['shelves'].append({'y': y_new, 'height': h, 'x': w})
                            s['items'].append((0.0, y_new, w, h, idx, rot))
                            placed = True
                            break
                    if placed:
                        break
                if not placed:
                               
                    s = {'shelves': [], 'items': []}
                                          
                    candidates = [(w0, h0, False)]
                    if rotation_allowed:
                        candidates.append((h0, w0, True))
                                                                   
                    chosen = None
                    for (w, h, rot) in candidates:
                        if w <= usable_w and h <= usable_h:
                            chosen = (w, h, rot)
                            break
                    if chosen is None:
                        return []                   
                    w, h, rot = chosen
                    s['shelves'].append({'y': 0.0, 'height': h, 'x': w})
                    s['items'].append((0.0, 0.0, w, h, idx, rot))
                    sheets.append(s)
            return sheets

        best = None
        best_score = (10**9, float('inf'))
        sheet_area = usable_w * usable_h
        for order in orders[:attempts]:
            layout = pack_once(order)
            if not layout:
                continue
            scrap = 0.0
            for s in layout:
                used = sum(w*h for (_, _, w, h, _, _) in s['items'])
                scrap += max(0.0, sheet_area - used)
            score = (len(layout), scrap)
            if score < best_score:
                best_score = score
                best = layout
        if not best:
            return []
                                    
        sheets_out: List[Sheet] = []
        for s in best:
            sh = Sheet(self.sheet_width, self.sheet_height)
            sh.free_rectangles = []
            sh.rectangles = []
            for (x, y, w, h, rid, rot) in s['items']:
                src = rects[rid]
                r = Rectangle(src.width, src.height, src.name, src.component, src.rotation_allowed and rotation_allowed, src.original_body)
                r.rotated = bool(rot)
                if r.rotated:
                    r.width, r.height = src.height, src.width
                r.x = float(x) + self.edge_margin
                r.y = float(y) + self.edge_margin
                sh.add_rectangle(r)
            sheets_out.append(sh)
        return sheets_out
