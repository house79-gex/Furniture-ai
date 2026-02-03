# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

                                                    
               
                                                                                   
 
                                 
                                                           
                                                                     

import adsk.core               
import adsk.fusion               
import traceback
import os
import shutil
from .cutlist import CutListGenerator

                                     
_handlers = []
_ui: adsk.core.UserInterface = None
_cmd_def: adsk.core.CommandDefinition = None
_btn_control: adsk.core.ToolbarControl = None
_panel: adsk.core.ToolbarPanel = None

                             
_cutlist_cmd_def: adsk.core.CommandDefinition = None
_cutlist_btn_control: adsk.core.ToolbarControl = None


class WoodWorkingExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def create_cabinet_door(self, design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness, unit_type, bodies, is_double=False):
                                                                                                    
        try:
            import math
            app = adsk.core.Application.get()
            
            if is_double:
                                                                 
                door_width = cab_width / 2
                num_doors = 2
            else:
                                               
                door_width = cab_width
                num_doors = 1
            
            door_thickness = cab_thickness                                                   
            door_height = cab_height                        
            
                                                             
            user_params = design.userParameters
            
            def add_door_param(name, value, comment):
                existing = user_params.itemByName(name)
                if existing:
                    existing.expression = str(value)
                else:
                    user_params.add(name, adsk.core.ValueInput.createByReal(value), unit_type, comment)
            
            add_door_param('Door_Type', num_doors, 'Number of doors (1=Single, 2=Double)')
            add_door_param('Door_Width', door_width, 'Individual door width')
            add_door_param('Door_Thickness', door_thickness, 'Cabinet door thickness')
            add_door_param('Door_Height', door_height, 'Cabinet door height')
            
                                                                         
            door_plane = sketch_plane
            
            sketches = design.rootComponent.sketches
            extrudes = design.rootComponent.features.extrudeFeatures
            move_feats = design.rootComponent.features.moveFeatures
            
            created_doors = []
            
                                                       
            for door_num in range(num_doors):
                                                          
                if is_double:
                    door_x_offset = door_num * door_width
                    door_name = f"Cabinet_Door_{door_num + 1}"
                    hinge_x = door_x_offset if door_num == 0 else door_x_offset + door_width                                                        
                    rotation_angle = math.radians(-45) if door_num == 0 else math.radians(45)                                                
                else:
                    door_x_offset = 0
                    door_name = "Cabinet_Door"
                    hinge_x = 0                                     
                    rotation_angle = math.radians(-45)                          
                
                                                                   
                door_sketch = sketches.add(door_plane)
                
                                                                    
                                                                     
                door_rect = door_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(door_x_offset, 0, 0),
                    adsk.core.Point3D.create(door_x_offset + door_width, door_thickness, 0)
                )
                
                                                                    
                door_profile = door_sketch.profiles.item(0)
                door_extrude_input = extrudes.createInput(door_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                door_extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cab_height))
                door_extrude = extrudes.add(door_extrude_input)
                
                if door_extrude.bodies.count > 0:
                    door_body = door_extrude.bodies.item(0)
                    door_body.name = door_name
                    
                                                                             
                                                                                                
                    try:
                        door_body.attributes.add("WoodWorkingWizard", "original_width", str(door_width))
                        door_body.attributes.add("WoodWorkingWizard", "original_height", str(cab_height))
                        door_body.attributes.add("WoodWorkingWizard", "original_thickness", str(door_thickness))
                        door_body.attributes.add("WoodWorkingWizard", "component_type", "door")
                    except:
                        pass                           
                    
                                            
                    try:
                        material_libs = app.materialLibraries
                        pine_names = ['Pino', 'Pine', 'Pine Wood']
                        pine_mat = None
                        
                        for i in range(material_libs.count):
                            mat_lib = material_libs.item(i)
                            for name in pine_names:
                                pine_mat = mat_lib.materials.itemByName(name)
                                if pine_mat:
                                    break
                            if pine_mat:
                                break
                        if pine_mat:
                            door_body.material = pine_mat
                    except:
                        pass
                    
                                            
                    try:
                        material_libs = app.materialLibraries
                        pine_names = ['Pino', 'Pine', 'Pine Wood']
                        pine_mat = None
                        
                        for i in range(material_libs.count):
                            mat_lib = material_libs.item(i)
                            for name in pine_names:
                                pine_mat = mat_lib.materials.itemByName(name)
                                if pine_mat:
                                    break
                            if pine_mat:
                                break
                        if pine_mat:
                            door_body.material = pine_mat
                    except:
                        pass
                    
                                                                                        
                    transform = adsk.core.Matrix3D.create()
                    
                                                                                            
                    axis_point = adsk.core.Point3D.create(hinge_x, 0, 0)
                    
                                                        
                    axis_direction = adsk.core.Vector3D.create(0, 0, 1)
                    
                    transform.setToRotation(rotation_angle, axis_direction, axis_point)
                    
                                                            
                    body_collection2 = adsk.core.ObjectCollection.create()
                    body_collection2.add(door_body)
                    move_input2 = move_feats.createInput(body_collection2, transform)
                    move_feats.add(move_input2)
                    
                    bodies.append(door_body)
                    created_doors.append(door_body)
            
            return created_doors
                
        except Exception as e:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(f'Door creation failed: {str(e)}\n{traceback.format_exc()}')
            return None
            
            return created_doors
                
        except Exception as e:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(f'Door creation failed: {str(e)}\n{traceback.format_exc()}')
            return None

    def create_drawers(self, design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness,
                      drawer_count, drawer_ply, drawer_base_ply, groove_height, drawer_spacing,
                      slides_thickness, drawer_height, drawer_width, drawer_depth, bodies, 
                      custom_drawer_depth=None, create_front_panels=False, front_panel_spacing=0.2):
                                                         
        try:
            app = adsk.core.Application.get()
            sketches = design.rootComponent.sketches
            features = design.rootComponent.features
            extrudes = features.extrudeFeatures
            planes = design.rootComponent.constructionPlanes
            
                                
            for drawer_num in range(drawer_count):
                                                                             
                                                                                          
                drawer_z_start = cab_thickness + (drawer_spacing * (drawer_num + 1)) + (drawer_num * drawer_height)
                
                                                            
                drawer_plane_input = planes.createInput()
                drawer_plane_input.setByOffset(sketch_plane, adsk.core.ValueInput.createByReal(drawer_z_start))
                drawer_plane = planes.add(drawer_plane_input)
                
                                                                        
                                                                                                               
                                                            
                drawer_x_start = cab_thickness + slides_thickness
                drawer_y_start = 0                    
                
                                                                       
                                                                                 
                                                                              
                back_height = drawer_height - (groove_height + drawer_base_ply)
                
                                                  
                sketch_front = sketches.add(drawer_plane)
                rect_front = sketch_front.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(drawer_x_start, drawer_y_start, 0),
                    adsk.core.Point3D.create(drawer_x_start + drawer_width, drawer_y_start + drawer_ply, 0)
                )
                profile_front = sketch_front.profiles.item(0)
                extrude_front_input = extrudes.createInput(profile_front, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrude_front_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_height))
                extrude_front = extrudes.add(extrude_front_input)
                if extrude_front.bodies.count > 0:
                    front_body = extrude_front.bodies.item(0)
                    front_body.name = f"Drawer_{drawer_num + 1}_Front"
                    bodies.append(front_body)
                
                                                    
                                                     
                actual_drawer_depth = custom_drawer_depth if custom_drawer_depth else drawer_depth
                back_y_position = drawer_y_start + actual_drawer_depth - drawer_ply
                
                sketch_back = sketches.add(drawer_plane)
                rect_back = sketch_back.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(drawer_x_start, back_y_position, 0),
                    adsk.core.Point3D.create(drawer_x_start + drawer_width, back_y_position + drawer_ply, 0)
                )
                profile_back = sketch_back.profiles.item(0)
                extrude_back_input = extrudes.createInput(profile_back, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrude_back_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(back_height))
                extrude_back = extrudes.add(extrude_back_input)
                if extrude_back.bodies.count > 0:
                    back_body = extrude_back.bodies.item(0)
                    back_body.name = f"Drawer_{drawer_num + 1}_Back"
                                                                              
                                                                                                
                    move_feats = features.moveFeatures
                    move_vec = adsk.core.Vector3D.create(0, 0, groove_height + drawer_base_ply)
                    move_xform = adsk.core.Matrix3D.create()
                    move_xform.translation = move_vec
                    oc = adsk.core.ObjectCollection.create()
                    oc.add(back_body)
                    move_input = move_feats.createInput(oc, move_xform)
                    move_feats.add(move_input)
                    bodies.append(back_body)
                
                                                      
                sketch_left = sketches.add(drawer_plane)
                rect_left = sketch_left.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(drawer_x_start, drawer_y_start + drawer_ply, 0),
                    adsk.core.Point3D.create(drawer_x_start + drawer_ply, drawer_y_start + actual_drawer_depth - drawer_ply, 0)
                )
                profile_left = sketch_left.profiles.item(0)
                extrude_left_input = extrudes.createInput(profile_left, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrude_left_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_height))
                extrude_left = extrudes.add(extrude_left_input)
                if extrude_left.bodies.count > 0:
                    left_body = extrude_left.bodies.item(0)
                    left_body.name = f"Drawer_{drawer_num + 1}_Left"
                    bodies.append(left_body)
                
                                                       
                sketch_right = sketches.add(drawer_plane)
                rect_right = sketch_right.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(drawer_x_start + drawer_width - drawer_ply, drawer_y_start + drawer_ply, 0),
                    adsk.core.Point3D.create(drawer_x_start + drawer_width, drawer_y_start + actual_drawer_depth - drawer_ply, 0)
                )
                profile_right = sketch_right.profiles.item(0)
                extrude_right_input = extrudes.createInput(profile_right, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrude_right_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_height))
                extrude_right = extrudes.add(extrude_right_input)
                if extrude_right.bodies.count > 0:
                    right_body = extrude_right.bodies.item(0)
                    right_body.name = f"Drawer_{drawer_num + 1}_Right"
                    bodies.append(right_body)
                
                                                       
                                                                       
                base_z = drawer_z_start + groove_height
                base_plane_input = planes.createInput()
                base_plane_input.setByOffset(sketch_plane, adsk.core.ValueInput.createByReal(base_z))
                base_plane = planes.add(base_plane_input)
                
                sketch_base = sketches.add(base_plane)
                                                                                   
                                                         
                groove_depth = drawer_ply / 2.0
                                                                             
                left_inner_face_x = drawer_x_start + drawer_ply
                right_inner_face_x = drawer_x_start + drawer_width - drawer_ply
                front_inner_face_y = drawer_y_start + drawer_ply
                back_inner_face_y = drawer_y_start + actual_drawer_depth - drawer_ply                                              
                                                                                    
                base_y_start = front_inner_face_y - groove_depth
                base_y_end = back_inner_face_y
                base_x_start = left_inner_face_x - groove_depth
                base_x_end = right_inner_face_x + groove_depth
                
                rect_base = sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(base_x_start, base_y_start, 0),
                    adsk.core.Point3D.create(base_x_end, base_y_end, 0)
                )
                profile_base = sketch_base.profiles.item(0)
                extrude_base_input = extrudes.createInput(profile_base, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrude_base_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_base_ply))
                extrude_base = extrudes.add(extrude_base_input)
                if extrude_base.bodies.count > 0:
                    base_body = extrude_base.bodies.item(0)
                    base_body.name = f"Drawer_{drawer_num + 1}_Base"
                    bodies.append(base_body)
                
                                                                                       
                combines = features.combineFeatures
                
                                     
                                                                                       
                                                                                                  
                inner_x_start = (drawer_x_start + drawer_ply) - groove_depth
                inner_x_end = (drawer_x_start + drawer_width - drawer_ply) + groove_depth
                front_inner_face_y = drawer_y_start + drawer_ply
                
                                                                                                                 
                                                                                                                   
                front_cutter_sk = sketches.add(base_plane)
                front_rect = front_cutter_sk.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(inner_x_start, front_inner_face_y - groove_depth, 0),
                    adsk.core.Point3D.create(inner_x_end, front_inner_face_y, 0)
                )
                front_cutter_profile = front_cutter_sk.profiles.item(0)
                front_cutter_ext_in = extrudes.createInput(front_cutter_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                front_cutter_ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_base_ply))
                front_cutter_ext = extrudes.add(front_cutter_ext_in)
                if front_cutter_ext.bodies.count > 0:
                    front_cutter_body = front_cutter_ext.bodies.item(0)
                    tools = adsk.core.ObjectCollection.create()
                    tools.add(front_cutter_body)
                                                                    
                    target = front_body
                    comb_in = combines.createInput(target, tools)
                    comb_in.isKeepToolBodies = False
                    comb_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
                    combines.add(comb_in)
                
                                              
                                                                                                  
                left_inner_face_x = drawer_x_start + drawer_ply
                inner_y_start = drawer_y_start + drawer_ply
                inner_y_end = drawer_y_start + actual_drawer_depth - drawer_ply                           
                
                left_cutter_sk = sketches.add(base_plane)
                left_rect = left_cutter_sk.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(left_inner_face_x - groove_depth, inner_y_start, 0),
                    adsk.core.Point3D.create(left_inner_face_x, inner_y_end, 0)
                )
                left_cutter_profile = left_cutter_sk.profiles.item(0)
                left_cutter_ext_in = extrudes.createInput(left_cutter_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                left_cutter_ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_base_ply))
                left_cutter_ext = extrudes.add(left_cutter_ext_in)
                if left_cutter_ext.bodies.count > 0:
                    left_cutter_body = left_cutter_ext.bodies.item(0)
                    tools = adsk.core.ObjectCollection.create()
                    tools.add(left_cutter_body)
                    target = left_body
                    comb_in = combines.createInput(target, tools)
                    comb_in.isKeepToolBodies = False
                    comb_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
                    combines.add(comb_in)
                
                                               
                right_inner_face_x = drawer_x_start + drawer_width - drawer_ply
                right_cutter_sk = sketches.add(base_plane)
                right_rect = right_cutter_sk.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(right_inner_face_x, inner_y_start, 0),
                    adsk.core.Point3D.create(right_inner_face_x + groove_depth, inner_y_end, 0)
                )
                right_cutter_profile = right_cutter_sk.profiles.item(0)
                right_cutter_ext_in = extrudes.createInput(right_cutter_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                right_cutter_ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(drawer_base_ply))
                right_cutter_ext = extrudes.add(right_cutter_ext_in)
                if right_cutter_ext.bodies.count > 0:
                    right_cutter_body = right_cutter_ext.bodies.item(0)
                    tools = adsk.core.ObjectCollection.create()
                    tools.add(right_cutter_body)
                    target = right_body
                    comb_in = combines.createInput(target, tools)
                    comb_in.isKeepToolBodies = False
                    comb_in.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
                    combines.add(comb_in)
                
                                                        
                if create_front_panels:
                                                                                               
                                                                                   
                    panel_width = cab_width
                    panel_thickness = drawer_ply                                  
                    
                                                                                            
                    panel_x_start = 0                                        
                    panel_y_start = -panel_thickness                               
                    
                                                                               
                                                                     
                    total_available_height = cab_height - (2 * cab_thickness)
                    
                                                                                 
                    total_front_spacing = (drawer_count - 1) * front_panel_spacing
                    
                                                                                      
                    total_panel_height = total_available_height - total_front_spacing
                    
                                                                
                    individual_panel_height = total_panel_height / drawer_count
                    
                                                                       
                                                                                                
                    panel_z_start = cab_thickness + (drawer_num * (individual_panel_height + front_panel_spacing))
                    
                                                               
                    front_panel_plane_input = planes.createInput()
                    front_panel_plane_input.setByOffset(sketch_plane, adsk.core.ValueInput.createByReal(panel_z_start))
                    front_panel_plane = planes.add(front_panel_plane_input)
                    
                                                                           
                    front_panel_sketch = sketches.add(front_panel_plane)
                    front_panel_rect = front_panel_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(panel_x_start, panel_y_start, 0),
                        adsk.core.Point3D.create(panel_x_start + panel_width, panel_y_start + panel_thickness, 0)
                    )
                    
                                                              
                    front_panel_profile = front_panel_sketch.profiles.item(0)
                    front_panel_extrude_input = extrudes.createInput(front_panel_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    front_panel_extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(individual_panel_height))
                    front_panel_extrude = extrudes.add(front_panel_extrude_input)
                    
                    if front_panel_extrude.bodies.count > 0:
                        front_panel_body = front_panel_extrude.bodies.item(0)
                        front_panel_body.name = f"Drawer_{drawer_num + 1}_Front_Panel"
                        bodies.append(front_panel_body)
                
        except Exception as e:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(f'Drawer creation failed: {str(e)}\n{traceback.format_exc()}')
    
                                                       

    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface if app else None
            if ui is None:
                return

            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs

                                                         
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                ui.messageBox('No active Fusion design.')
                return

                         
            plane_sel = adsk.core.SelectionCommandInput.cast(inputs.itemById('planeSel'))
            type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('projectType'))
            unit_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('unitType'))
            
            if not type_dd or not unit_dd:
                ui.messageBox('Inputs are not available.')
                return
            
                                                                       
            selected_sketch_plane = None
            selected_plane_name = 'XY Construction Plane (default)'
            
            if plane_sel and plane_sel.selectionCount > 0:
                try:
                    selected_sketch_plane = plane_sel.selection(0).entity
                    if hasattr(selected_sketch_plane, 'name'):
                        selected_plane_name = selected_sketch_plane.name
                    else:
                        selected_plane_name = f'{type(selected_sketch_plane).__name__}'
                except Exception as e:
                    ui.messageBox(f'Error getting selected plane: {str(e)}')
                    selected_sketch_plane = None
            
                                                     
            if selected_sketch_plane is None:
                selected_sketch_plane = design.rootComponent.xYConstructionPlane
                selected_plane_name = 'XY Construction Plane (default)'

                               
            project_type = type_dd.selectedItem.name if type_dd.selectedItem else 'Cabinet'
            unit_type = unit_dd.selectedItem.name if unit_dd.selectedItem else 'mm'

                                 
            user_params = design.userParameters

                                                        
            def add_or_update_param(name, value, unit, comment):
                try:
                                                       
                    existing_param = user_params.itemByName(name)
                    if existing_param:
                                                   
                        existing_param.expression = str(value)
                    else:
                                              
                        user_params.add(name, adsk.core.ValueInput.createByReal(value), unit, comment)
                except:
                                            
                    pass

                                                          
            if project_type == 'Cabinet':
                                    
                width_in = adsk.core.ValueCommandInput.cast(inputs.itemById('cabinetWidth'))
                height_in = adsk.core.ValueCommandInput.cast(inputs.itemById('cabinetHeight'))
                depth_in = adsk.core.ValueCommandInput.cast(inputs.itemById('cabinetDepth'))
                thickness_in = adsk.core.ValueCommandInput.cast(inputs.itemById('cabinetThickness'))
                
                if width_in:
                    add_or_update_param('Cabinet_Width', width_in.value, unit_type, 'Cabinet width')
                if height_in:
                    add_or_update_param('Cabinet_Height', height_in.value, unit_type, 'Cabinet height')
                if depth_in:
                    add_or_update_param('Cabinet_Depth', depth_in.value, unit_type, 'Cabinet depth')
                if thickness_in:
                    add_or_update_param('Cabinet_Thickness', thickness_in.value, unit_type, 'Cabinet material thickness')
                
                                               
                interior_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('cabinetInterior'))
                interior_type = interior_dd.selectedItem.name if interior_dd and interior_dd.selectedItem else 'None (Structure Only)'
                
                                           
                cab_width = width_in.value
                cab_height = height_in.value
                cab_depth = depth_in.value
                cab_thickness = thickness_in.value
                
                sketches = design.rootComponent.sketches
                features = design.rootComponent.features
                extrudes = features.extrudeFeatures
                bodies = []
                
                                    
                sketch_plane = selected_sketch_plane
                
                                            
                if interior_type == 'Shelf':
                                                                                
                    shelf_width = width_in.value - (2 * thickness_in.value)
                    shelf_depth = depth_in.value - thickness_in.value                                   
                    shelf_thickness = thickness_in.value
                    
                    add_or_update_param('Shelf_Width', shelf_width, unit_type, 'Shelf width (internal)')
                    add_or_update_param('Shelf_Depth', shelf_depth, unit_type, 'Shelf depth (flush with front)')
                    add_or_update_param('Shelf_Thickness', shelf_thickness, unit_type, 'Shelf thickness')
                    
                                           
                    shelf_count_in = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('shelfCount'))
                    shelf_count = shelf_count_in.value if shelf_count_in else 1
                    add_or_update_param('Shelf_Count', shelf_count, '', 'Number of shelves')
                    
                                                
                    cab_width = width_in.value
                    cab_height = height_in.value
                    cab_depth = depth_in.value
                    cab_thickness = thickness_in.value
                    inner_width = cab_width - (2 * cab_thickness)
                    inner_depth = cab_depth - cab_thickness                    
                    
                    sketches = design.rootComponent.sketches
                    features = design.rootComponent.features
                    extrudes = features.extrudeFeatures
                    bodies = []
                    
                                        
                    sketch_plane = selected_sketch_plane
                    
                                                                        
                    sketch_base = sketches.add(sketch_plane)
                    rect_base = sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_base = sketch_base.profiles.item(0)
                    distance_base = adsk.core.ValueInput.createByReal(cab_thickness)
                    extrude_base_input = extrudes.createInput(profile_base, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_base_input.setDistanceExtent(False, distance_base)
                    extrude_base = extrudes.add(extrude_base_input)
                    if extrude_base.bodies.count > 0:
                        base_body = extrude_base.bodies.item(0)
                        base_body.name = "Cabinet_Base"
                        bodies.append(base_body)
                    
                                                      
                                                                                                      
                    side_height = cab_height - (2 * cab_thickness)
                    
                                                                        
                    planes = design.rootComponent.constructionPlanes
                    side_plane_input = planes.createInput()
                    side_plane_input.setByOffset(
                        sketch_plane,
                        adsk.core.ValueInput.createByReal(cab_thickness)
                    )
                    side_plane = planes.add(side_plane_input)
                    
                    sketch1 = sketches.add(side_plane)
                    rect1 = sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_thickness, cab_depth, 0)
                    )
                    profile1 = sketch1.profiles.item(0)
                    distance1 = adsk.core.ValueInput.createByReal(side_height)
                    extrude1_input = extrudes.createInput(profile1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude1_input.setDistanceExtent(False, distance1)
                    extrude1 = extrudes.add(extrude1_input)
                    if extrude1.bodies.count > 0:
                        left_body = extrude1.bodies.item(0)
                        left_body.name = "Cabinet_Left_Side"
                        bodies.append(left_body)
                    
                                                                                                  
                    sketch2 = sketches.add(side_plane)
                    rect2 = sketch2.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_thickness, cab_depth - cab_thickness, 0),
                        adsk.core.Point3D.create(cab_width - cab_thickness, cab_depth, 0)
                    )
                    profile2 = sketch2.profiles.item(0)
                    distance2 = adsk.core.ValueInput.createByReal(side_height)
                    extrude2_input = extrudes.createInput(profile2, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude2_input.setDistanceExtent(False, distance2)
                    extrude2 = extrudes.add(extrude2_input)
                    if extrude2.bodies.count > 0:
                        back_body = extrude2.bodies.item(0)
                        back_body.name = "Cabinet_Back"
                        bodies.append(back_body)
                    
                                                       
                    sketch3 = sketches.add(side_plane)
                    rect3 = sketch3.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_width - cab_thickness, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile3 = sketch3.profiles.item(0)
                    distance3 = adsk.core.ValueInput.createByReal(side_height)
                    extrude3_input = extrudes.createInput(profile3, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude3_input.setDistanceExtent(False, distance3)
                    extrude3 = extrudes.add(extrude3_input)
                    if extrude3.bodies.count > 0:
                        right_body = extrude3.bodies.item(0)
                        right_body.name = "Cabinet_Right_Side"
                        bodies.append(right_body)
                    
                                                                         
                    top_plane_input = planes.createInput()
                    top_plane_input.setByOffset(
                        sketch_plane,
                        adsk.core.ValueInput.createByReal(cab_height - cab_thickness)
                    )
                    top_plane = planes.add(top_plane_input)
                    
                    sketch_top = sketches.add(top_plane)
                    rect_top = sketch_top.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_top = sketch_top.profiles.item(0)
                    distance_top = adsk.core.ValueInput.createByReal(cab_thickness)
                    extrude_top_input = extrudes.createInput(profile_top, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_top_input.setDistanceExtent(False, distance_top)
                    extrude_top = extrudes.add(extrude_top_input)
                    if extrude_top.bodies.count > 0:
                        top_body = extrude_top.bodies.item(0)
                        top_body.name = "Cabinet_Top"
                        bodies.append(top_body)
                    
                                                                                                
                                                                             
                    available_height = cab_height - (2 * cab_thickness)                              
                    shelf_spacing = available_height / (shelf_count + 1)
                    
                    for shelf_num in range(shelf_count):
                                                             
                        shelf_z_position = cab_thickness + (shelf_spacing * (shelf_num + 1))
                        
                                                                   
                        shelf_plane_input = planes.createInput()
                        shelf_plane_input.setByOffset(
                            sketch_plane,
                            adsk.core.ValueInput.createByReal(shelf_z_position)
                        )
                        shelf_plane = planes.add(shelf_plane_input)
                        
                                                                       
                        shelf_sketch = sketches.add(shelf_plane)
                        shelf_rect = shelf_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                            adsk.core.Point3D.create(cab_thickness, 0, 0),                          
                            adsk.core.Point3D.create(cab_thickness + inner_width, inner_depth, 0)
                        )
                        shelf_profile = shelf_sketch.profiles.item(0)
                        shelf_distance = adsk.core.ValueInput.createByReal(cab_thickness)
                        shelf_extrude_input = extrudes.createInput(shelf_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                        shelf_extrude_input.setDistanceExtent(False, shelf_distance)
                        shelf_extrude = extrudes.add(shelf_extrude_input)
                        if shelf_extrude.bodies.count > 0:
                            shelf_body = shelf_extrude.bodies.item(0)
                            shelf_body.name = f"Cabinet_Shelf_{shelf_num + 1}"
                            bodies.append(shelf_body)
                    
                                                  
                    try:
                        material_libs = app.materialLibraries
                        pine_names = ['Pino', 'Pine', 'Pine Wood']
                        pine_mat = None
                        
                        for i in range(material_libs.count):
                            mat_lib = material_libs.item(i)
                            for name in pine_names:
                                pine_mat = mat_lib.materials.itemByName(name)
                                if pine_mat:
                                    break
                            if pine_mat:
                                break
                        if pine_mat:
                            for body in bodies:
                                body.material = pine_mat
                    except Exception as mat_error:
                        pass
                    
                                                
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        is_double = door_type_dd and door_type_dd.selectedItem and door_type_dd.selectedItem.name == 'Double'
                        self.create_cabinet_door(design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness, unit_type, bodies, is_double)
                    
                                                                                  
                    
                                           
                    door_info = ""
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        door_type = door_type_dd.selectedItem.name if door_type_dd and door_type_dd.selectedItem else 'Single'
                        door_info = f"\nDoor: {door_type}"
                    
                    ui.messageBox(f'SUCCESS!\n\nCabinet with shelf created\n{len(bodies)} bodies created\nShelves: {shelf_count}{door_info}')
                
                elif interior_type == 'None (Structure Only)':
                                                                               
                    
                                                                        
                    sketch_base = sketches.add(sketch_plane)
                    rect_base = sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_base = sketch_base.profiles.item(0)
                    distance_base = adsk.core.ValueInput.createByReal(cab_thickness)
                    extrude_base_input = extrudes.createInput(profile_base, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_base_input.setDistanceExtent(False, distance_base)
                    extrude_base = extrudes.add(extrude_base_input)
                    if extrude_base.bodies.count > 0:
                        base_body = extrude_base.bodies.item(0)
                        base_body.name = "Cabinet_Base"
                        bodies.append(base_body)
                    
                                                           
                    side_height = cab_height - (2 * cab_thickness)
                    
                                                                        
                    planes = design.rootComponent.constructionPlanes
                    side_plane_input = planes.createInput()
                    side_plane_input.setByOffset(
                        sketch_plane,
                        adsk.core.ValueInput.createByReal(cab_thickness)
                    )
                    side_plane = planes.add(side_plane_input)
                    
                               
                    sketch1 = sketches.add(side_plane)
                    rect1 = sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_thickness, cab_depth, 0)
                    )
                    profile1 = sketch1.profiles.item(0)
                    distance1 = adsk.core.ValueInput.createByReal(side_height)
                    extrude1_input = extrudes.createInput(profile1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude1_input.setDistanceExtent(False, distance1)
                    extrude1 = extrudes.add(extrude1_input)
                    if extrude1.bodies.count > 0:
                        left_body = extrude1.bodies.item(0)
                        left_body.name = "Cabinet_Left_Side"
                        bodies.append(left_body)
                    
                          
                    sketch2 = sketches.add(side_plane)
                    rect2 = sketch2.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_thickness, cab_depth - cab_thickness, 0),
                        adsk.core.Point3D.create(cab_width - cab_thickness, cab_depth, 0)
                    )
                    profile2 = sketch2.profiles.item(0)
                    distance2 = adsk.core.ValueInput.createByReal(side_height)
                    extrude2_input = extrudes.createInput(profile2, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude2_input.setDistanceExtent(False, distance2)
                    extrude2 = extrudes.add(extrude2_input)
                    if extrude2.bodies.count > 0:
                        back_body = extrude2.bodies.item(0)
                        back_body.name = "Cabinet_Back"
                        bodies.append(back_body)
                    
                                
                    sketch3 = sketches.add(side_plane)
                    rect3 = sketch3.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_width - cab_thickness, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile3 = sketch3.profiles.item(0)
                    distance3 = adsk.core.ValueInput.createByReal(side_height)
                    extrude3_input = extrudes.createInput(profile3, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude3_input.setDistanceExtent(False, distance3)
                    extrude3 = extrudes.add(extrude3_input)
                    if extrude3.bodies.count > 0:
                        right_body = extrude3.bodies.item(0)
                        right_body.name = "Cabinet_Right_Side"
                        bodies.append(right_body)
                    
                                                                         
                    top_plane_input = planes.createInput()
                    top_plane_input.setByOffset(
                        sketch_plane,
                        adsk.core.ValueInput.createByReal(cab_height - cab_thickness)
                    )
                    top_plane = planes.add(top_plane_input)
                    
                    sketch_top = sketches.add(top_plane)
                    rect_top = sketch_top.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_top = sketch_top.profiles.item(0)
                    distance_top = adsk.core.ValueInput.createByReal(cab_thickness)
                    extrude_top_input = extrudes.createInput(profile_top, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_top_input.setDistanceExtent(False, distance_top)
                    extrude_top = extrudes.add(extrude_top_input)
                    if extrude_top.bodies.count > 0:
                        top_body = extrude_top.bodies.item(0)
                        top_body.name = "Cabinet_Top"
                        bodies.append(top_body)
                    
                                                  
                    try:
                        material_libs = app.materialLibraries
                        pine_names = ['Pino', 'Pine', 'Pine Wood']
                        pine_mat = None
                        
                        for i in range(material_libs.count):
                            mat_lib = material_libs.item(i)
                            for name in pine_names:
                                pine_mat = mat_lib.materials.itemByName(name)
                                if pine_mat:
                                    break
                            if pine_mat:
                                break
                        if pine_mat:
                            for body in bodies:
                                body.material = pine_mat
                    except Exception as mat_error:
                        pass
                    
                                                
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        is_double = door_type_dd and door_type_dd.selectedItem and door_type_dd.selectedItem.name == 'Double'
                        self.create_cabinet_door(design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness, unit_type, bodies, is_double)
                    
                                                                                  
                    
                                           
                    door_info = ""
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        door_type = door_type_dd.selectedItem.name if door_type_dd and door_type_dd.selectedItem else 'Single'
                        door_info = f"\nDoor: {door_type}"
                    
                    ui.messageBox(f'SUCCESS!\n\nCabinet structure created\n{len(bodies)} bodies created{door_info}')
                
                elif interior_type == 'Drawers':
                                           
                    drawer_count_in = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('drawerCount'))
                    drawer_ply_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerPlyThickness'))
                    drawer_base_ply_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerBasePlyThickness'))
                    groove_height_in = adsk.core.ValueCommandInput.cast(inputs.itemById('grooveHeight'))
                    drawer_spacing_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerSpacing'))
                    slides_thickness_in = adsk.core.ValueCommandInput.cast(inputs.itemById('slidesThickness'))
                    drawer_depth_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerDepth'))
                    drawer_height_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerHeight'))
                    drawer_front_panels_in = adsk.core.BoolValueCommandInput.cast(inputs.itemById('drawerFrontPanels'))
                    drawer_front_spacing_in = adsk.core.ValueCommandInput.cast(inputs.itemById('drawerFrontSpacing'))
                    
                    drawer_count = drawer_count_in.value if drawer_count_in else 1
                    drawer_ply = drawer_ply_in.value if drawer_ply_in else 1.2
                    drawer_base_ply = drawer_base_ply_in.value if drawer_base_ply_in else 0.6
                    groove_height = groove_height_in.value if groove_height_in else 0.6
                    drawer_spacing = drawer_spacing_in.value if drawer_spacing_in else 0.0
                    slides_thickness = slides_thickness_in.value if slides_thickness_in else 0.6
                    custom_drawer_depth = drawer_depth_in.value if drawer_depth_in else None
                    user_drawer_height = drawer_height_in.value if drawer_height_in else None
                    create_front_panels = drawer_front_panels_in.value if drawer_front_panels_in else False
                    front_panel_spacing = drawer_front_spacing_in.value if drawer_front_spacing_in else 0.2
                    
                                                
                    add_or_update_param('Drawer_Count', drawer_count, '', 'Number of drawers')
                    add_or_update_param('Drawer_Ply_Thickness', drawer_ply, unit_type, 'Drawer sides/front/back thickness')
                    add_or_update_param('Drawer_Base_Ply_Thickness', drawer_base_ply, unit_type, 'Drawer base panel thickness')
                    add_or_update_param('Groove_Height', groove_height, unit_type, 'Height from bottom to groove')
                    add_or_update_param('Drawer_Spacing', drawer_spacing, unit_type, 'Vertical spacing between drawers and at top/bottom')
                    add_or_update_param('Slides_Thickness', slides_thickness, unit_type, 'Slide allowance each side')
                    if user_drawer_height:
                        add_or_update_param('User_Drawer_Height', user_drawer_height, unit_type, 'User-specified individual drawer height')
                    
                                                 
                                                                      
                    available_height = cab_height - (2 * cab_thickness)
                    
                                                                                                          
                    if user_drawer_height:
                                                                       
                        total_drawer_height = drawer_count * user_drawer_height
                        total_spacing_needed = drawer_spacing * (drawer_count + 1)                                    
                        total_needed = total_drawer_height + total_spacing_needed
                        
                        if total_needed > available_height:
                                                     
                            max_possible_height = (available_height - total_spacing_needed) / drawer_count
                            ui.messageBox(f'Warning: Specified drawer height ({user_drawer_height:.1f}cm) is too large.\n'
                                        f'Total needed: {total_needed:.1f}cm > Available: {available_height:.1f}cm\n'
                                        f'Using maximum possible height: {max_possible_height:.1f}cm per drawer')
                            drawer_height = max_possible_height
                        else:
                            drawer_height = user_drawer_height
                            
                                                                                  
                        used_height = (drawer_count * drawer_height) + (drawer_spacing * (drawer_count + 1))
                        extra_space = available_height - used_height
                                                                                             
                        if extra_space > 0 and drawer_count > 1:
                            extra_spacing_per_gap = extra_space / (drawer_count + 1)
                            effective_spacing = drawer_spacing + extra_spacing_per_gap
                        else:
                            effective_spacing = drawer_spacing
                    else:
                                                                   
                        total_spacing = drawer_spacing * (drawer_count + 1)
                        drawer_height = (available_height - total_spacing) / drawer_count
                        effective_spacing = drawer_spacing
                    
                                                                  
                                                                                  
                    drawer_width = cab_width - (2 * cab_thickness) - (2 * slides_thickness)
                                                                                                        
                    max_drawer_depth = cab_depth - cab_thickness
                                                                                           
                    if custom_drawer_depth and custom_drawer_depth <= max_drawer_depth:
                        drawer_depth = custom_drawer_depth
                    else:
                        drawer_depth = max_drawer_depth
                        if custom_drawer_depth and custom_drawer_depth > max_drawer_depth:
                            ui.messageBox(f'Warning: Drawer depth ({custom_drawer_depth:.1f}) exceeds maximum allowed ({max_drawer_depth:.1f}). Using maximum depth.')
                    
                    add_or_update_param('Max_Drawer_Depth', max_drawer_depth, unit_type, 'Maximum allowed drawer depth')
                    
                    add_or_update_param('Drawer_Height', drawer_height, unit_type, 'Height of each drawer space')
                    add_or_update_param('Drawer_Width', drawer_width, unit_type, 'Internal drawer width')
                    add_or_update_param('Drawer_Depth', drawer_depth, unit_type, 'Internal drawer depth')
                    
                                                                       
                                                                        
                    sketch_base = sketches.add(sketch_plane)
                    rect_base = sketch_base.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_base = sketch_base.profiles.item(0)
                    extrude_base_input = extrudes.createInput(profile_base, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_base_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cab_thickness))
                    extrude_base = extrudes.add(extrude_base_input)
                    if extrude_base.bodies.count > 0:
                        base_body = extrude_base.bodies.item(0)
                        base_body.name = "Cabinet_Base"
                        bodies.append(base_body)
                    
                                                                              
                    planes = design.rootComponent.constructionPlanes
                    plane_input = planes.createInput()
                    plane_input.setByOffset(sketch_plane, adsk.core.ValueInput.createByReal(cab_thickness))
                    elevated_plane = planes.add(plane_input)
                    
                                                                     
                    sketch_left = sketches.add(elevated_plane)
                    rect_left = sketch_left.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_thickness, cab_depth, 0)
                    )
                    profile_left = sketch_left.profiles.item(0)
                    side_height = cab_height - (2 * cab_thickness)
                    extrude_left_input = extrudes.createInput(profile_left, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_left_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(side_height))
                    extrude_left = extrudes.add(extrude_left_input)
                    if extrude_left.bodies.count > 0:
                        left_body = extrude_left.bodies.item(0)
                        left_body.name = "Cabinet_Left_Side"
                        bodies.append(left_body)
                    
                                
                    sketch_right = sketches.add(elevated_plane)
                    rect_right = sketch_right.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_width - cab_thickness, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_right = sketch_right.profiles.item(0)
                    extrude_right_input = extrudes.createInput(profile_right, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_right_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(side_height))
                    extrude_right = extrudes.add(extrude_right_input)
                    if extrude_right.bodies.count > 0:
                        right_body = extrude_right.bodies.item(0)
                        right_body.name = "Cabinet_Right_Side"
                        bodies.append(right_body)
                    
                                
                    sketch_back = sketches.add(elevated_plane)
                    rect_back = sketch_back.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(cab_thickness, cab_depth - cab_thickness, 0),
                        adsk.core.Point3D.create(cab_width - cab_thickness, cab_depth, 0)
                    )
                    profile_back = sketch_back.profiles.item(0)
                    extrude_back_input = extrudes.createInput(profile_back, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_back_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(side_height))
                    extrude_back = extrudes.add(extrude_back_input)
                    if extrude_back.bodies.count > 0:
                        back_body = extrude_back.bodies.item(0)
                        back_body.name = "Cabinet_Back"
                        bodies.append(back_body)
                    
                               
                    top_plane_input = planes.createInput()
                    top_plane_input.setByOffset(sketch_plane, adsk.core.ValueInput.createByReal(cab_height - cab_thickness))
                    top_plane = planes.add(top_plane_input)
                    
                    sketch_top = sketches.add(top_plane)
                    rect_top = sketch_top.sketchCurves.sketchLines.addTwoPointRectangle(
                        adsk.core.Point3D.create(0, 0, 0),
                        adsk.core.Point3D.create(cab_width, cab_depth, 0)
                    )
                    profile_top = sketch_top.profiles.item(0)
                    extrude_top_input = extrudes.createInput(profile_top, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_top_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cab_thickness))
                    extrude_top = extrudes.add(extrude_top_input)
                    if extrude_top.bodies.count > 0:
                        top_body = extrude_top.bodies.item(0)
                        top_body.name = "Cabinet_Top"
                        bodies.append(top_body)
                    
                                        
                    self.create_drawers(design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness, 
                                      drawer_count, drawer_ply, drawer_base_ply, groove_height, effective_spacing,
                                      slides_thickness, drawer_height, drawer_width, drawer_depth, bodies,
                                      custom_drawer_depth, create_front_panels, front_panel_spacing)
                    
                                                       
                    try:
                        material_libs = app.materialLibraries
                        pine_names = ['Pino', 'Pine', 'Pine Wood']
                        pine_mat = None
                        
                        for i in range(material_libs.count):
                            mat_lib = material_libs.item(i)
                            for name in pine_names:
                                pine_mat = mat_lib.materials.itemByName(name)
                                if pine_mat:
                                    break
                            if pine_mat:
                                break
                        if pine_mat:
                            for body in bodies:
                                body.material = pine_mat
                    except Exception as mat_error:
                        pass
                    
                                                
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        is_double = door_type_dd and door_type_dd.selectedItem and door_type_dd.selectedItem.name == 'Double'
                        self.create_cabinet_door(design, sketch_plane, cab_width, cab_height, cab_depth, cab_thickness, unit_type, bodies, is_double)
                    
                                                                                  
                    
                                           
                    door_info = ""
                    door_checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('cabinetDoor'))
                    if door_checkbox and door_checkbox.value:
                        door_type_dd = adsk.core.DropDownCommandInput.cast(inputs.itemById('doorType'))
                        door_type = door_type_dd.selectedItem.name if door_type_dd and door_type_dd.selectedItem else 'Single'
                        door_info = f"\nDoor: {door_type}"
                    
                    ui.messageBox(f'SUCCESS!\n\nCabinet with drawers created\n{len(bodies)} bodies created\nDrawers: {drawer_count}{door_info}')
                
                else:
                    ui.messageBox(f'Cabinet parameters created successfully!')
            
            else:           
                                    
                length_in = adsk.core.ValueCommandInput.cast(inputs.itemById('toekickWidth'))
                thickness_in = adsk.core.ValueCommandInput.cast(inputs.itemById('toekickThickness'))
                height_in = adsk.core.ValueCommandInput.cast(inputs.itemById('toekickHeight'))
                depth_in = adsk.core.ValueCommandInput.cast(inputs.itemById('toekickDepth'))
                
                if length_in:
                    add_or_update_param('Tk_Width', length_in.value, unit_type, 'Toekick Width')
                if height_in:
                    add_or_update_param('Tk_Height', height_in.value, unit_type, 'Toekick Height')
                if depth_in:
                    add_or_update_param('Tk_Depth', depth_in.value, unit_type, 'Toekick Depth')
                if thickness_in:
                    add_or_update_param('Tk_Ply_Thickness', thickness_in.value, unit_type, 'Plywood toekick thickness')

                                          
            if project_type == 'Toekick':
                                                  
                tk_length = length_in.value if length_in else 60.0
                tk_depth = depth_in.value if depth_in else 35.0
                tk_height = height_in.value if height_in else 10.0
                tk_thickness = thickness_in.value if thickness_in else 1.9
                inner_width = tk_length - (tk_thickness * 2)
                
                sketches = design.rootComponent.sketches
                features = design.rootComponent.features
                extrudes = features.extrudeFeatures
                bodies = []
                
                                                         
                sketch_plane = selected_sketch_plane
                plane_name = selected_plane_name
                
                                                                                       
                toekick_sketch = sketches.add(sketch_plane)
                lines = toekick_sketch.sketchCurves.sketchLines
                
                                                                     
                                                         
                lines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(tk_thickness, 0, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, 0, 0), adsk.core.Point3D.create(tk_thickness, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, tk_depth, 0), adsk.core.Point3D.create(0, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(0, tk_depth, 0), adsk.core.Point3D.create(0, 0, 0))
                
                                                                      
                                                                             
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, 0, 0), adsk.core.Point3D.create(tk_length, 0, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length, 0, 0), adsk.core.Point3D.create(tk_length, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length, tk_depth, 0), adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth, 0), adsk.core.Point3D.create(tk_length - tk_thickness, 0, 0))
                
                                                                
                                                                                    
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, 0, 0), adsk.core.Point3D.create(tk_length - tk_thickness, 0, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, 0, 0), adsk.core.Point3D.create(tk_length - tk_thickness, tk_thickness, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, tk_thickness, 0), adsk.core.Point3D.create(tk_thickness, tk_thickness, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, tk_thickness, 0), adsk.core.Point3D.create(tk_thickness, 0, 0))
                
                                                               
                                                                                                      
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, tk_depth - tk_thickness, 0), adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth - tk_thickness, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth - tk_thickness, 0), adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_length - tk_thickness, tk_depth, 0), adsk.core.Point3D.create(tk_thickness, tk_depth, 0))
                lines.addByTwoPoints(adsk.core.Point3D.create(tk_thickness, tk_depth, 0), adsk.core.Point3D.create(tk_thickness, tk_depth - tk_thickness, 0))
                
                                                               
                                          
                if toekick_sketch.profiles.count > 0:
                    profile_left = toekick_sketch.profiles.item(0)
                    extrude_input = extrudes.createInput(profile_left, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(tk_height))
                    extrude_feat = extrudes.add(extrude_input)
                    if extrude_feat.bodies.count > 0:
                        body = extrude_feat.bodies.item(0)
                        body.name = "Toekick_Left_Vertical"
                        bodies.append(body)
                
                                            
                if toekick_sketch.profiles.count > 1:
                    profile_back = toekick_sketch.profiles.item(1)
                    extrude_input = extrudes.createInput(profile_back, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(tk_height))
                    extrude_feat = extrudes.add(extrude_input)
                    if extrude_feat.bodies.count > 0:
                        body = extrude_feat.bodies.item(0)
                        body.name = "Toekick_Back_Horizontal"
                        bodies.append(body)
                
                                           
                if toekick_sketch.profiles.count > 2:
                    profile_right = toekick_sketch.profiles.item(2)
                    extrude_input = extrudes.createInput(profile_right, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(tk_height))
                    extrude_feat = extrudes.add(extrude_input)
                    if extrude_feat.bodies.count > 0:
                        body = extrude_feat.bodies.item(0)
                        body.name = "Toekick_Right_Vertical"
                        bodies.append(body)
                
                                             
                if toekick_sketch.profiles.count > 3:
                    profile_front = toekick_sketch.profiles.item(3)
                    extrude_input = extrudes.createInput(profile_front, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(tk_height))
                    extrude_feat = extrudes.add(extrude_input)
                    if extrude_feat.bodies.count > 0:
                        body = extrude_feat.bodies.item(0)
                        body.name = "Toekick_Front_Horizontal"
                        bodies.append(body)
                
                                                   
                try:
                    material_libs = app.materialLibraries
                    pine_names = ['Pino', 'Pine', 'Pine Wood']
                    pine_mat = None
                    
                    for i in range(material_libs.count):
                        mat_lib = material_libs.item(i)
                        for name in pine_names:
                            pine_mat = mat_lib.materials.itemByName(name)
                            if pine_mat:
                                break
                        if pine_mat:
                            break
                    if pine_mat:
                        for body in bodies:
                            body.material = pine_mat
                    else:
                        ui.messageBox("Could not find 'Pino', 'Pine', or 'Pine Wood' material in any Fusion 360 library. Bodies were created without this material.")
                except Exception as mat_error:
                    ui.messageBox(f'Material assignment failed: {str(mat_error)}')
                
                                                                              

                ui.messageBox(f'SUCCESS!\n\nToekick created with {len(bodies)} bodies\nPlane used: {plane_name}')
            else:
                ui.messageBox(f'{project_type} parameters created successfully!')

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



class WoodWorkingCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            
                                             
            cmd.commandCategoryName = 'Wood Working Wizard'
            cmd.isExecutedWhenPreEmpted = False
            
                                                      
                                                                                            
            cmd.isOKButtonVisible = True
            cmd.setDialogInitialSize(500, 700)
            cmd.setDialogMinimumSize(500, 700)
            
            on_execute = WoodWorkingExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)

                                      
            on_input_changed = WoodWorkingInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            _handlers.append(on_input_changed)

            inputs = cmd.commandInputs
            
                                         
                                              
            import os
            cmd_dir = os.path.dirname(os.path.realpath(__file__))
            banner_path = os.path.join(cmd_dir, 'resources', 'banner.png')
            
                              
            try:
                if os.path.exists(banner_path):
                    banner = inputs.addImageCommandInput('bannerImage', '', banner_path)
                    banner.isFullWidth = True
                    banner.isVisible = True
            except:
                pass                                         
            
                                    
            plane = inputs.addSelectionInput('planeSel', 'Sketch Plane', 'Select a planar face or construction plane (or leave empty for XY plane)')
            plane.addSelectionFilter('PlanarFaces')
            plane.addSelectionFilter('ConstructionPlanes')
            plane.setSelectionLimits(0, 1)                                    

                                   
            type_dd = inputs.addDropDownCommandInput('projectType', 'Project Type', adsk.core.DropDownStyles.TextListDropDownStyle)
            type_dd.listItems.add('Cabinet', True)
            type_dd.listItems.add('Toekick', False)
            type_dd.tooltip = ('Choose your woodworking project:\n\n'
                             '• Cabinet: Full cabinet with sides, back, top, bottom, and optional interior (shelves/drawers) and doors\n'
                             '• Toekick: Frame-style base for cabinets - creates the recessed area at floor level')

                                
            unit_dd = inputs.addDropDownCommandInput('unitType', 'Units', adsk.core.DropDownStyles.TextListDropDownStyle)
            unit_dd.listItems.add('mm', True)
            unit_dd.listItems.add('in', False)                                 
            unit_dd.listItems.add('cm', False)
            unit_dd.tooltip = ('Select measurement units for all dimensions:\n\n'
                             '• mm (millimeters): Precise measurements, common in European woodworking\n'
                             '• in (inches): Standard in North American woodworking\n'
                             '• cm (centimeters): Good balance between precision and readability')

                                                 
            cabinet_group = inputs.addGroupCommandInput('cabinetGroup', 'Cabinet Dimensions')
            cabinet_inputs = cabinet_group.children
            
            width_input = cabinet_inputs.addValueInput('cabinetWidth', 'Width', 'mm', adsk.core.ValueInput.createByReal(60.0))
            width_input.tooltip = 'Overall cabinet width (left to right). Standard kitchen cabinets: 30-90cm'
            
            height_input = cabinet_inputs.addValueInput('cabinetHeight', 'Height', 'mm', adsk.core.ValueInput.createByReal(72.0))
            height_input.tooltip = 'Overall cabinet height (floor to top). Standard base cabinets: 70-85cm'
            
            depth_input = cabinet_inputs.addValueInput('cabinetDepth', 'Depth', 'mm', adsk.core.ValueInput.createByReal(35.0))
            depth_input.tooltip = 'Overall cabinet depth (front to back). Standard base cabinets: 55-65cm'
            
            thickness_input = cabinet_inputs.addValueInput('cabinetThickness', 'Material Thickness', 'mm', adsk.core.ValueInput.createByReal(1.9))
            thickness_input.tooltip = 'Thickness of plywood/MDF panels. Common: 12mm (1.2cm), 15mm (1.5cm), 18mm (1.8cm)'

                                                                     
            cabinet_interior_dd = inputs.addDropDownCommandInput('cabinetInterior', 'Interior Configuration', adsk.core.DropDownStyles.TextListDropDownStyle)
            cabinet_interior_dd.listItems.add('None (Structure Only)', True)
            cabinet_interior_dd.listItems.add('Drawers', False)
            cabinet_interior_dd.listItems.add('Shelf', False)
            cabinet_interior_dd.isVisible = True
            cabinet_interior_dd.tooltip = ('Choose the interior configuration:\n\n'
                                         '• Structure Only: Basic cabinet box with top, bottom, sides, and back\n'
                                         '• Drawers: Cabinet with sliding drawers, grooves, and base panels\n'
                                         '• Shelf: Cabinet with fixed horizontal shelves for storage')

                                                         
            door_checkbox = inputs.addBoolValueInput('cabinetDoor', 'Add Door', True, '', False)
            door_checkbox.isVisible = True
            door_checkbox.tooltip = 'Add cabinet door(s) in open position'
            
                                                                                 
            door_type_dd = inputs.addDropDownCommandInput('doorType', 'Door Configuration', adsk.core.DropDownStyles.TextListDropDownStyle)
            door_type_dd.listItems.add('Single', True)
            door_type_dd.listItems.add('Double', False)
            door_type_dd.isVisible = False
            door_type_dd.tooltip = 'Single: One door covering full width\nDouble: Two doors side by side'

                                                         
            help_text = inputs.addTextBoxCommandInput('helpInfo', '', '', 4, True)
            help_text.isVisible = False
            help_text.formattedText = ('<b>Cabinet Interior Guide:</b><br><br>'
                                     '<b>Structure Only:</b> Creates the basic cabinet framework - perfect for custom interior layouts or when you want to add your own shelving later.<br><br>'
                                     '<b>Drawers:</b> Creates fully functional drawers with grooved sides for base panels. Includes slide clearance calculations.<br><br>'
                                     '<b>Shelf:</b> Creates fixed horizontal shelves evenly spaced within the cabinet - ideal for general storage.')

                                                     
            shelf_group = inputs.addGroupCommandInput('shelfGroup', 'Shelf Options')
            shelf_group.isVisible = False
            shelf_inputs = shelf_group.children
            shelf_inputs.addIntegerSpinnerCommandInput('shelfCount', 'Number of Shelves', 1, 10, 1, 1)

                                                      
            drawer_group = inputs.addGroupCommandInput('drawerGroup', 'Drawer Options')
            drawer_group.isVisible = False
            drawer_inputs = drawer_group.children
            drawer_inputs.addIntegerSpinnerCommandInput('drawerCount', 'Number of Drawers', 1, 10, 1, 1)
            drawer_inputs.addValueInput('drawerPlyThickness', 'Drawer Ply Thickness', 'mm', adsk.core.ValueInput.createByReal(1.2))
            drawer_inputs.addValueInput('drawerBasePlyThickness', 'Drawer Base Ply Thickness', 'mm', adsk.core.ValueInput.createByReal(0.6))
            drawer_inputs.addValueInput('grooveHeight', 'Groove Height from Bottom', 'mm', adsk.core.ValueInput.createByReal(0.6))
            drawer_inputs.addValueInput('drawerSpacing', 'Drawer Spacing', 'mm', adsk.core.ValueInput.createByReal(0.0))
            drawer_inputs.addValueInput('slidesThickness', 'Slides Thickness (each side)', 'mm', adsk.core.ValueInput.createByReal(0.6))
            drawer_depth_input = drawer_inputs.addValueInput('drawerDepth', 'Drawer Depth', 'mm', adsk.core.ValueInput.createByReal(25.0))
            drawer_depth_input.tooltip = 'Depth of the drawer boxes. Maximum allowed: Cabinet Depth - Cabinet Thickness. Default uses 80% of maximum.'
            
            drawer_height_input = drawer_inputs.addValueInput('drawerHeight', 'Individual Drawer Height', 'mm', adsk.core.ValueInput.createByReal(10.0))
            drawer_height_input.tooltip = 'Height of each individual drawer. Total height needed = (drawer_count * height) + (spacing * (count + 1)). Must fit within cabinet interior height.'
            
                                        
            drawer_front_checkbox = drawer_inputs.addBoolValueInput('drawerFrontPanels', 'Add Drawer Front Panels', True, '', False)
            drawer_front_checkbox.tooltip = 'Add front panels to drawers (cannot be used with doors)'
            drawer_front_spacing_input = drawer_inputs.addValueInput('drawerFrontSpacing', 'Front Panel Spacing', 'mm', adsk.core.ValueInput.createByReal(0.2))
            drawer_front_spacing_input.tooltip = 'Spacing between drawer front panels'
            drawer_front_spacing_input.isVisible = False                     

                                                
            toekick_group = inputs.addGroupCommandInput('toekickGroup', 'Toekick Parameters')
            toekick_group.isVisible = False
            toekick_inputs = toekick_group.children
            toekick_inputs.addValueInput('toekickWidth', 'Width', 'mm', adsk.core.ValueInput.createByReal(60.0))
            toekick_inputs.addValueInput('toekickHeight', 'Height', 'mm', adsk.core.ValueInput.createByReal(10.0))
            toekick_inputs.addValueInput('toekickDepth', 'Depth', 'mm', adsk.core.ValueInput.createByReal(35.0))
            toekick_inputs.addValueInput('toekickThickness', 'Plywood Thickness', 'mm', adsk.core.ValueInput.createByReal(1.9))
            
                                                                                      

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class WoodWorkingInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            changed_input = args.input
            inputs = changed_input.parentCommand.commandInputs
            
                                        
            if changed_input.id == 'projectType':
                type_dd = adsk.core.DropDownCommandInput.cast(changed_input)
                cabinet_group = inputs.itemById('cabinetGroup')
                toekick_group = inputs.itemById('toekickGroup')
                cabinet_interior_dd = inputs.itemById('cabinetInterior')
                door_checkbox = inputs.itemById('cabinetDoor')
                door_type_dd = inputs.itemById('doorType')
                shelf_group = inputs.itemById('shelfGroup')
                drawer_group = inputs.itemById('drawerGroup')
                
                if type_dd.selectedItem.name == 'Cabinet':
                    cabinet_group.isVisible = True
                    toekick_group.isVisible = False
                    cabinet_interior_dd.isVisible = True
                    door_checkbox.isVisible = True
                                            
                    help_text = inputs.itemById('helpInfo')
                    if help_text:
                        help_text.formattedText = ('<b>Cabinet Builder:</b><br><br>'
                                                 'Create a complete cabinet with customizable interior and door options. '
                                                 'Choose your interior configuration and door style to match your project needs. '
                                                 'All components will be generated with proper joinery and realistic proportions.')
                        help_text.isVisible = True
                                                                
                    if door_checkbox and door_checkbox.value:
                        door_type_dd.isVisible = True
                    else:
                        door_type_dd.isVisible = False
                                                
                    if cabinet_interior_dd.selectedItem and cabinet_interior_dd.selectedItem.name == 'Shelf':
                        shelf_group.isVisible = True
                        drawer_group.isVisible = False
                    elif cabinet_interior_dd.selectedItem and cabinet_interior_dd.selectedItem.name == 'Drawers':
                        shelf_group.isVisible = False
                        drawer_group.isVisible = True
                    else:
                        shelf_group.isVisible = False
                        drawer_group.isVisible = False
                else:                    
                    cabinet_group.isVisible = False
                    toekick_group.isVisible = True
                    cabinet_interior_dd.isVisible = False
                    door_checkbox.isVisible = False
                    door_type_dd.isVisible = False
                    shelf_group.isVisible = False
                    drawer_group.isVisible = False
                                            
                    help_text = inputs.itemById('helpInfo')
                    if help_text:
                        help_text.formattedText = ('<b>Toekick Builder:</b><br><br>'
                                                 'Create a frame-style base that goes under cabinets. '
                                                 'The toekick provides the recessed area at floor level where your feet can fit when standing at the cabinet. '
                                                 'Consists of left/right verticals and front/back horizontals forming a sturdy frame.')
                        help_text.isVisible = True
            
                                                 
            elif changed_input.id == 'cabinetInterior':
                interior_dd = adsk.core.DropDownCommandInput.cast(changed_input)
                shelf_group = inputs.itemById('shelfGroup')
                drawer_group = inputs.itemById('drawerGroup')
                help_text = inputs.itemById('helpInfo')
                
                if interior_dd.selectedItem and interior_dd.selectedItem.name == 'Shelf':
                    shelf_group.isVisible = True
                    drawer_group.isVisible = False
                    if help_text:
                        help_text.formattedText = ('<b>Shelf Configuration:</b><br><br>'
                                                 'Creates fixed horizontal shelves evenly distributed within the cabinet height. '
                                                 'Shelves are positioned between the side panels and sit flush with the front opening. '
                                                 'Perfect for storing books, dishes, or general items that don\'t require sliding access.')
                        help_text.isVisible = True
                elif interior_dd.selectedItem and interior_dd.selectedItem.name == 'Drawers':
                    shelf_group.isVisible = False
                    drawer_group.isVisible = True
                    if help_text:
                        help_text.formattedText = ('<b>Drawer Configuration:</b><br><br>'
                                                 'Creates fully functional drawers with front, back, left, and right panels. '
                                                 'Includes grooved sides for base panel insertion and accounts for drawer slide clearance. '
                                                 'Each drawer has a separate base panel that slides into grooves for easy assembly.')
                        help_text.isVisible = True
                elif interior_dd.selectedItem and interior_dd.selectedItem.name == 'None (Structure Only)':
                    shelf_group.isVisible = False
                    drawer_group.isVisible = False
                    if help_text:
                        help_text.formattedText = ('<b>Structure Only:</b><br><br>'
                                                 'Creates the basic cabinet framework: top, bottom, left side, right side, and back panel. '
                                                 'No internal shelves or drawers - gives you complete freedom to customize the interior later. '
                                                 'Ideal when you want to add custom shelving, wine racks, or other specialized storage.')
                        help_text.isVisible = True
                else:
                    shelf_group.isVisible = False
                    drawer_group.isVisible = False
                    if help_text:
                        help_text.isVisible = False
            
                                         
            elif changed_input.id == 'cabinetDoor':
                door_checkbox = adsk.core.BoolValueCommandInput.cast(changed_input)
                door_type_dd = inputs.itemById('doorType')
                drawer_front_checkbox = inputs.itemById('drawerFrontPanels')
                
                if door_checkbox and door_checkbox.value:
                    door_type_dd.isVisible = True
                                                                       
                    if drawer_front_checkbox:
                        drawer_front_checkbox.value = False
                else:
                    door_type_dd.isVisible = False
            
                                                        
            elif changed_input.id == 'drawerFrontPanels':
                drawer_front_checkbox = adsk.core.BoolValueCommandInput.cast(changed_input)
                drawer_front_spacing = inputs.itemById('drawerFrontSpacing')
                door_checkbox = inputs.itemById('cabinetDoor')
                
                if drawer_front_checkbox and drawer_front_checkbox.value:
                    drawer_front_spacing.isVisible = True
                                                                         
                    if door_checkbox:
                        door_checkbox.value = False
                                                      
                        door_type_dd = inputs.itemById('doorType')
                        if door_type_dd:
                            door_type_dd.isVisible = False
                else:
                    drawer_front_spacing.isVisible = False
            
                                
            elif changed_input.id == 'unitType':
                unit_dd = adsk.core.DropDownCommandInput.cast(changed_input)
                unit = unit_dd.selectedItem.name
                
                                                       
                cabinet_group = adsk.core.GroupCommandInput.cast(inputs.itemById('cabinetGroup'))
                if cabinet_group:
                    for i in range(cabinet_group.children.count):
                        value_input = adsk.core.ValueCommandInput.cast(cabinet_group.children.item(i))
                        if value_input:
                            value_input.unitType = unit
                
                shelf_group = adsk.core.GroupCommandInput.cast(inputs.itemById('shelfGroup'))
                if shelf_group:
                    for i in range(shelf_group.children.count):
                        value_input = adsk.core.ValueCommandInput.cast(shelf_group.children.item(i))
                        if value_input:
                            value_input.unitType = unit

                drawer_group = adsk.core.GroupCommandInput.cast(inputs.itemById('drawerGroup'))
                if drawer_group:
                    for i in range(drawer_group.children.count):
                        value_input = adsk.core.ValueCommandInput.cast(drawer_group.children.item(i))
                        if value_input:
                            value_input.unitType = unit

                toekick_group = adsk.core.GroupCommandInput.cast(inputs.itemById('toekickGroup'))
                if toekick_group:
                    for i in range(toekick_group.children.count):
                        value_input = adsk.core.ValueCommandInput.cast(toekick_group.children.item(i))
                        if value_input:
                            value_input.unitType = unit
            
                                                                      
            elif changed_input.id in ['cabinetDepth', 'cabinetThickness', 'cabinetHeight']:
                                        
                cab_depth_input = inputs.itemById('cabinetDepth')
                cab_thickness_input = inputs.itemById('cabinetThickness')
                cab_height_input = inputs.itemById('cabinetHeight')
                drawer_depth_input = inputs.itemById('drawerDepth')
                drawer_height_input = inputs.itemById('drawerHeight')
                
                if cab_depth_input and cab_thickness_input and drawer_depth_input:
                    cab_depth = cab_depth_input.value
                    cab_thickness = cab_thickness_input.value
                    
                                                            
                    max_drawer_depth = cab_depth - cab_thickness
                    recommended_depth = max_drawer_depth * 0.8                                 
                    
                                                       
                    drawer_depth_input.tooltip = f'Drawer depth. Maximum: {max_drawer_depth:.1f}cm. Current max calculation: {cab_depth:.1f} - {cab_thickness:.1f} = {max_drawer_depth:.1f}cm'
                    
                                                                          
                    if drawer_depth_input.value > max_drawer_depth:
                        drawer_depth_input.value = recommended_depth
                
                                             
                if cab_height_input and cab_thickness_input and drawer_height_input:
                    cab_height = cab_height_input.value
                    cab_thickness = cab_thickness_input.value
                    drawer_count_input = inputs.itemById('drawerCount')
                    drawer_spacing_input = inputs.itemById('drawerSpacing')
                    
                    if drawer_count_input and drawer_spacing_input:
                        drawer_count = drawer_count_input.value
                        drawer_spacing = drawer_spacing_input.value
                        
                                                                
                        available_height = cab_height - (2 * cab_thickness)                          
                        total_spacing = drawer_spacing * (drawer_count + 1)                                            
                        max_drawer_height = (available_height - total_spacing) / drawer_count
                        
                                        
                        drawer_height_input.tooltip = f'Individual drawer height. Maximum: {max_drawer_height:.1f}cm (with {drawer_count} drawers and {drawer_spacing:.1f}cm spacing). Available space: {available_height:.1f}cm'
                        
                                                                     
                        if drawer_height_input.value > max_drawer_height:
                            drawer_height_input.value = max_drawer_height * 0.9                  
            
                                                                            
            elif changed_input.id in ['drawerCount', 'drawerSpacing']:
                cab_height_input = inputs.itemById('cabinetHeight')
                cab_thickness_input = inputs.itemById('cabinetThickness')
                drawer_height_input = inputs.itemById('drawerHeight')
                drawer_count_input = inputs.itemById('drawerCount')
                drawer_spacing_input = inputs.itemById('drawerSpacing')
                
                if all([cab_height_input, cab_thickness_input, drawer_height_input, drawer_count_input, drawer_spacing_input]):
                    cab_height = cab_height_input.value
                    cab_thickness = cab_thickness_input.value
                    drawer_count = drawer_count_input.value
                    drawer_spacing = drawer_spacing_input.value
                    
                                                                          
                    available_height = cab_height - (2 * cab_thickness)
                    total_spacing = drawer_spacing * (drawer_count + 1)
                    max_drawer_height = (available_height - total_spacing) / drawer_count if drawer_count > 0 else 0
                    
                                    
                    drawer_height_input.tooltip = f'Individual drawer height. Maximum: {max_drawer_height:.1f}cm (with {drawer_count} drawers and {drawer_spacing:.1f}cm spacing). Available space: {available_height:.1f}cm'
                    
                                                                 
                    if max_drawer_height > 0 and drawer_height_input.value > max_drawer_height:
                        drawer_height_input.value = max_drawer_height * 0.9
                            
        except:
            if _ui:
                _ui.messageBox('Input changed failed:\n{}'.format(traceback.format_exc()))


                                              
                                       
                                              

class UpdateCheckExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface if app else None
            if not ui:
                return
                                                                                     
            try:
                from . import updater as updater                
            except Exception:
                try:
                    import updater                
                except Exception as e:
                    ui.messageBox(f'Updater module not found or failed to import.\n{e}')
                    return

            newer, _msg, manifest = updater.check_for_update()
            if newer:
                latest = manifest.get('latestVersion', 'new version')
                try:
                    btn = ui.messageBox(
                        f'A new version is available: {latest}.\n\nDo you want to download and install it now?',
                        'WoodWorking Wizard - Update Available',
                        adsk.core.MessageBoxButtonTypes.YesNoButtonType,                
                        adsk.core.MessageBoxIconTypes.QuestionIconType                  
                    )
                    try:
                        yes_val = adsk.core.DialogResults.DialogYes                
                    except:
                        yes_val = 1
                    if btn == yes_val:
                        ok, umsg = updater.apply_update_from_manifest(manifest)
                        ui.messageBox(umsg)
                except:
                    ok, umsg = updater.apply_update_from_manifest(manifest)
                    if ok:
                        ui.messageBox(umsg)
            else:
                try:
                    ui.messageBox('You are up to date.')
                except:
                    pass
        except:
            if _ui:
                _ui.messageBox('Update check failed:\n{}'.format(traceback.format_exc()))


class UpdateCheckCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
                                                        
            handler = UpdateCheckExecuteHandler()
            cmd.execute.add(handler)
            _handlers.append(handler)
            cmd.setDialogInitialSize(300, 100)
            cmd.setDialogMinimumSize(300, 100)
        except:
            if _ui:
                _ui.messageBox('Update command creation failed:\n{}'.format(traceback.format_exc()))


                                              
                               
                                              

class CutListExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            if not design:
                ui.messageBox('No active design found.')
                return
            
                                    
            inputs = args.command.commandInputs
            
                                                          
            selection_input = adsk.core.SelectionCommandInput.cast(inputs.itemById('cutlistSelection'))
            selected_bodies = []
            
            if selection_input:
                for i in range(selection_input.selectionCount):
                    entity = selection_input.selection(i).entity
                    if hasattr(entity, 'objectType'):
                        if entity.objectType == adsk.fusion.BRepBody.classType():
                            selected_bodies.append(entity)
            
            if len(selected_bodies) == 0:
                ui.messageBox('Please select at least one body to generate a cut list.\n\nTip: Click on bodies in the browser or in the canvas.')
                return
            
                           
            unit_input = adsk.core.DropDownCommandInput.cast(inputs.itemById('cutlistUnit'))
            unit_type = 'mm'           
            if unit_input and unit_input.selectedItem:
                unit_name = unit_input.selectedItem.name
                if unit_name == 'Millimeters':
                    unit_type = 'mm'
                elif unit_name == 'Centimeters':
                    unit_type = 'cm'
                elif unit_name == 'Inches':
                    unit_type = 'in'
            
                              
            project_name_input = adsk.core.StringValueCommandInput.cast(inputs.itemById('cutlistProjectName'))
            project_name = "Selected_Bodies"
            if project_name_input and project_name_input.value.strip():
                project_name = project_name_input.value.strip()
            
                                 
            enable_nesting_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('enableNesting'))
            enable_nesting = enable_nesting_input.value if enable_nesting_input else False
            
            sheet_width = 244.0           
            sheet_height = 122.0
            kerf = 0.3
            edge_margin = 1.0
            rotation_allowed = True
            create_3d_visualization = True
            show_labels = True
            z_spacing = 10.0
            
            if enable_nesting:
                sheet_width_input = adsk.core.ValueCommandInput.cast(inputs.itemById('sheetWidth'))
                if sheet_width_input:
                    sheet_width = sheet_width_input.value
                
                sheet_height_input = adsk.core.ValueCommandInput.cast(inputs.itemById('sheetHeight'))
                if sheet_height_input:
                    sheet_height = sheet_height_input.value
                
                kerf_input = adsk.core.ValueCommandInput.cast(inputs.itemById('kerf'))
                if kerf_input:
                    kerf = kerf_input.value
                
                edge_margin_input = adsk.core.ValueCommandInput.cast(inputs.itemById('edgeMargin'))
                if edge_margin_input:
                    edge_margin = edge_margin_input.value
                
                rotation_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('allowRotation'))
                if rotation_input:
                    rotation_allowed = rotation_input.value
                
                create_3d_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('create3DVisualization'))
                if create_3d_input:
                    create_3d_visualization = create_3d_input.value
                
                show_labels_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('showLabels'))
                show_labels = show_labels_input.value if show_labels_input else True
                
                z_spacing_input = adsk.core.ValueCommandInput.cast(inputs.itemById('zSpacing'))
                if z_spacing_input:
                    z_spacing = z_spacing_input.value
            
                                              
            gen_csv = False
            csv_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('generateCsv'))
            if csv_input:
                gen_csv = csv_input.value
            
            if not gen_csv and not enable_nesting:
                ui.messageBox('Please enable at least one output: CSV or Nesting Layout.')
                return

                               
            import datetime
            import webbrowser
            
            cutlist_gen = CutListGenerator(design, unit_type)
            cutlist_gen.extract_components_from_bodies(selected_bodies)
            
                                     
            from pathlib import Path
            output_dir = Path.home() / "Documents" / "WoodWorkingWizard_CutLists"
            output_dir.mkdir(parents=True, exist_ok=True)
            
                                
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{project_name}_{timestamp}"
            
                                      
            outputs_lines = []
            csv_path = output_dir / f"{base_filename}.csv"
            csv_ok = False

                                                                                  
            layout_message = ""
            sheets = None
            if enable_nesting:
                success, sheet_count, created_bodies, sheets = cutlist_gen.generate_nesting_layout(
                    str(output_dir),
                    sheet_width=sheet_width,
                    sheet_height=sheet_height,
                    kerf=kerf,
                    edge_margin=edge_margin,
                    rotation_allowed=rotation_allowed,
                    create_3d_visualization=create_3d_visualization,
                    z_spacing=z_spacing,
                    show_labels=show_labels
                )
                
                if success:
                    bodies_msg = f'{len(created_bodies)} 3D bodies created' if create_3d_visualization else 'Layout calculated'
                    layout_message = f'\n\nNesting Layout:\n{sheet_count} sheets required\n{bodies_msg}'
                else:
                    layout_message = f'\n\nNesting layout generation failed: {sheet_count}'

                                                                           
            if gen_csv:
                ok, _ = cutlist_gen.generate_csv_report(str(csv_path), sheets=sheets)
                csv_ok = ok
            
                                  
                                               
            if csv_ok:
                outputs_lines.append(f'CSV Export: {csv_path.name}')
            outputs_text = '\n'.join(outputs_lines) if outputs_lines else 'No reports generated'

            ui.messageBox(
                f'Cut List Generated Successfully!\n\n'
                f'Bodies processed: {len(selected_bodies)}\n'
                f'Components found: {len(cutlist_gen.components)}\n\n'
                f'{outputs_text}'
                f'{layout_message}\n\n'
                f'Files saved to:\n{output_dir}'
            )
            
        except:
            if _ui:
                _ui.messageBox('Cut List generation failed:\n{}'.format(traceback.format_exc()))


class CutListCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.command
            inputs = cmd.commandInputs
            
                                         
            cmd_dir = os.path.dirname(os.path.realpath(__file__))
            banner_path = os.path.join(cmd_dir, 'resources', 'banner.png')
            
            try:
                if os.path.exists(banner_path):
                    banner = inputs.addImageCommandInput('bannerImage', '', banner_path)
                    banner.isFullWidth = True
                    banner.isVisible = True
            except:
                pass                                         
            
                                            
            selection_input = inputs.addSelectionInput('cutlistSelection', 'Select Bodies', 'Select one or more bodies for the cut list')
            selection_input.addSelectionFilter(adsk.core.SelectionCommandInput.Bodies)
            selection_input.setSelectionLimits(0, 0)                 
            
                                    
            project_name_input = inputs.addStringValueInput('cutlistProjectName', 'Project Name', 'My_Project')
            project_name_input.tooltip = 'Enter a name for this cut list project'
            
                                
            unit_dropdown = inputs.addDropDownCommandInput('cutlistUnit', 'Unit', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            unit_items = unit_dropdown.listItems
            unit_items.add('Millimeters', True, '')                 
            unit_items.add('Centimeters', False, '')
            unit_items.add('Inches', False, '')
            
                                         
            outputs_group = inputs.addGroupCommandInput('outputsGroup', 'Outputs')
            outputs_group.isExpanded = True
            outputs_inputs = outputs_group.children
            outputs_inputs.addBoolValueInput('generateCsv', 'CSV Export (spreadsheet)', True, '', True)

                                       
            nesting_group = inputs.addGroupCommandInput('nestingGroup', 'Nesting Layout Options')
            nesting_group.isExpanded = True
            nesting_group_inputs = nesting_group.children
            
                                     
            enable_nesting = nesting_group_inputs.addBoolValueInput('enableNesting', 'Generate Nesting Layout', True, '', True)
            enable_nesting.tooltip = 'Create optimized sheet layouts for cutting'
            
                              
            sheet_width = nesting_group_inputs.addValueInput('sheetWidth', 'Sheet Width', 'cm', adsk.core.ValueInput.createByReal(244))
            sheet_width.tooltip = 'Standard: 244cm (8 feet)'
            
            sheet_height = nesting_group_inputs.addValueInput('sheetHeight', 'Sheet Height', 'cm', adsk.core.ValueInput.createByReal(122))
            sheet_height.tooltip = 'Standard: 122cm (4 feet)'
            
                                        
            kerf = nesting_group_inputs.addValueInput('kerf', 'Kerf (Blade Width)', 'cm', adsk.core.ValueInput.createByReal(0.3))
            kerf.tooltip = 'Spacing between pieces for saw blade'
            
                         
            edge_margin = nesting_group_inputs.addValueInput('edgeMargin', 'Edge Margin', 'cm', adsk.core.ValueInput.createByReal(1.0))
            edge_margin.tooltip = 'Safety margin from sheet edges (parts stay away from edges by this amount)'
            
                              
            rotation = nesting_group_inputs.addBoolValueInput('allowRotation', 'Allow 90° Rotation', True, '', True)
            rotation.tooltip = 'Allow pieces to be rotated for better packing'
            
                              
            create_3d = nesting_group_inputs.addBoolValueInput('create3DVisualization', 'Create 3D Visualization in Fusion', True, '', True)
            create_3d.tooltip = 'Create 3D bodies showing nested layout with transparent sheets'
            
                                             
            show_labels = nesting_group_inputs.addBoolValueInput('showLabels', 'Show Component Labels', True, '', True)
            show_labels.tooltip = 'Display component names as text on nested pieces'
            
                                            
            z_spacing = nesting_group_inputs.addValueInput('zSpacing', 'Sheet Spacing (vertical)', 'cm', adsk.core.ValueInput.createByReal(10.0))
            z_spacing.tooltip = 'Vertical spacing between sheets in 3D view'
            
                           
            info_text = inputs.addTextBoxCommandInput('cutlistInfo', '', 
                '<b>Generate Cut List with Nesting Layout</b><br><br>'
                'This tool creates detailed cut lists and optimized sheet layouts.<br><br>'
                '<b>Features:</b><br>'
                '• Extracts dimensions from each body<br>'
                '• Groups components by material & thickness<br>'
                '• Generates optimized nesting layouts with 3D visualization<br>'
                '• Calculates sheet utilization<br>'
                '• Exports to CSV format<br><br>'
                '<b>Usage:</b><br>'
                '1. Select bodies in the browser or canvas<br>'
                '2. Choose your preferred unit<br>'
                '3. Configure sheet dimensions and nesting options<br>'
                '4. Click OK to generate', 
                8, True)
            
                             
            cmd.setDialogInitialSize(550, 700)
            cmd.setDialogMinimumSize(550, 700)
            
                                 
            execute_handler = CutListExecuteHandler()
            cmd.execute.add(execute_handler)
            _handlers.append(execute_handler)
            
        except:
            if _ui:
                _ui.messageBox('Cut List command creation failed:\n{}'.format(traceback.format_exc()))


def run(context):
    global _ui, _cmd_def, _btn_control, _panel, _cutlist_cmd_def, _cutlist_btn_control
    try:
        app = adsk.core.Application.get()
        _ui = app.userInterface if app else None
        if _ui is None:
            return

                                                        
        try:
                                                                          
            try:
                from . import updater as updater                
            except Exception:
                import updater                
            newer, _msg, manifest = updater.check_for_update()
            if newer and _ui is not None:
                latest = manifest.get('latestVersion', 'new version')
                try:
                    btn = _ui.messageBox(
                        f'A new version is available: {latest}.\n\nDo you want to download and install it now?',
                        'WoodWorking Wizard - Update Available',
                        adsk.core.MessageBoxButtonTypes.YesNoButtonType,                
                        adsk.core.MessageBoxIconTypes.QuestionIconType                  
                    )
                    try:
                        yes_val = adsk.core.DialogResults.DialogYes                
                    except:
                        yes_val = 1
                    if btn == yes_val:
                        ok, umsg = updater.apply_update_from_manifest(manifest)
                        _ui.messageBox(umsg)
                except:
                    ok, umsg = updater.apply_update_from_manifest(manifest)
                    if ok:
                        _ui.messageBox(umsg)
        except:
                                                              
            pass

                                          
        cmd_dir = os.path.dirname(os.path.realpath(__file__))
        cmd_resources = os.path.join(cmd_dir, 'resources')
        
                                                                                    
                                                                                   
        cutlist_resources = os.path.join(cmd_dir, 'resources', 'cutlist')
        try:
            os.makedirs(cutlist_resources, exist_ok=True)
                                                         
            src16_alt = os.path.join(cmd_resources, '16x16_1.png')
            src32_alt = os.path.join(cmd_resources, '32x32_1.png')
            dest16 = os.path.join(cutlist_resources, '16x16.png')
            dest32 = os.path.join(cutlist_resources, '32x32.png')
            
            if os.path.exists(src16_alt) and os.path.exists(src32_alt):
                shutil.copyfile(src16_alt, dest16)
                shutil.copyfile(src32_alt, dest32)
            else:
                                                                   
                src16 = os.path.join(cmd_resources, '16x16.png')
                src32 = os.path.join(cmd_resources, '32x32.png')
                if os.path.exists(src16):
                    shutil.copyfile(src16, dest16)
                if os.path.exists(src32):
                    shutil.copyfile(src32, dest32)
        except Exception:
                                                                               
            pass
        
                                                  
        cmd_id = 'WoodWorkingWizard'
        cmd_name = 'WoodWorking Wizard'
        cmd_desc = 'Create woodworking projects with user parameters'
        
        cmd_defs = _ui.commandDefinitions
        _cmd_def = cmd_defs.itemById(cmd_id)
        if not _cmd_def:
            _cmd_def = cmd_defs.addButtonDefinition(cmd_id, cmd_name, cmd_desc, cmd_resources)

        created_handler = WoodWorkingCreatedHandler()
        _cmd_def.commandCreated.add(created_handler)
        _handlers.append(created_handler)

                                   
        cutlist_cmd_id = 'WoodWorkingCutList'
        cutlist_cmd_name = 'Generate Cut List'
        cutlist_cmd_desc = 'Generate a cut list from selected bodies'
        
        _cutlist_cmd_def = cmd_defs.itemById(cutlist_cmd_id)
        if not _cutlist_cmd_def:
                                                                                
            _cutlist_cmd_def = cmd_defs.addButtonDefinition(cutlist_cmd_id, cutlist_cmd_name, cutlist_cmd_desc, cutlist_resources)
        
        cutlist_created_handler = CutListCreatedHandler()
        _cutlist_cmd_def.commandCreated.add(cutlist_created_handler)
        _handlers.append(cutlist_created_handler)

                                          
        workspaces = _ui.workspaces
        design_ws = workspaces.itemById('FusionSolidEnvironment')
        if design_ws:
                                          
            _panel = design_ws.toolbarPanels.itemById('SolidCreatePanel')
            if _panel:
                                         
                if _panel.controls.itemById(cmd_id) is None:
                    _btn_control = _panel.controls.addCommand(_cmd_def)
                    _btn_control.isPromoted = True
                
                                      
                if _panel.controls.itemById(cutlist_cmd_id) is None:
                    _cutlist_btn_control = _panel.controls.addCommand(_cutlist_cmd_def)
                    _cutlist_btn_control.isPromoted = True

                                                                   
                update_cmd_id = 'WoodWorkingUpdateCheck'
                update_cmd_name = 'Check for Updates'
                update_cmd_desc = 'Check online for a newer version and install it'

                update_cmd_def = cmd_defs.itemById(update_cmd_id)
                if not update_cmd_def:
                    update_cmd_def = cmd_defs.addButtonDefinition(update_cmd_id, update_cmd_name, update_cmd_desc, cmd_resources)

                update_created_handler = UpdateCheckCreatedHandler()
                update_cmd_def.commandCreated.add(update_created_handler)
                _handlers.append(update_created_handler)

                if _panel.controls.itemById(update_cmd_id) is None:
                    upd_btn = _panel.controls.addCommand(update_cmd_def)
                    upd_btn.isPromoted = False
                
    except:
        if _ui:
            _ui.messageBox('Add-in run failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    global _ui, _cmd_def, _btn_control, _panel, _cutlist_cmd_def, _cutlist_btn_control
    try:
        if _ui is None:
            app = adsk.core.Application.get()
            _ui = app.userInterface if app else None

        if _panel:
                                       
            if _btn_control:
                try:
                    _panel.controls.itemById(_btn_control.id).deleteMe()
                except:
                    pass
                _btn_control = None
            
                                    
            if _cutlist_btn_control:
                try:
                    _panel.controls.itemById(_cutlist_btn_control.id).deleteMe()
                except:
                    pass
                _cutlist_btn_control = None

                                               
        if _cmd_def:
            try:
                _ui.commandDefinitions.itemById(_cmd_def.id).deleteMe()
            except:
                pass
            _cmd_def = None
        
                                            
        if _cutlist_cmd_def:
            try:
                _ui.commandDefinitions.itemById(_cutlist_cmd_def.id).deleteMe()
            except:
                pass
            _cutlist_cmd_def = None
            
                        
        _handlers.clear()
        
    except:
        if _ui:
            _ui.messageBox('Add-in stop failed:\n{}'.format(traceback.format_exc()))