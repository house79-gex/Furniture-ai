# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   

import adsk.core               
import adsk.fusion               
import traceback


class NestingVisualization:
                                                                                   
    
    def __init__(self, design):
        self.design = design
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
    
    def create_nested_visualization(self, sheets, unit_type='mm', sheet_spacing=10.0, show_labels=True):
                   
        try:
            root_comp = self.design.rootComponent
            created_occurrences = []
            
                                                            
            map_occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            map_comp = map_occurrence.component
            map_comp.name = "Nesting_Layout"
            
                                                                                       
            max_body_x = 0.0
            max_body_y = 0.0
            
            for body in root_comp.bRepBodies:
                try:
                    bbox = body.boundingBox
                    max_body_x = max(max_body_x, bbox.maxPoint.x)
                    max_body_y = max(max_body_y, bbox.maxPoint.y)
                except:
                    pass
            
            for occ in root_comp.allOccurrences:
                try:
                    if occ.bRepBodies:
                        for body in occ.bRepBodies:
                            bbox = body.boundingBox
                            max_body_x = max(max_body_x, bbox.maxPoint.x)
                            max_body_y = max(max_body_y, bbox.maxPoint.y)
                except:
                    pass

                                                   
            spacing_cm = self._to_cm(sheet_spacing, unit_type)
            min_spacing = max(spacing_cm, 10.0)
                                                                                                
            max_sheet_length_cm = max(self._to_cm(s.width, unit_type) for s in sheets) if sheets else 0.0
            
                                                      
                                                                                        
            x_offset = max_body_x + max_sheet_length_cm + min_spacing
            y_offset = 0.0                      
            
                                                         
            for sheet_idx, sheet in enumerate(sheets):
                                                 
                board_occ = self._create_board_occurrence(
                    map_comp,
                    sheet,
                    x_offset,
                    y_offset,
                    sheet_idx + 1,
                    unit_type
                )
                
                if board_occ:
                    created_occurrences.append(board_occ)
                    
                                                            
                    sheet_thickness_cm = self._to_cm(sheet.thickness, unit_type)
                    created_count = 0
                    for rect in sheet.rectangles:
                        comp_occ = None
                        if getattr(rect, 'original_body', None):
                            comp_occ = self._create_nested_component_with_joint(
                                map_comp,
                                board_occ,
                                rect,
                                x_offset,
                                y_offset,
                                unit_type,
                                sheet_thickness_cm
                            )
                                                                         
                            if not comp_occ:
                                comp_occ = self._create_placeholder_occurrence(
                                    map_comp,
                                    board_occ,
                                    rect,
                                    x_offset,
                                    y_offset,
                                    unit_type,
                                    sheet_thickness_cm
                                )
                        else:
                            comp_occ = self._create_placeholder_occurrence(
                                map_comp,
                                board_occ,
                                rect,
                                x_offset,
                                y_offset,
                                unit_type,
                                sheet_thickness_cm
                            )
                        if comp_occ:
                            created_occurrences.append(comp_occ)
                            created_count += 1
                
                                             
                sheet_length_cm = self._to_cm(sheet.width, unit_type)
                x_offset += sheet_length_cm + min_spacing
            
                         
            try:
                self.app.activeViewport.fit()
            except:
                pass

            return created_occurrences
            
        except Exception as e:
            self.ui.messageBox(f'Nesting visualization failed:\n{str(e)}\n{traceback.format_exc()}')
            return []
    
    def _create_board_occurrence(self, map_comp, sheet, x_offset, y_offset, sheet_num, unit_type):
                                                                      
        try:
                                                           
            width_cm = self._to_cm(sheet.width, unit_type)
            height_cm = self._to_cm(sheet.height, unit_type)
            thickness_cm = self._to_cm(sheet.thickness, unit_type)
            
                                                                           
            
                                                                                
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(x_offset, y_offset, 0)
            
            board_occ = map_comp.occurrences.addNewComponent(transform)
            board_comp = board_occ.component
            board_comp.name = f"Sheet_{sheet_num}"
            
                                                                              
            sketch = board_comp.sketches.add(board_comp.xYConstructionPlane)
            sketch.name = "Board"
            
                                                          
            p1 = adsk.core.Point3D.create(0, 0, 0)
            p2 = adsk.core.Point3D.create(width_cm, height_cm, 0)
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)
            
                             
            profile = sketch.profiles.item(0)
            
                                          
            extrudes = board_comp.features.extrudeFeatures
            extrude_input = extrudes.createInput(
                profile,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            distance = adsk.core.ValueInput.createByReal(thickness_cm)
            extrude_input.setDistanceExtent(False, distance)
            extrude_feature = extrudes.add(extrude_input)
            
                                  
            if extrude_feature.bodies.count > 0:
                board_body = extrude_feature.bodies.item(0)
                board_body.name = f"Sheet_{sheet_num}_{sheet.material}_{sheet.thickness}{unit_type}"
                board_body.opacity = 0.3                    
            
            return board_occ
            
        except Exception as e:
                                                         
            return None
    
    def _create_nested_component_with_joint(self, map_comp, board_occ, rect, x_offset, y_offset, unit_type, sheet_thickness_cm):
                                                                                      
        try:
            original_body = rect.original_body
            if not original_body:
                return None
            
                                                         
            x_cm = self._to_cm(rect.x, unit_type)
            y_cm = self._to_cm(rect.y, unit_type)
            
                                                                                             
                                                                        
            rect_width = self._to_cm(rect.width, unit_type)
            rect_height = self._to_cm(rect.height, unit_type)
            
                                                                                                        
            body_thickness = None
            try:
                attrs = original_body.attributes
                th_attr = attrs.itemByName("WoodWorkingWizard", "original_thickness")
                if th_attr:
                                           
                    body_thickness = float(th_attr.value)
            except:
                body_thickness = None

            if body_thickness is None:
                                                                                                        
                try:
                    bbox = original_body.boundingBox
                    dim_x = bbox.maxPoint.x - bbox.minPoint.x
                    dim_y = bbox.maxPoint.y - bbox.minPoint.y
                    dim_z = bbox.maxPoint.z - bbox.minPoint.z
                    dims = sorted([dim_x, dim_y, dim_z])
                    body_thickness = dims[0]
                except:
                                                      
                    body_thickness = sheet_thickness_cm
            
            rotation_mark = "_R90" if rect.rotated else ""
            comp_name = f"{rect.name}_Nested{rotation_mark}"
            
                                                                                               
            world_x = x_offset + x_cm
            world_y = y_offset + y_cm
            world_z = sheet_thickness_cm + 0.01                       
            
                                                         
            world_transform = adsk.core.Matrix3D.create()
            world_transform.translation = adsk.core.Vector3D.create(world_x, world_y, world_z)
            
                                                                      
            comp_occ = map_comp.occurrences.addNewComponent(world_transform)
            comp_comp = comp_occ.component
            comp_comp.name = comp_name
            
                                                                   
                                                                                   
            sketch = comp_comp.sketches.add(comp_comp.xYConstructionPlane)
            rect_sketch = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(rect_width, rect_height, 0)
            )
            
            profile = sketch.profiles.item(0)
            extrudes = comp_comp.features.extrudeFeatures
            extrude_input = extrudes.createInput(
                profile,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            distance = adsk.core.ValueInput.createByReal(body_thickness)
            extrude_input.setDistanceExtent(False, distance)
            extrude_feature = extrudes.add(extrude_input)
            
            if extrude_feature.bodies.count > 0:
                comp_body = extrude_feature.bodies.item(0)
                comp_body.name = comp_name
                
                                                    
                try:
                    if original_body.material:
                        comp_body.material = original_body.material
                except:
                    pass
            
            return comp_occ
            
        except Exception as e:
                                                             
            return None
    
    def _find_largest_planar_face(self, body):
                                                                                      
        try:
            largest_face = None
            largest_area = 0.0
            
            for face in body.faces:
                if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                    area = face.area
                    if area > largest_area:
                        largest_area = area
                        largest_face = face
            
            return largest_face
            
        except Exception as e:
                            
            return None
    
    def _create_placeholder_occurrence(self, map_comp, board_occ, rect, x_offset, y_offset, unit_type, sheet_thickness_cm):
                                                                                                            
        try:
                                 
            width_cm = self._to_cm(rect.width, unit_type)
            height_cm = self._to_cm(rect.height, unit_type)
            x_cm = self._to_cm(rect.x, unit_type)
            y_cm = self._to_cm(rect.y, unit_type)
                                                                                
            thickness_cm = sheet_thickness_cm

                                                                 
            if rect.rotated:
                final_width = height_cm
                final_height = width_cm
            else:
                final_width = width_cm
                final_height = height_cm

                                                                                               
            world_x = x_offset + x_cm
            world_y = y_offset + y_cm
            world_z = sheet_thickness_cm + 0.01
            
                                                         
            world_transform = adsk.core.Matrix3D.create()
            world_transform.translation = adsk.core.Vector3D.create(world_x, world_y, world_z)

                                                          
            comp_occ = map_comp.occurrences.addNewComponent(world_transform)
            comp_comp = comp_occ.component
            rotation_mark = "_R90" if rect.rotated else ""
            comp_comp.name = f"{rect.name}_Placeholder{rotation_mark}"

                                            
            sketch = comp_comp.sketches.add(comp_comp.xYConstructionPlane)
            p1 = adsk.core.Point3D.create(0, 0, 0)
            p2 = adsk.core.Point3D.create(final_width, final_height, 0)
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

                     
            profile = sketch.profiles.item(0)
            extrudes = comp_comp.features.extrudeFeatures
            extrude_input = extrudes.createInput(
                profile,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            distance = adsk.core.ValueInput.createByReal(thickness_cm)
            extrude_input.setDistanceExtent(False, distance)
            extrude_feature = extrudes.add(extrude_input)

            if extrude_feature.bodies.count > 0:
                body = extrude_feature.bodies.item(0)
                body.name = comp_comp.name

            return comp_occ
            
        except Exception as e:
                                                             
            return None
    
    def _to_cm(self, value, from_unit):
                                                                    
        if from_unit == 'mm':
            return value / 10.0
        elif from_unit == 'in':
            return value * 2.54
        else:      
            return value
