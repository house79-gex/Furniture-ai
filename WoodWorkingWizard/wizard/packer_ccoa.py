# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   
from typing import List, Tuple

from .nesting import Rectangle, Sheet


class CCOAPacker:
    def __init__(self, sheet_width: float, sheet_height: float, kerf: float, edge_margin: float):
        self.sheet_width = float(sheet_width)
        self.sheet_height = float(sheet_height)
        self.kerf = float(kerf)
        self.edge = float(edge_margin)

    def pack(self, rects: List[Rectangle], rotation_allowed: bool, attempts: int = 24) -> List[Sheet]:
        usable_w = self.sheet_width - 2 * self.edge
        usable_h = self.sheet_height - 2 * self.edge
        if usable_w <= 0 or usable_h <= 0:
            return []

                                               
        base: List[Tuple[float, float, int]] = [(float(r.width), float(r.height), i) for i, r in enumerate(rects)]

        def area(x: Tuple[float, float, int]):
            return x[0] * x[1]

        def max_side(x: Tuple[float, float, int]):
            return max(x[0], x[1])

        def by_w(x):
            return x[0]

        def by_h(x):
            return x[1]

        orders: List[List[Tuple[float, float, int]]] = [
            sorted(base, key=area, reverse=True),
            sorted(base, key=max_side, reverse=True),
            sorted(base, key=by_w, reverse=True),
            sorted(base, key=by_h, reverse=True),
        ]
                                           
        while len(orders) < attempts:
            orders.extend(orders[: max(0, attempts - len(orders))])

        best = None
        best_score = (10**9, float('inf'))
        sheet_area = usable_w * usable_h

        for order in orders[:attempts]:
            layout = self._pack_once(order, rects, rotation_allowed, usable_w, usable_h)
            if not layout:
                continue
            scrap = 0.0
            for sh in layout:
                used = sum(r.width * r.height for r in getattr(sh, 'rectangles', []))
                scrap += max(0.0, sheet_area - used)
            score = (len(layout), scrap)
            if score < best_score:
                best_score = score
                best = layout

                                                                             
                                                                               
        if best:
            best = self._consolidate(best, rotation_allowed, usable_w, usable_h)

        return best or []

                           

    def _pack_once(self, order: List[Tuple[float, float, int]], rects: List[Rectangle], rotation_allowed: bool, usable_w: float, usable_h: float) -> List[Sheet]:
        sheets: List[Sheet] = []

                                                                                                     
        pack = self
        class SheetState:
            def __init__(self):
                                                           
                self.sh = Sheet(pack.sheet_width, pack.sheet_height)
                self.sh.free_rectangles = []
                self.sh.rectangles = []
                self.candidates: List[Tuple[float, float]] = [(pack.edge, pack.edge)]

        for (w0, h0, idx) in order:
            placed = False
            for ss in sheets:
                if self._try_place_on_sheet(ss, rects, idx, w0, h0, rotation_allowed, usable_w, usable_h):
                    placed = True
                    break
            if not placed:
                ss = SheetState()
                if not self._try_place_on_sheet(ss, rects, idx, w0, h0, rotation_allowed, usable_w, usable_h):
                    return []                          
                sheets.append(ss)

        return [s.sh for s in sheets]

    def _try_place_on_sheet(self, ss, rects: List[Rectangle], ridx: int, w0: float, h0: float, rotation_allowed: bool, usable_w: float, usable_h: float) -> bool:
                                
        orientations = [(w0, h0, False)]
        if rotation_allowed:
            orientations.append((h0, w0, True))

        best = None
        best_key = None

        for (w, h, rot) in orientations:
            for (cx, cy) in ss.candidates:
                                                                                                                   
                x = cx
                y = cy
                if not self._fits_in_usable(x, y, w, h, usable_w, usable_h):
                    continue
                                          
                if self._overlaps_any(x, y, w, h, ss.sh.rectangles):
                    continue
                                                                                                      
                key = (y, x, (usable_w - (x - self.edge) - w) * (usable_h - (y - self.edge) - h))
                if best_key is None or key < best_key:
                    best_key = key
                    best = (x, y, w, h, rot)

        if best is None:
                                                                                                
            placed = self._try_place_with_scan(ss, rects, ridx, w0, h0, rotation_allowed, usable_w, usable_h)
            return placed

        x, y, w, h, rot = best
        src = rects[ridx]
        r = Rectangle(src.width, src.height, src.name, src.component, src.rotation_allowed, src.original_body)
        r.rotated = rot
        if rot:
            r.width, r.height = src.height, src.width
        r.x = x
        r.y = y
        ss.sh.add_rectangle(r)

                                                                                 
        self._add_candidate(ss, x + w + self.kerf, y, usable_w, usable_h)
        self._add_candidate(ss, x, y + h + self.kerf, usable_w, usable_h)
        self._prune_candidates(ss)
        return True

    def _h_overlap(self, x: float, w: float, r: Rectangle) -> bool:
                                                                          
        return not ((x + w + self.kerf) <= r.x or (r.x + r.width + self.kerf) <= x)

    def _lowest_y_for_x(self, x: float, w: float, h: float, placed: List[Rectangle]) -> float:
        y = self.edge
        for r in placed:
            if self._h_overlap(x, w, r):
                y = max(y, r.y + r.height + self.kerf)
        return y

    def _try_place_with_scan(self, ss, rects: List[Rectangle], ridx: int, w0: float, h0: float, rotation_allowed: bool, usable_w: float, usable_h: float) -> bool:
        orientations = [(w0, h0, False)]
        if rotation_allowed:
            orientations.append((h0, w0, True))

        best = None
        best_key = None

                                                                           
        x_positions = {self.edge}
        for r in ss.sh.rectangles:
            x_positions.add(r.x)
            x_positions.add(r.x + r.width + self.kerf)
        xs = sorted([x for x in x_positions if self.edge <= x <= self.edge + usable_w])

        for (w, h, rot) in orientations:
            for x in xs:
                if x + w > self.edge + usable_w:
                    continue
                y = self._lowest_y_for_x(x, w, h, ss.sh.rectangles)
                if y + h > self.edge + usable_h:
                    continue
                                     
                if self._overlaps_any(x, y, w, h, ss.sh.rectangles):
                    continue
                key = (y, x)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (x, y, w, h, rot)

        if best is None:
            return False

        x, y, w, h, rot = best
        src = rects[ridx]
        r = Rectangle(src.width, src.height, src.name, src.component, src.rotation_allowed, src.original_body)
        r.rotated = rot
        if rot:
            r.width, r.height = src.height, src.width
        r.x = x
        r.y = y
        ss.sh.add_rectangle(r)

                                                         
        self._add_candidate(ss, x + w + self.kerf, y, usable_w, usable_h)
        self._add_candidate(ss, x, y + h + self.kerf, usable_w, usable_h)
        self._prune_candidates(ss)
        return True

    def _fits_in_usable(self, x: float, y: float, w: float, h: float, usable_w: float, usable_h: float) -> bool:
        return (x >= self.edge and y >= self.edge and x + w <= self.edge + usable_w and y + h <= self.edge + usable_h)

    def _overlaps_any(self, x: float, y: float, w: float, h: float, placed: List[Rectangle]) -> bool:
        for r in placed:
            if self._overlap(x, y, w, h, r.x, r.y, r.width, r.height):
                return True
        return False

    def _overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def _add_candidate(self, ss, x: float, y: float, usable_w: float, usable_h: float):
        if x < self.edge or y < self.edge:
            return
        if x > self.edge + usable_w or y > self.edge + usable_h:
            return
        ss.candidates.append((x, y))

    def _prune_candidates(self, ss):
                                                                 
                                                                              
                                                                                             
                                                                                
                                                                                  
        cands = sorted(set(ss.candidates))
        pruned: List[Tuple[float, float]] = []
        for x, y in cands:
            dominated = False
            for x2, y2 in cands:
                if (x2 >= x and y2 >= y) and (x2 > x or y2 > y):
                    dominated = True
                    break
            if not dominated:
                pruned.append((x, y))
        ss.candidates = pruned

                                                 

    def _build_state_from_sheet(self, sh: Sheet):
                                                                                             
        class _SS:
            pass
        ss = _SS()
        ss.sh = sh
        ss.candidates = [(self.edge, self.edge)]
                                                        
        for r in getattr(sh, 'rectangles', []):
            self._add_candidate(ss, r.x + r.width + self.kerf, r.y, self.sheet_width - 2 * self.edge, self.sheet_height - 2 * self.edge)
            self._add_candidate(ss, r.x, r.y + r.height + self.kerf, self.sheet_width - 2 * self.edge, self.sheet_height - 2 * self.edge)
        self._prune_candidates(ss)
        return ss

    def _consolidate(self, sheets: List[Sheet], rotation_allowed: bool, usable_w: float, usable_h: float) -> List[Sheet]:
                                                                                                 
        changed = True
                                              
        while changed:
            changed = False
                                                                             
            i = len(sheets) - 1
            while i > 0 and i < len(sheets):
                donor = sheets[i]
                                                                      
                                                               
                donor_rects = sorted(list(getattr(donor, 'rectangles', [])), key=lambda r: r.width * r.height, reverse=True)
                moved_any = False
                for src in donor_rects:
                    placed = False
                    for j in range(0, i):
                        target = sheets[j]
                        ss = self._build_state_from_sheet(target)
                                                                                         
                        if self._try_place_on_sheet(ss, [src], 0, src.width, src.height, rotation_allowed, usable_w, usable_h):
                                                              
                            try:
                                donor.rectangles.remove(src)
                            except ValueError:
                                pass
                            placed = True
                            moved_any = True
                            changed = True
                            break
                                                                    
                                                                                              
                if len(getattr(donor, 'rectangles', [])) == 0:
                    sheets.pop(i)
                    changed = True
                                                                              
                i -= 1
        return sheets
