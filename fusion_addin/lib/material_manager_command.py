"""
Comando per la gestione dei materiali
"""

import adsk.core
import adsk.fusion
import traceback
from typing import List
from . import material_manager


class MaterialManagerCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando gestione materiali"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Dimensioni dialog
            cmd.setDialogInitialSize(450, 500)
            
            # Event handlers
            on_execute = MaterialManagerExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_destroy = MaterialManagerDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Info
            info_text = inputs.addTextBoxCommandInput('info', '', 
                                                      'Gestione Materiali FurnitureAI\n\n'
                                                      'Applica materiali ai componenti del mobile selezionato.\n'
                                                      'Il sistema riconosce automaticamente il tipo di componente.',
                                                      4, True)
            info_text.isReadOnly = True
            
            # Gruppo Applicazione Materiali
            group_app = inputs.addGroupCommandInput('gruppo_applicazione', 'Applica Materiali')
            group_app.isExpanded = True
            app_inputs = group_app.children
            
            # Materiale unico o differenziato
            app_inputs.addBoolValueInput('materiale_unico', 'Materiale unico per tutto', True, '', True)
            
            # Dropdown materiale principale
            dropdown_mat = app_inputs.addDropDownCommandInput(
                'materiale_principale',
                'Materiale',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            materiali = [
                'Rovere', 'Noce', 'Laccato Bianco', 'Laccato Nero',
                'Melaminico Bianco', 'Melaminico Grigio', 'Vetro Trasparente',
                'Metallo Alluminio'
            ]
            for i, mat in enumerate(materiali):
                dropdown_mat.listItems.add(mat, i == 0)
            
            # Materiali differenziati (disabilitati di default)
            app_inputs.addTextBoxCommandInput('separator', '', 
                                             'Materiali differenziati (se non materiale unico):', 
                                             1, True).isReadOnly = True
            
            # Dropdown materiale corpo
            dropdown_corpo = app_inputs.addDropDownCommandInput(
                'materiale_corpo',
                'Corpo (fianchi, ripiani)',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            for mat in materiali:
                dropdown_corpo.listItems.add(mat, False)
            dropdown_corpo.listItems.item(0).isSelected = True
            app_inputs.itemById('materiale_corpo').isEnabled = False
            
            # Dropdown materiale ante
            dropdown_ante = app_inputs.addDropDownCommandInput(
                'materiale_ante',
                'Ante',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            for mat in materiali:
                dropdown_ante.listItems.add(mat, False)
            dropdown_ante.listItems.item(2).isSelected = True  # Laccato Bianco
            app_inputs.itemById('materiale_ante').isEnabled = False
            
            # Dropdown materiale schienale
            dropdown_schienale = app_inputs.addDropDownCommandInput(
                'materiale_schienale',
                'Schienale',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            for mat in materiali:
                dropdown_schienale.listItems.add(mat, False)
            dropdown_schienale.listItems.item(4).isSelected = True  # Melaminico Bianco
            app_inputs.itemById('materiale_schienale').isEnabled = False
            
            # Handler per cambiamenti input
            on_input_changed = MaterialManagerInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            self._handlers.append(on_input_changed)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione dialog gestione materiali:\n{}'.format(traceback.format_exc()))


class MaterialManagerExecuteHandler(adsk.core.CommandEventHandler):
    """Handler per l'esecuzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)
            
            if not design:
                ui.messageBox('Nessun design attivo')
                return
            
            # Ottieni parametri da inputs
            inputs = args.command.commandInputs
            
            materiale_unico = inputs.itemById('materiale_unico').value
            
            # Crea material manager
            mat_mgr = material_manager.MaterialManager(design)
            component = design.rootComponent
            
            if materiale_unico:
                # Materiale unico
                mat_principale = inputs.itemById('materiale_principale').selectedItem.name
                success = mat_mgr.apply_material_uniform(component, mat_principale)
                
                if success:
                    ui.messageBox('Materiali applicati con successo!\n\n'
                                'Materiale: {}'.format(mat_principale))
                else:
                    ui.messageBox('ATTENZIONE: Alcuni materiali potrebbero non essere stati applicati.\n\n'
                                'Verifica che i componenti esistano nel design.')
            else:
                # Materiali differenziati
                materials_map = {
                    'fianco': inputs.itemById('materiale_corpo').selectedItem.name,
                    'ripiano': inputs.itemById('materiale_corpo').selectedItem.name,
                    'struttura': inputs.itemById('materiale_corpo').selectedItem.name,
                    'anta': inputs.itemById('materiale_ante').selectedItem.name,
                    'schienale': inputs.itemById('materiale_schienale').selectedItem.name
                }
                
                success = mat_mgr.apply_materials_differentiated(component, materials_map)
                
                if success:
                    ui.messageBox('Materiali applicati con successo!\n\n'
                                'Corpo: {}\n'
                                'Ante: {}\n'
                                'Schienale: {}'.format(
                                    materials_map['fianco'],
                                    materials_map['anta'],
                                    materials_map['schienale']))
                else:
                    ui.messageBox('ATTENZIONE: Alcuni materiali potrebbero non essere stati applicati.\n\n'
                                'Verifica che i componenti esistano nel design.')
                
        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore applicazione materiali:\n{}'.format(str(e)))


class MaterialManagerInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Handler per i cambiamenti negli input"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            changed_input = args.input
            inputs = args.inputs
            
            # Abilita/disabilita materiali differenziati
            if changed_input.id == 'materiale_unico':
                mat_corpo = inputs.itemById('materiale_corpo')
                mat_ante = inputs.itemById('materiale_ante')
                mat_schienale = inputs.itemById('materiale_schienale')
                
                if mat_corpo:
                    mat_corpo.isEnabled = not changed_input.value
                if mat_ante:
                    mat_ante.isEnabled = not changed_input.value
                if mat_schienale:
                    mat_schienale.isEnabled = not changed_input.value
                    
        except:
            pass


class MaterialManagerDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
