# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

from .maxrects import MaxRectsBssf

import operator
import itertools
import collections

import decimal

                         
def float2dec(ft, decimal_digits):
           
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_UP
        places = decimal.Decimal(10)**(-decimal_digits)
        return decimal.Decimal.from_float(float(ft)).quantize(places)


                                   
SORT_AREA  = lambda rectlist: sorted(rectlist, reverse=True, 
        key=lambda r: r[0]*r[1])               

SORT_PERI  = lambda rectlist: sorted(rectlist, reverse=True, 
        key=lambda r: r[0]+r[1])                    

SORT_DIFF  = lambda rectlist: sorted(rectlist, reverse=True, 
        key=lambda r: abs(r[0]-r[1]))               

SORT_SSIDE = lambda rectlist: sorted(rectlist, reverse=True, 
        key=lambda r: (min(r[0], r[1]), max(r[0], r[1])))                     

SORT_LSIDE = lambda rectlist: sorted(rectlist, reverse=True, 
        key=lambda r: (max(r[0], r[1]), min(r[0], r[1])))                    

SORT_RATIO = lambda rectlist: sorted(rectlist, reverse=True,
        key=lambda r: r[0]/r[1])                     

SORT_NONE = lambda rectlist: list(rectlist)           



class BinFactory(object):

    def __init__(self, width, height, count, pack_algo, *args, **kwargs):
        self._width = width
        self._height = height
        self._count = count
        
        self._pack_algo = pack_algo
        self._algo_kwargs = kwargs
        self._algo_args = args
        self._ref_bin = None                                          
        
        self._bid = kwargs.get("bid", None)

    def _create_bin(self):
        return self._pack_algo(self._width, self._height, *self._algo_args, **self._algo_kwargs)

    def is_empty(self):
        return self._count<1

    def fitness(self, width, height):
        if not self._ref_bin:
            self._ref_bin = self._create_bin()

        return self._ref_bin.fitness(width, height)

    def fits_inside(self, width, height):
                                                                     
        if not self._ref_bin:
            self._ref_bin = self._create_bin()

        return self._ref_bin._fits_surface(width, height)

    def new_bin(self):
        if self._count > 0:
            self._count -= 1
            return self._create_bin()
        else:
            return None

    def __eq__(self, other):
        return self._width*self._height == other._width*other._height

    def __lt__(self, other):
        return self._width*self._height < other._width*other._height

    def __str__(self):
        return "Bin: {} {} {}".format(self._width, self._height, self._count)



class PackerBNFMixin(object):
           

    def add_rect(self, width, height, rid=None):
        while True:
                                                              
            if len(self._open_bins)==0:
                                                                       
                new_bin = self._new_open_bin(width, height, rid=rid)
                if new_bin is None:
                    return None

                                                                              
            rect = self._open_bins[0].add_rect(width, height, rid=rid)
            if rect is not None:
                return rect

                                                                      
            closed_bin = self._open_bins.popleft()
            self._closed_bins.append(closed_bin)


class PackerBFFMixin(object):
           
 
    def add_rect(self, width, height, rid=None):
                                                           
        for b in self._open_bins:
            rect = b.add_rect(width, height, rid=rid)
            if rect is not None:
                return rect

        while True:
                                                                   
            new_bin = self._new_open_bin(width, height, rid=rid)
            if new_bin is None:
                return None

                                                              
                                        
            rect = new_bin.add_rect(width, height, rid=rid)
            if rect is not None:
                return rect


class PackerBBFMixin(object):
           

                                  
    first_item = operator.itemgetter(0)

    def add_rect(self, width, height, rid=None):
 
                                    
        fit = ((b.fitness(width, height),  b) for b in self._open_bins)
        fit = (b for b in fit if b[0] is not None)
        try:
            _, best_bin = min(fit, key=self.first_item)
            best_bin.add_rect(width, height, rid)
            return True
        except ValueError:
            pass    

                                                
        while True:
                                                                   
            new_bin = self._new_open_bin(width, height, rid=rid)
            if new_bin is None:
                return False

                                                              
                                        
            if new_bin.add_rect(width, height, rid):
                return True



class PackerOnline(object):
           

    def __init__(self, pack_algo=MaxRectsBssf, rotation=True):
                   
        self._rotation = rotation
        self._pack_algo = pack_algo
        self.reset()

    def __iter__(self):
        return itertools.chain(self._closed_bins, self._open_bins)

    def __len__(self):
        return len(self._closed_bins)+len(self._open_bins)
    
    def __getitem__(self, key):
                   
        if not isinstance(key, int):
            raise TypeError("Indices must be integers")

        size = len(self)                       

        if key < 0:
            key += size

        if not 0 <= key < size:
            raise IndexError("Index out of range")
        
        if key < len(self._closed_bins):
            return self._closed_bins[key]
        else:
            return self._open_bins[key-len(self._closed_bins)]

    def _new_open_bin(self, width=None, height=None, rid=None):
                   
        factories_to_delete = set()  
        new_bin = None

        for key, binfac in self._empty_bins.items():

                                                       
                                                                         
            if not binfac.fits_inside(width, height):
                continue
           
                                             
            new_bin = binfac.new_bin()
            if new_bin is None:
                continue
            self._open_bins.append(new_bin)

                                                           
            if binfac.is_empty():
                factories_to_delete.add(key)
       
            break

                                 
        for f in factories_to_delete:
            del self._empty_bins[f]

        return new_bin 

    def add_bin(self, width, height, count=1, **kwargs):
                                                                
        kwargs['rot'] = self._rotation
        bin_factory = BinFactory(width, height, count, self._pack_algo, **kwargs)
        self._empty_bins[next(self._bin_count)] = bin_factory

    def rect_list(self):
        rectangles = []
        bin_count = 0

        for abin in self:
            for rect in abin:
                rectangles.append((bin_count, rect.x, rect.y, rect.width, rect.height, rect.rid))
            bin_count += 1

        return rectangles

    def bin_list(self):
                   
        return [(b.width, b.height) for b in self]

    def validate_packing(self):
        for b in self:
            b.validate_packing()

    def reset(self): 
                                       
        self._closed_bins = collections.deque()

                                       
        self._open_bins = collections.deque()

                                               
        self._empty_bins = collections.OrderedDict()                                  
        self._bin_count = itertools.count()


class Packer(PackerOnline):
           

    def __init__(self, pack_algo=MaxRectsBssf, sort_algo=SORT_NONE, 
            rotation=True):
                   
        super(Packer, self).__init__(pack_algo=pack_algo, rotation=rotation)
        
        self._sort_algo = sort_algo

                                           
        self._avail_bins = collections.deque()
        self._avail_rect = collections.deque()

                                      
        self._sorted_rect = []

    def add_bin(self, width, height, count=1, **kwargs):
        self._avail_bins.append((width, height, count, kwargs))

    def add_rect(self, width, height, rid=None):
        self._avail_rect.append((width, height, rid))

    def _is_everything_ready(self):
        return self._avail_rect and self._avail_bins

    def pack(self):

        self.reset()

        if not self._is_everything_ready():
                                                  
            return

                                      
        for b in self._avail_bins:
            width, height, count, extra_kwargs = b
            super(Packer, self).add_bin(width, height, count, **extra_kwargs)

                                    
        self._sorted_rect = self._sort_algo(self._avail_rect)

                       
        for r in self._sorted_rect:
            super(Packer, self).add_rect(*r)


 
class PackerBNF(Packer, PackerBNFMixin):
           
    pass

class PackerBFF(Packer, PackerBFFMixin):
           
    pass
    
class PackerBBF(Packer, PackerBBFMixin):
           
    pass 

class PackerOnlineBNF(PackerOnline, PackerBNFMixin):
           
    pass 

class PackerOnlineBFF(PackerOnline, PackerBFFMixin):
           
    pass

class PackerOnlineBBF(PackerOnline, PackerBBFMixin):
           
    pass


class PackerGlobal(Packer, PackerBNFMixin):
           
    first_item = operator.itemgetter(0)
    
    def __init__(self, pack_algo=MaxRectsBssf, rotation=True):
                   
        super(PackerGlobal, self).__init__(pack_algo=pack_algo,
            sort_algo=SORT_NONE, rotation=rotation)

    def _find_best_fit(self, pbin):
                   
        fit = ((pbin.fitness(r[0], r[1]), k) for k, r in self._sorted_rect.items())
        fit = (f for f in fit if f[0] is not None)
        try:
            _, rect = min(fit, key=self.first_item)
            return rect
        except ValueError:
            return None


    def _new_open_bin(self, remaining_rect):
                   
        factories_to_delete = set()  
        new_bin = None

        for key, binfac in self._empty_bins.items():

                                                                       
                                    
            a_rectangle_fits = False
            for _, rect in remaining_rect.items():
                if binfac.fits_inside(rect[0], rect[1]):
                    a_rectangle_fits = True
                    break

            if not a_rectangle_fits:
                factories_to_delete.add(key)
                continue
           
                                             
            new_bin = binfac.new_bin()
            if new_bin is None:
                continue
            self._open_bins.append(new_bin)

                                                           
            if binfac.is_empty():
                factories_to_delete.add(key)
       
            break

                                 
        for f in factories_to_delete:
            del self._empty_bins[f]

        return new_bin 

    def pack(self):
       
        self.reset()

        if not self._is_everything_ready():
            return
        
                                      
        for b in self._avail_bins:
            width, height, count, extra_kwargs = b
            super(Packer, self).add_bin(width, height, count, **extra_kwargs)
    
                                                      
        self._sorted_rect = collections.OrderedDict(
                enumerate(self._sort_algo(self._avail_rect)))
        
                                                                                    
                                                                                        
                                                                                     
                    
        while len(self._sorted_rect) > 0:

                                                                             
            pbin = self._new_open_bin(self._sorted_rect)
            if pbin is None:
                break

                                                                   
            while True:
              
                                          
                best_rect_key = self._find_best_fit(pbin)
                if best_rect_key is None:
                    closed_bin = self._open_bins.popleft()
                    self._closed_bins.append(closed_bin)
                    break                                                             

                best_rect = self._sorted_rect[best_rect_key]
                del self._sorted_rect[best_rect_key]

                PackerBNFMixin.add_rect(self, *best_rect)





                
class Enum(tuple): 
    __getattr__ = tuple.index

PackingMode = Enum(["Online", "Offline"])
PackingBin = Enum(["BNF", "BFF", "BBF", "Global"])


def newPacker(mode=PackingMode.Offline, 
         bin_algo=PackingBin.BBF, 
        pack_algo=MaxRectsBssf,
        sort_algo=SORT_AREA, 
        rotation=True):
           
    packer_class = None

                 
    if mode == PackingMode.Online:
        sort_algo=None
        if bin_algo == PackingBin.BNF:
            packer_class = PackerOnlineBNF
        elif bin_algo == PackingBin.BFF:
            packer_class = PackerOnlineBFF
        elif bin_algo == PackingBin.BBF:
            packer_class = PackerOnlineBBF
        else:
            raise AttributeError("Unsupported bin selection heuristic")

                  
    elif mode == PackingMode.Offline:
        if bin_algo == PackingBin.BNF:
            packer_class = PackerBNF
        elif bin_algo == PackingBin.BFF:
            packer_class = PackerBFF
        elif bin_algo == PackingBin.BBF:
            packer_class = PackerBBF
        elif bin_algo == PackingBin.Global:
            packer_class = PackerGlobal
            sort_algo=None
        else:
            raise AttributeError("Unsupported bin selection heuristic")

    else:
        raise AttributeError("Unknown packing mode.")

    if sort_algo:
        return packer_class(pack_algo=pack_algo, sort_algo=sort_algo, 
            rotation=rotation)
    else:
        return packer_class(pack_algo=pack_algo, rotation=rotation)


