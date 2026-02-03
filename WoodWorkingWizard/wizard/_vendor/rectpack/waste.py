# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

from .guillotine import GuillotineBafMinas
from .geometry import Rectangle



class WasteManager(GuillotineBafMinas):

    def __init__(self, rot=True, merge=True, *args, **kwargs):
        super(WasteManager, self).__init__(1, 1, rot=rot, merge=merge, *args, **kwargs)
   
    def add_waste(self, x, y, width, height):
                                   
        self._add_section(Rectangle(x, y, width, height))

    def _fits_surface(self, width, height):
        raise NotImplementedError

    def validate_packing(self):
        raise NotImplementedError

    def reset(self):
        super(WasteManager, self).reset()
        self._sections = []
