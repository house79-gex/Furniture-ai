# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

import collections
import itertools
import operator
import heapq
import copy
from .pack_algo import PackingAlgorithm
from .geometry import Point as P
from .geometry import HSegment, Rectangle
from .waste import WasteManager


class Skyline(PackingAlgorithm):
           

    def __init__(self, width, height, rot=True, *args, **kwargs):
                   
        self._waste_management = False
        self._waste = WasteManager(rot=rot)
        super(Skyline, self).__init__(width, height, rot, merge=False, *args, **kwargs)

    def _placement_points_generator(self, skyline, width):
                    
        skyline_r = skyline[-1].right
        skyline_l = skyline[0].left

                                                     
        ppointsl = (s.left for s in skyline if s.left+width <= skyline_r)

                                                      
        ppointsr = (s.right-width for s in skyline if s.right-width >= skyline_l)

                         
        return heapq.merge(ppointsl, ppointsr)

    def _generate_placements(self, width, height):
                   
        skyline = self._skyline

        points = collections.deque()

        left_index = right_index = 0                                    
        support_height = skyline[0].top
        support_index = 0 
    
        placements = self._placement_points_generator(skyline, width)
        for p in placements:

                                                                         
            if p+width > skyline[right_index].right:
                for right_index in range(right_index+1, len(skyline)):
                    if skyline[right_index].top >= support_height:
                        support_index = right_index
                        support_height = skyline[right_index].top
                    if p+width <= skyline[right_index].right:
                        break
                
                                           
            if p >= skyline[left_index].right:
                left_index +=1
           
                                                                   
            if support_index < left_index:
                support_index = left_index
                support_height = skyline[left_index].top
                for i in range(left_index, right_index+1):
                    if skyline[i].top >= support_height:
                        support_index = i
                        support_height = skyline[i].top

                                                           
            if support_height+height <= self.height:
                points.append((Rectangle(p, support_height, width, height),                    left_index, right_index))

        return points

    def _merge_skyline(self, skylineq, segment):
                   
        if len(skylineq) == 0:
            skylineq.append(segment)
            return

        if skylineq[-1].top == segment.top:
            s = skylineq[-1]
            skylineq[-1] = HSegment(s.start, s.length+segment.length)
        else:
            skylineq.append(segment)

    def _add_skyline(self, rect):
                   
        skylineq = collections.deque([])                               
        
        for sky in self._skyline:
            if sky.right <= rect.left or sky.left >= rect.right:
                self._merge_skyline(skylineq, sky)
                continue

            if sky.left < rect.left and sky.right > rect.left:
                                                              
                self._merge_skyline(skylineq, 
                        HSegment(sky.start, rect.left-sky.left))
                sky = HSegment(P(rect.left, sky.top), sky.right-rect.left)
            
            if sky.left < rect.right:
                if sky.left == rect.left:
                    self._merge_skyline(skylineq, 
                        HSegment(P(rect.left, rect.top), rect.width))
                                                               
                if sky.right > rect.right:
                    self._merge_skyline(skylineq, 
                        HSegment(P(rect.right, sky.top), sky.right-rect.right))
                    sky = HSegment(sky.start, rect.right-sky.left)
            
            if sky.left >= rect.left and sky.right <= rect.right:
                                                                               
                if self._waste_management and sky.top < rect.bottom:
                    self._waste.add_waste(sky.left, sky.top, 
                        sky.length, rect.bottom - sky.top)
            else:
                         
                self._merge_skyline(skylineq, sky)

                            
        self._skyline = list(skylineq)

    def _rect_fitness(self, rect, left_index, right_index):
        return rect.top

    def _select_position(self, width, height):
                   
        positions = self._generate_placements(width, height)
        if self.rot and width != height:
            positions += self._generate_placements(height, width)
        if not positions:
            return None, None
        return min(((p[0], self._rect_fitness(*p))for p in positions), 
                key=operator.itemgetter(1))

    def fitness(self, width, height):
                   
        assert(width > 0 and height >0)
        if width > max(self.width, self.height) or            height > max(self.height, self.width):
            return None

                                                          
        if self._waste_management:
            if self._waste.fitness(width, height) is not None:
                return 0

                                                                 
                                                   
        rect, fitness = self._select_position(width, height)
        return fitness

    def add_rect(self, width, height, rid=None):
                   
        assert(width > 0 and height > 0)
        if width > max(self.width, self.height) or            height > max(self.height, self.width):
            return None

        rect = None
                                                                               
        if self._waste_management:
            rect = self._waste.add_rect(width, height, rid)

                                              
        if not rect:
            rect, _ = self._select_position(width, height)
            if rect:
                self._add_skyline(rect)

        if rect is None:
            return None
        
                                                  
        rect.rid = rid
        self.rectangles.append(rect)
        return rect

    def reset(self):
        super(Skyline, self).reset()
        self._skyline = [HSegment(P(0, 0), self.width)]
        self._waste.reset()




class SkylineWMixin(Skyline):
                               
    def __init__(self, width, height, *args, **kwargs):
        super(SkylineWMixin, self).__init__(width, height, *args, **kwargs)
        self._waste_management = True


class SkylineMwf(Skyline):
           
    def _rect_fitness(self, rect, left_index, right_index):
        waste = 0
        for seg in self._skyline[left_index:right_index+1]:
            waste +=                (min(rect.right, seg.right)-max(rect.left, seg.left)) *                (rect.bottom-seg.top)

        return waste

    def _rect_fitnes2s(self, rect, left_index, right_index):
        waste = ((min(rect.right, seg.right)-max(rect.left, seg.left)) for seg in self._skyline[left_index:right_index+1])
        return sum(waste)

class SkylineMwfl(Skyline):
            
    def _rect_fitness(self, rect, left_index, right_index):
        waste = 0
        for seg in self._skyline[left_index:right_index+1]:
            waste +=                (min(rect.right, seg.right)-max(rect.left, seg.left)) *                (rect.bottom-seg.top)

        return waste*self.width*self.height+rect.top


class SkylineBl(Skyline):
           
    def _rect_fitness(self, rect, left_index, right_index):
        return rect.top




class SkylineBlWm(SkylineBl, SkylineWMixin):
    pass

class SkylineMwfWm(SkylineMwf, SkylineWMixin):
    pass

class SkylineMwflWm(SkylineMwfl, SkylineWMixin):
    pass
