# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

from .geometry import Rectangle


class PackingAlgorithm(object):
                                     

    def __init__(self, width, height, rot=True, bid=None, *args, **kwargs):
                   
        self.width = width
        self.height = height
        self.rot = rot
        self.rectangles = []
        self.bid = bid
        self._surface = Rectangle(0, 0, width, height)
        self.reset()

    def __len__(self):
        return len(self.rectangles)

    def __iter__(self):
        return iter(self.rectangles)

    def _fits_surface(self, width, height):
                   
        assert(width > 0 and height > 0)
        if self.rot and (width > self.width or height > self.height):
            width, height = height, width

        if width > self.width or height > self.height:
            return False
        else:
            return True
    
    def __getitem__(self, key):
                   
        return self.rectangles[key]

    def used_area(self):
                   
        return sum(r.area() for r in self)

    def fitness(self, width, height, rot = False):
                   
        raise NotImplementedError
        
    def add_rect(self, width, height, rid=None):
                   
        raise NotImplementedError

    def rect_list(self):
                   
        rectangle_list = []
        for r in self:
            rectangle_list.append((r.x, r.y, r.width, r.height, r.rid))

        return rectangle_list

    def validate_packing(self):
                   
        surface = Rectangle(0, 0, self.width, self.height)

        for r in self:
            if not surface.contains(r):
                raise Exception("Rectangle placed outside surface")

        
        rectangles = [r for r in self]
        if len(rectangles) <= 1:
            return

        for r1 in range(0, len(rectangles)-2):
            for r2 in range(r1+1, len(rectangles)-1):
                if rectangles[r1].intersects(rectangles[r2]):
                    raise Exception("Rectangle collision detected")

    def is_empty(self):
                                                        
        return not bool(len(self))

    def reset(self):
        self.rectangles = []                                



