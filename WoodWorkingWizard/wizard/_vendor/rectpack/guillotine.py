# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

from .pack_algo import PackingAlgorithm
from .geometry import Rectangle
import itertools
import operator


class Guillotine(PackingAlgorithm):
           
    def __init__(self, width, height, rot=True, merge=True, *args, **kwargs):
                   
        self._merge = merge
        super(Guillotine, self).__init__(width, height, rot, *args, **kwargs)
        

    def _add_section(self, section):
                   
        section.rid = 0     
        plen = 0

        while self._merge and self._sections and plen != len(self._sections):
            plen = len(self._sections)
            self._sections = [s for s in self._sections if not section.join(s)]
        self._sections.append(section)


    def _split_horizontal(self, section, width, height):
                   
                                                                  
                                                                  
                                                     
                                       

                                                                        
        if height < section.height:
            self._add_section(Rectangle(section.x, section.y+height,
                section.width, section.height-height))

        if width < section.width:
            self._add_section(Rectangle(section.x+width, section.y,
                section.width-width, height))


    def _split_vertical(self, section, width, height):
                   
                                                                   
                                                        
        if height < section.height:
            self._add_section(Rectangle(section.x, section.y+height,
                width, section.height-height))
        
        if width < section.width:
            self._add_section(Rectangle(section.x+width, section.y,
                section.width-width, section.height))
        

    def _split(self, section, width, height):
                   
        raise NotImplementedError


    def _section_fitness(self, section, width, height):
                   
        raise NotImplementedError

    def _select_fittest_section(self, w, h):
                   
        fitn = ((self._section_fitness(s, w, h), s, False) for s in self._sections 
                if self._section_fitness(s, w, h) is not None)
        fitr = ((self._section_fitness(s, h, w), s, True) for s in self._sections 
                if self._section_fitness(s, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)
        
        try:
            _, sec, rot = min(fit, key=operator.itemgetter(0))
        except ValueError:
            return None, None

        return sec, rot


    def add_rect(self, width, height, rid=None):     
                   
        assert(width > 0 and height >0)

                                                         
        section, rotated = self._select_fittest_section(width, height)
        if not section:
            return None
        
        if rotated:
            width, height = height, width
        
                                                 
        self._sections.remove(section)
        self._split(section, width, height)
       
                                                  
        rect = Rectangle(section.x, section.y, width, height, rid)
        self.rectangles.append(rect)
        return rect

    def fitness(self, width, height):
                   
        assert(width > 0 and height > 0)

                                   
        section, rotated = self._select_fittest_section(width, height)
        if not section:
            return None
        
                                                                             
                                    
        if rotated:
            return self._section_fitness(section, height, width)
        else:
            return self._section_fitness(section, width, height)

    def reset(self):
        super(Guillotine, self).reset()
        self._sections = []
        self._add_section(Rectangle(0, 0, self.width, self.height))



class GuillotineBaf(Guillotine):
           
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return section.area()-width*height


class GuillotineBlsf(Guillotine):
           
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return max(section.width-width, section.height-height)


class GuillotineBssf(Guillotine):
           
    def _section_fitness(self, section, width, height):
        if width > section.width or height > section.height:
            return None
        return min(section.width-width, section.height-height)


class GuillotineSas(Guillotine):
           
    def _split(self, section, width, height):
        if section.width < section.height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineLas(Guillotine):
           
    def _split(self, section, width, height):
        if section.width >= section.height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)



class GuillotineSlas(Guillotine):
           
    def _split(self, section, width, height):
        if section.width-width < section.height-height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineLlas(Guillotine):
           
    def _split(self, section, width, height):
        if section.width-width >= section.height-height:
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)



class GuillotineMaxas(Guillotine):
           
    def _split(self, section, width, height):
        if width*(section.height-height) <= height*(section.width-width):
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
        


class GuillotineMinas(Guillotine):
           
    def _split(self, section, width, height):
        if width*(section.height-height) >= height*(section.width-width):
            return self._split_horizontal(section, width, height)
        else:
            return self._split_vertical(section, width, height)
       


                                                            
                                         
class GuillotineBssfSas(GuillotineBssf, GuillotineSas):
    pass
class GuillotineBssfLas(GuillotineBssf, GuillotineLas):
    pass
class GuillotineBssfSlas(GuillotineBssf, GuillotineSlas):
    pass
class GuillotineBssfLlas(GuillotineBssf, GuillotineLlas):
    pass
class GuillotineBssfMaxas(GuillotineBssf, GuillotineMaxas):
    pass
class GuillotineBssfMinas(GuillotineBssf, GuillotineMinas):
    pass
class GuillotineBlsfSas(GuillotineBlsf, GuillotineSas):
    pass
class GuillotineBlsfLas(GuillotineBlsf, GuillotineLas):
    pass
class GuillotineBlsfSlas(GuillotineBlsf, GuillotineSlas):
    pass
class GuillotineBlsfLlas(GuillotineBlsf, GuillotineLlas):
    pass
class GuillotineBlsfMaxas(GuillotineBlsf, GuillotineMaxas):
    pass
class GuillotineBlsfMinas(GuillotineBlsf, GuillotineMinas):
    pass
class GuillotineBafSas(GuillotineBaf, GuillotineSas):
    pass
class GuillotineBafLas(GuillotineBaf, GuillotineLas):
    pass
class GuillotineBafSlas(GuillotineBaf, GuillotineSlas):
    pass
class GuillotineBafLlas(GuillotineBaf, GuillotineLlas):
    pass
class GuillotineBafMaxas(GuillotineBaf, GuillotineMaxas):
    pass
class GuillotineBafMinas(GuillotineBaf, GuillotineMinas):
    pass



