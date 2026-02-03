# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   

import adsk.core               
import adsk.fusion               
import os
from datetime import datetime
from .wizard.nesting import Rectangle
from .wizard.packer_rectpack import RectpackAdapter
from .wizard.packer_ccoa import CCOAPacker
from .wizard.visualization import NestingVisualization


class Component:
                                                        
    
    def __init__(self, name, width, height, depth, thickness, material, quantity=1, body=None):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.thickness = thickness
        self.material = material
        self.quantity = quantity
        self.body = body                                             
        self.area = self._calculate_area()
        self.volume = self._calculate_volume()
    
    def _calculate_area(self):
                                                      
                                                
        if self.width and self.height and self.depth:
            return 2 * (self.width * self.height + 
                       self.width * self.depth + 
                       self.height * self.depth)
        return 0
    
    def _calculate_volume(self):
                                                
        if self.width and self.height and self.depth:
            return self.width * self.height * self.depth
        return 0


class CutListGenerator:
                                                     
    
    def __init__(self, design, unit_type='cm'):
        self.design = design
        self.unit_type = unit_type
        self.components = []
        self.material_totals = {}
    
    def extract_components_from_bodies(self, bodies):
                                                                   
        for body in bodies:
            try:
                                     
                name = body.name if body.name else "Unnamed"
                material_name = self._get_material_name(body)
                
                                                                                                  
                original_dims = self._get_stored_dimensions(body)
                
                if original_dims:
                                                                                                      
                    width = self._convert_units(original_dims['width'])
                    height = self._convert_units(original_dims['height'])
                    depth = self._convert_units(original_dims['thickness'])
                    thickness = depth                                                  
                    
                    print(f"Using stored dimensions for {name}: {width:.2f} x {height:.2f} x {thickness:.2f} {self.unit_type}")
                else:
                                                                                        
                    bb = body.boundingBox
                    if bb:
                                                                           
                        width = self._convert_units(bb.maxPoint.x - bb.minPoint.x)
                        height = self._convert_units(bb.maxPoint.y - bb.minPoint.y)
                        depth = self._convert_units(bb.maxPoint.z - bb.minPoint.z)
                        
                                                                              
                        dims = sorted([width, height, depth])
                        thickness = dims[0]
                        
                                                                       
                        width = dims[2]
                        height = dims[1]
                        depth = dims[0]
                    else:
                        continue                           
                
                                  
                component = Component(
                    name=name,
                    width=width,
                    height=height,
                    depth=depth,
                    thickness=thickness,
                    material=material_name,
                    quantity=1,
                    body=body                                    
                )
                
                self.components.append(component)
                self._update_material_totals(component)
                
            except Exception as e:
                                                     
                continue
    
    def _get_material_name(self, body):
                                          
        try:
            if body.material:
                return body.material.name
        except:
            pass
        return "Unknown"
    
    def _get_stored_dimensions(self, body):
                                                                                    
        try:
                                                                                     
            attrs = body.attributes
            width_attr = attrs.itemByName("WoodWorkingWizard", "original_width")
            height_attr = attrs.itemByName("WoodWorkingWizard", "original_height")
            thickness_attr = attrs.itemByName("WoodWorkingWizard", "original_thickness")
            
            if width_attr and height_attr and thickness_attr:
                                                                               
                return {
                    'width': float(width_attr.value),
                    'height': float(height_attr.value),
                    'thickness': float(thickness_attr.value)
                }
        except:
            pass
        return None
    
    def _convert_units(self, value_cm):
                                                    
        if self.unit_type == 'mm':
            return value_cm * 10
        elif self.unit_type == 'in':
            return value_cm / 2.54
        else:      
            return value_cm
    
    def _update_material_totals(self, component):
                                                
        material = component.material
        if material not in self.material_totals:
            self.material_totals[material] = {
                'count': 0,
                'total_area': 0,
                'total_volume': 0,
                'components': []
            }
        
        self.material_totals[material]['count'] += component.quantity
        self.material_totals[material]['total_area'] += component.area * component.quantity
        self.material_totals[material]['total_volume'] += component.volume * component.quantity
        self.material_totals[material]['components'].append(component)
    
    def generate_html_report(self, output_path):
                                            
        html = self._build_html()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True, output_path
        except Exception as e:
            return False, str(e)
    
    def generate_csv_report(self, output_path, sheets=None):
                   
        csv = self._build_csv(sheets=sheets)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv)
            return True, output_path
        except Exception as e:
            return False, str(e)
    
    def _build_html(self):
                                        
        unit_label = self.unit_type
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WoodWorking Wizard - Cut List</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #8B4513;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 5px 0 0 0;
            font-size: 14px;
        }}
        .summary {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary h2 {{
            margin-top: 0;
            color: #8B4513;
            font-size: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        th {{
            background-color: #8B4513;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .material-section {{
            margin-bottom: 30px;
        }}
        .material-header {{
            background-color: #D2691E;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 16px;
            font-weight: bold;
        }}
        .totals {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .number {{
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🪵 WoodWorking Wizard - Cut List</h1>
        <p>Generated: {timestamp}</p>
        <p>Units: {unit_label}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Total Components:</strong> {len(self.components)}</p>
        <p><strong>Materials:</strong> {len(self.material_totals)}</p>
    </div>
"""
        
                                
        for material, data in self.material_totals.items():
            html += f"""
    <div class="material-section">
        <div class="material-header">{material} ({data['count']} pieces)</div>
        <table>
            <tr>
                <th>Component Name</th>
                <th class="number">Width ({unit_label})</th>
                <th class="number">Height ({unit_label})</th>
                <th class="number">Thickness ({unit_label})</th>
                <th class="number">Qty</th>
            </tr>
"""
            for comp in data['components']:
                html += f"""
            <tr>
                <td>{comp.name}</td>
                <td class="number">{comp.width:.2f}</td>
                <td class="number">{comp.height:.2f}</td>
                <td class="number">{comp.thickness:.2f}</td>
                <td class="number">{comp.quantity}</td>
            </tr>
"""
            
            total_vol = data['total_volume']
            html += f"""
            <tr class="totals">
                <td colspan="4">Total Volume</td>
                <td class="number">{total_vol:.2f} {unit_label}³</td>
            </tr>
        </table>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def _build_csv(self, sheets=None):
                   
        unit_label = self.unit_type
        
                    
        csv = f"Component Name,Material,Width ({unit_label}),Height ({unit_label}),Thickness ({unit_label}),Quantity\n"
        
                                     
        sorted_components = sorted(self.components, key=lambda x: x.material)
        
        for comp in sorted_components:
            csv += f'"{comp.name}","{comp.material}",{comp.width:.2f},{comp.height:.2f},{comp.thickness:.2f},{comp.quantity}\n'
        
                             
        csv += "\n--- Material Summary ---\n"
        csv += "Material,Component Count,Total Volume\n"
        
        for material, data in self.material_totals.items():
            csv += f'"{material}",{data["count"]},{data["total_volume"]:.2f}\n'

                                                                          
        if sheets:
            csv += "\n--- Panels (Grouped by Sheet) ---\n"
            for idx, sheet in enumerate(sheets, start=1):
                csv += f"Panel {idx}\n"
                csv += f"Component Name,Width ({unit_label}),Height ({unit_label}),Thickness ({unit_label}),Quantity\n"
                                                     
                agg = {}
                for rect in getattr(sheet, 'rectangles', []):
                    comp = getattr(rect, 'component', None)
                    if comp is not None:
                        name = comp.name
                        width = comp.width
                        height = comp.height
                        thickness = comp.thickness
                    else:
                                                          
                        name = getattr(rect, 'name', 'Unnamed')
                        width = getattr(rect, 'width', 0.0)
                        height = getattr(rect, 'height', 0.0)
                        thickness = getattr(sheet, 'thickness', 0.0)
                    key = (name, round(width, 4), round(height, 4), round(thickness, 4))
                    agg[key] = agg.get(key, 0) + 1
                for (name, width, height, thickness), qty in agg.items():
                    csv += f'"{name}",{width:.2f},{height:.2f},{thickness:.2f},{qty}\n'
                csv += "\n"
        
        return csv
    
    def generate_nesting_layout(self, output_dir, sheet_width=244, sheet_height=122, 
                               kerf=0.3, edge_margin=1.0, rotation_allowed=True,
                               create_3d_visualization=True, z_spacing=10.0, show_labels=True,
                               optimization_attempts: int = 128):
                   
        print(f"\n*** GENERATE_NESTING_LAYOUT CALLED ***")
        
        try:
                                                       
            if self.unit_type == 'mm':
                sheet_width_unit = sheet_width * 10
                sheet_height_unit = sheet_height * 10
                kerf_unit = kerf * 10
                edge_margin_unit = edge_margin * 10
                z_spacing_unit = z_spacing * 10
            elif self.unit_type == 'in':
                sheet_width_unit = sheet_width / 2.54
                sheet_height_unit = sheet_height / 2.54
                kerf_unit = kerf / 2.54
                edge_margin_unit = edge_margin / 2.54
                z_spacing_unit = z_spacing / 2.54
            else:      
                sheet_width_unit = sheet_width
                sheet_height_unit = sheet_height
                kerf_unit = kerf
                edge_margin_unit = edge_margin
                z_spacing_unit = z_spacing
            
                                                        
            material_groups = {}
            for comp in self.components:
                key = f"{comp.material}_{comp.thickness:.2f}"
                if key not in material_groups:
                    material_groups[key] = {
                        'material': comp.material,
                        'thickness': comp.thickness,
                        'components': []
                    }
                material_groups[key]['components'].append(comp)
            
                                                                     
            all_sheets = []
            created_bodies = []
            
            for group_key, group_data in material_groups.items():
                                                   
                rectangles = []
                for comp in group_data['components']:
                    for _ in range(comp.quantity):
                        rect = Rectangle(
                            width=comp.width,
                            height=comp.height,
                            name=comp.name,
                            component=comp,
                            rotation_allowed=rotation_allowed,
                            original_body=comp.body                       
                        )
                        rectangles.append(rect)
                
                                                                          
                sheets = []
                try:
                    adapter = RectpackAdapter(
                        sheet_width=sheet_width_unit,
                        sheet_height=sheet_height_unit,
                        kerf=kerf_unit,
                        edge_margin=edge_margin_unit
                    )
                    sheets = adapter.pack(rectangles, rotation_allowed, attempts=optimization_attempts)
                except Exception:
                    sheets = []
                if not sheets:
                                                      
                    try:
                        ccoa = CCOAPacker(
                            sheet_width=sheet_width_unit,
                            sheet_height=sheet_height_unit,
                            kerf=kerf_unit,
                            edge_margin=edge_margin_unit
                        )
                        sheets = ccoa.pack(rectangles, rotation_allowed, attempts=optimization_attempts)
                    except Exception as e:
                        return False, f'Nesting failed: {e}', 0, []
                if not sheets:
                    return False, 'Nesting returned no layout', 0, []
                
                                                                          
                for sh in sheets:
                    if not getattr(sh, 'material', None):
                        sh.material = group_data['material']
                    if not getattr(sh, 'thickness', None):
                        sh.thickness = group_data['thickness']
                all_sheets.extend(sheets)
                
                                                      
                if create_3d_visualization and self.design:
                    visualizer = NestingVisualization(self.design)
                    bodies = visualizer.create_nested_visualization(
                        sheets, 
                        self.unit_type,
                        z_spacing_unit,
                        show_labels
                    )
                    created_bodies.extend(bodies)
            
            return True, len(all_sheets), created_bodies, all_sheets
            
        except Exception as e:
            return False, str(e), 0, []

    def generate_panel_csv(self, sheets, output_path):
                   
        try:
            unit_label = self.unit_type
            lines = []
            lines.append(f"Panels CSV grouped by nested sheets")
            lines.append("")
            
                                                                          
            for idx, sheet in enumerate(sheets, start=1):
                lines.append(f"Panel {idx}")
                lines.append(f"Component Name,Width ({unit_label}),Height ({unit_label}),Thickness ({unit_label}),Quantity")
                
                                                               
                agg = {}
                for rect in sheet.rectangles:
                    comp = getattr(rect, 'component', None)
                    if not comp:
                                                                              
                        name = rect.name or "Unnamed"
                        width = rect.width
                        height = rect.height
                                                                          
                        thickness = sheet.thickness
                    else:
                        name = comp.name
                        width = comp.width
                        height = comp.height
                        thickness = comp.thickness
                    key = (name, round(width, 4), round(height, 4), round(thickness, 4))
                    agg[key] = agg.get(key, 0) + 1
                
                                       
                for (name, width, height, thickness), qty in agg.items():
                    lines.append(f'"{name}",{width:.2f},{height:.2f},{thickness:.2f},{qty}')
                
                lines.append("")                             
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            return True, output_path
        except Exception as e:
            return False, str(e)
