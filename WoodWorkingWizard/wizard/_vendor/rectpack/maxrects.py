# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

from .pack_algo import PackingAlgorithm
from .geometry import Rectangle
import itertools
import collections
import operator


first_item = operator.itemgetter(0)



class MaxRects(PackingAlgorithm):

    def __init__(self, width, height, rot=True, *args, **kwargs):
        super(MaxRects, self).__init__(width, height, rot, *args, **kwargs)
   
    def _rect_fitness(self, max_rect, width, height):
                   
        if width <= max_rect.width and height <= max_rect.height:
            return 0
        else:
            return None

    def _select_position(self, w, h): 
                   
        if not self._max_rects:
            return None, None

                          
        fitn = ((self._rect_fitness(m, w, h), w, h, m) for m in self._max_rects 
                if self._rect_fitness(m, w, h) is not None)

                           
        fitr = ((self._rect_fitness(m, h, w), h, w, m) for m in self._max_rects 
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m

    def _generate_splits(self, m, r):
                   
        new_rects = []
        
        if r.left > m.left:
            new_rects.append(Rectangle(m.left, m.bottom, r.left-m.left, m.height))
        if r.right < m.right:
            new_rects.append(Rectangle(r.right, m.bottom, m.right-r.right, m.height))
        if r.top < m.top:
            new_rects.append(Rectangle(m.left, r.top, m.width, m.top-r.top))
        if r.bottom > m.bottom:
            new_rects.append(Rectangle(m.left, m.bottom, m.width, r.bottom-m.bottom))
        
        return new_rects

    def _split(self, rect):
                   
        max_rects = collections.deque()

        for r in self._max_rects:
            if r.intersects(rect):
                max_rects.extend(self._generate_splits(r, rect))
            else:
                max_rects.append(r)

                                       
        self._max_rects = list(max_rects)

    def _remove_duplicates(self):
                   
        contained = set()
        for m1, m2 in itertools.combinations(self._max_rects, 2):
            if m1.contains(m2):
                contained.add(m2)
            elif m2.contains(m1):
                contained.add(m1)
        
                               
        self._max_rects = [m for m in self._max_rects if m not in contained]

    def fitness(self, width, height): 
                   
        assert(width > 0 and height > 0)
        
        rect, max_rect = self._select_position(width, height)
        if rect is None:
            return None

                        
        return self._rect_fitness(max_rect, rect.width, rect.height)

    def add_rect(self, width, height, rid=None):
                   
        assert(width > 0 and height >0)

                                              
        rect, _ = self._select_position(width, height)
        if not rect:
            return None
        
                                                                          
                    
        self._split(rect)
    
                                                   
        self._remove_duplicates()

                                              
        rect.rid = rid
        self.rectangles.append(rect)
        return rect

    def reset(self):
        super(MaxRects, self).reset()
        self._max_rects = [Rectangle(0, 0, self.width, self.height)]




class MaxRectsBl(MaxRects):
    
    def _select_position(self, w, h): 
                   
        fitn = ((m.y+h, m.x, w, h, m) for m in self._max_rects 
                if self._rect_fitness(m, w, h) is not None)
        fitr = ((m.y+w, m.x, h, w, m) for m in self._max_rects 
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m


class MaxRectsBssf(MaxRects):
                                                         
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return min(max_rect.width-width, max_rect.height-height)
           
class MaxRectsBaf(MaxRects):
                                            
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None
        
        return (max_rect.width*max_rect.height)-(width*height)


class MaxRectsBlsf(MaxRects):
                                                        
    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return max(max_rect.width-width, max_rect.height-height)
