# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   

import math
from typing import List, Tuple, Optional


class Rectangle:
                                                          
    
    def __init__(self, width, height, name="", component=None, rotation_allowed=True, original_body=None):
        self.width = width
        self.height = height
        self.name = name
        self.component = component                                          
        self.original_body = original_body                                             
        self.rotation_allowed = rotation_allowed
        self.x = 0                      
        self.y = 0
        self.rotated = False                                 
    
    def area(self):
        return self.width * self.height
    
    def rotate(self):
                                          
        if self.rotation_allowed:
            self.width, self.height = self.height, self.width
            self.rotated = not self.rotated
    
    def fits_in(self, width, height):
                                                     
        return self.width <= width and self.height <= height


class Sheet:
                                         
    
    def __init__(self, width, height, material="Plywood", thickness=1.9):
        self.width = width
        self.height = height
        self.material = material
        self.thickness = thickness
        self.rectangles = []                     
        self.free_rectangles = [Rectangle(width, height, "free_space")]                    
        self.utilization = 0.0                            
    
    def add_rectangle(self, rect: Rectangle):
                                                  
        self.rectangles.append(rect)
        self._update_utilization()
    
    def _update_utilization(self):
                                                     
        total_area = self.width * self.height
        used_area = sum(r.area() for r in self.rectangles)
        self.utilization = (used_area / total_area * 100) if total_area > 0 else 0


                                                                                          


class NestingLayoutGenerator:
                                                         
    
    def __init__(self, unit_type='mm'):
        self.unit_type = unit_type
    
    def generate_svg(self, sheets: List[Sheet], output_path: str) -> bool:
                   
        try:
            svg_content = self._build_svg(sheets)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error generating SVG: {e}")
            return False
    
    def _build_svg(self, sheets: List[Sheet]) -> str:
                                               
                      
        scale = 2                   
        margin = 50
        sheet_spacing = 100
        
                                        
        max_width = max(s.width for s in sheets) if sheets else 0
        total_height = sum(s.height + sheet_spacing for s in sheets)
        
        svg_width = int((max_width * scale) + (2 * margin))
        svg_height = int((total_height * scale) + (2 * margin))
        
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">
    <defs>
        <style>
            .sheet {{ fill: #f5e6d3; stroke: #8B4513; stroke-width: 3; }}
            .component {{ fill: #d4a574; stroke: #654321; stroke-width: 1.5; opacity: 0.8; }}
            .component:hover {{ opacity: 1; stroke-width: 2; }}
            .label {{ font-family: Arial, sans-serif; font-size: 10px; fill: #000; }}
            .sheet-label {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #8B4513; }}
        </style>
    </defs>
'''
        
                         
        y_offset = margin
        for idx, sheet in enumerate(sheets):
            svg += self._draw_sheet_svg(sheet, margin, y_offset, scale, idx + 1)
            y_offset += int((sheet.height + sheet_spacing) * scale)
        
        svg += '</svg>'
        return svg
    
    def _draw_sheet_svg(self, sheet: Sheet, x_offset: float, y_offset: float, scale: float, sheet_num: int) -> str:
                                                         
        svg = f'\n    <!-- Sheet {sheet_num} -->\n'
        
                               
        svg += f'    <rect class="sheet" x="{x_offset}" y="{y_offset}" width="{sheet.width * scale}" height="{sheet.height * scale}"/>\n'
        
                     
        svg += f'    <text class="sheet-label" x="{x_offset + 10}" y="{y_offset + 20}">Sheet {sheet_num} - {sheet.material} ({sheet.thickness}{self.unit_type}) - Utilization: {sheet.utilization:.1f}%</text>\n'
        
                         
        for rect in sheet.rectangles:
            x = x_offset + (rect.x * scale)
            y = y_offset + (rect.y * scale)
            w = rect.width * scale
            h = rect.height * scale
            
            svg += f'    <rect class="component" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
            
                                          
            if w > 40 and h > 20:
                label_x = x + (w / 2)
                label_y = y + (h / 2)
                rotation_mark = " ↻" if rect.rotated else ""
                svg += f'    <text class="label" x="{label_x}" y="{label_y}" text-anchor="middle">{rect.name}{rotation_mark}</text>\n'
                svg += f'    <text class="label" x="{label_x}" y="{label_y + 12}" text-anchor="middle">{rect.width:.0f}×{rect.height:.0f}</text>\n'
        
        return svg
