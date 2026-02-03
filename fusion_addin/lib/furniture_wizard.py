"""
Wizard per la creazione guidata di mobili parametrici
"""

import adsk.core
import adsk.fusion
import traceback
from typing import Optional, Dict, Any
from . import furniture_generator, ai_client, config_manager, material_manager

# Costanti per valori default
DEFAULT_SCHIENALE_OFFSET_CM = 0.8  # Offset default per schienale arretrato custom (8mm)


class FurnitureWizardCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando wizard mobili"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []  # FIX: mantieni riferimenti handlers per prevenire garbage collection
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Imposta dimensioni dialog ottimali (450x600px per non uscire da schermo)
            cmd.setDialogInitialSize(450, 600)
            
            # Aggiungi event handlers
            on_execute = FurnitureWizardExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)  # FIX: salva riferimento
            
            on_input_changed = FurnitureWizardInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            self._handlers.append(on_input_changed)  # FIX: salva riferimento
            
            on_destroy = FurnitureWizardDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)  # FIX: salva riferimento
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo tipo mobile
            group_tipo = inputs.addGroupCommandInput('gruppo_tipo', 'Tipo Mobile')
            group_tipo.isExpanded = False  # COLLASSATO
            tipo_inputs = group_tipo.children
            
            dropdown_tipo = tipo_inputs.addDropDownCommandInput(
                'tipo_mobile',
                'Seleziona tipo',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_tipo.listItems.add('Mobile Base', True)
            dropdown_tipo.listItems.add('Pensile', False)
            dropdown_tipo.listItems.add('Anta', False)
            dropdown_tipo.listItems.add('Cassetto', False)
            dropdown_tipo.listItems.add('Armadio', False)
            
            # Gruppo dimensioni
            group_dim = inputs.addGroupCommandInput('gruppo_dimensioni', 'Dimensioni (cm)')
            group_dim.isExpanded = True  # UNICO GRUPPO ESPANSO
            dim_inputs = group_dim.children
            
            dim_inputs.addValueInput('larghezza', 'Larghezza (L)', 'cm', 
                                    adsk.core.ValueInput.createByReal(80.0))
            dim_inputs.addValueInput('altezza', 'Altezza (H)', 'cm',
                                    adsk.core.ValueInput.createByReal(90.0))
            dim_inputs.addValueInput('profondita', 'Profondità (P)', 'cm',
                                    adsk.core.ValueInput.createByReal(60.0))
            
            # Gruppo parametri
            group_param = inputs.addGroupCommandInput('gruppo_parametri', 'Parametri')
            group_param.isExpanded = False  # COLLASSATO
            param_inputs = group_param.children
            
            param_inputs.addValueInput('spessore_pannello', 'Spessore pannello', 'cm',
                                      adsk.core.ValueInput.createByReal(1.8))
            param_inputs.addValueInput('spessore_schienale', 'Spessore schienale', 'cm',
                                      adsk.core.ValueInput.createByReal(0.6))
            param_inputs.addIntegerSpinnerCommandInput('num_ripiani', 'N. ripiani', 0, 10, 1, 2)
            
            # Sistema 32mm
            param_inputs.addBoolValueInput('sistema_32mm', 'Sistema 32mm', True, '', True)
            
            # Fori e ferramenta
            group_fori = inputs.addGroupCommandInput('gruppo_fori', 'Fori e Ferramenta')
            group_fori.isExpanded = False
            fori_inputs = group_fori.children
            
            fori_inputs.addBoolValueInput('fori_ripiani', 'Fori reggi-ripiano (Ø5)', True, '', True)
            fori_inputs.addBoolValueInput('spinatura', 'Spinatura Ø8', True, '', True)
            fori_inputs.addIntegerSpinnerCommandInput('num_cerniere', 'N. cerniere Ø35', 0, 10, 1, 2)
            
            # Ante e cassetti
            group_ante = inputs.addGroupCommandInput('gruppo_ante', 'Ante e Cassetti')
            group_ante.isExpanded = False
            ante_inputs = group_ante.children
            
            ante_inputs.addIntegerSpinnerCommandInput('num_ante', 'N. ante', 0, 10, 1, 0)
            ante_inputs.addIntegerSpinnerCommandInput('num_cassetti', 'N. cassetti', 0, 10, 1, 0)
            
            # Schienale
            group_schienale = inputs.addGroupCommandInput('gruppo_schienale', 'Schienale')
            group_schienale.isExpanded = False
            schienale_inputs = group_schienale.children
            
            dropdown_schienale = schienale_inputs.addDropDownCommandInput(
                'tipo_schienale',
                'Montaggio schienale',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_schienale.listItems.add('A filo dietro', True)
            dropdown_schienale.listItems.add('Incastrato (scanalatura 10mm)', False)
            dropdown_schienale.listItems.add('Arretrato custom', False)
            
            # Nota: Fusion 360 ValueInput usa unità del documento (default cm)
            # L'etichetta 'cm' è corretta e coerente con altri parametri
            schienale_inputs.addValueInput('arretramento_schienale', 'Arretramento (se custom)', 'cm',
                                          adsk.core.ValueInput.createByReal(DEFAULT_SCHIENALE_OFFSET_CM))
            schienale_inputs.itemById('arretramento_schienale').isEnabled = False
            
            # Zoccolo
            group_zoccolo = inputs.addGroupCommandInput('gruppo_zoccolo', 'Zoccolo')
            group_zoccolo.isExpanded = False
            zoccolo_inputs = group_zoccolo.children
            
            zoccolo_inputs.addBoolValueInput('con_zoccolo', 'Aggiungi zoccolo', True, '', True)
            zoccolo_inputs.addValueInput('altezza_zoccolo', 'Altezza zoccolo', 'cm',
                                        adsk.core.ValueInput.createByReal(10.0))
            
            # Gruppo Materiali e Finiture
            group_materiali = inputs.addGroupCommandInput('gruppo_materiali', 'Materiali e Finiture')
            group_materiali.isExpanded = False  # COLLASSATO
            materiali_inputs = group_materiali.children
            
            # Applica materiali
            materiali_inputs.addBoolValueInput('applica_materiali', 'Applica materiali', True, '', True)
            
            # Materiale unico o differenziato
            materiali_inputs.addBoolValueInput('materiale_unico', 'Materiale unico per tutto', True, '', True)
            
            # Dropdown materiale corpo
            dropdown_mat_corpo = materiali_inputs.addDropDownCommandInput(
                'materiale_corpo',
                'Materiale corpo',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            materiali_disponibili = [
                'Rovere', 'Noce', 'Laccato Bianco', 'Laccato Nero',
                'Melaminico Bianco', 'Melaminico Grigio'
            ]
            is_first = True
            for mat in materiali_disponibili:
                dropdown_mat_corpo.listItems.add(mat, is_first)
                is_first = False
            
            # Dropdown materiale ante (disabilitato se materiale unico)
            dropdown_mat_ante = materiali_inputs.addDropDownCommandInput(
                'materiale_ante',
                'Materiale ante',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            for mat in materiali_disponibili:
                dropdown_mat_ante.listItems.add(mat, False)
            dropdown_mat_ante.listItems.item(2).isSelected = True  # Laccato Bianco default
            materiali_inputs.itemById('materiale_ante').isEnabled = False
            
            # Dropdown materiale schienale (disabilitato se materiale unico)
            dropdown_mat_schienale = materiali_inputs.addDropDownCommandInput(
                'materiale_schienale',
                'Materiale schienale',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            for mat in materiali_disponibili:
                dropdown_mat_schienale.listItems.add(mat, False)
            dropdown_mat_schienale.listItems.item(4).isSelected = True  # Melaminico Bianco default
            materiali_inputs.itemById('materiale_schienale').isEnabled = False
            
            # Gruppo IA
            group_ia = inputs.addGroupCommandInput('gruppo_ia', 'Assistente IA')
            group_ia.isExpanded = False  # COLLASSATO
            ia_inputs = group_ia.children
            
            ia_inputs.addTextBoxCommandInput('descrizione_mobile', 'Descrivi il mobile', 
                                            'Es: mobile base cucina largo 80cm con 2 ripiani e 2 ante', 
                                            3, False)
            
            # Bottone per compilare campi da descrizione
            ia_inputs.addBoolValueInput('btn_compila_ia', 'Compila da Descrizione', False, '', False)
            ia_inputs.addBoolValueInput('usa_ia', 'Usa IA per suggerimenti', True, '', False)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione wizard:\n{}'.format(traceback.format_exc()))


class FurnitureWizardExecuteHandler(adsk.core.CommandEventHandler):
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
            params = self._extract_parameters(inputs)
            
            # Valida parametri
            validation_errors = furniture_generator.validate_parameters(params)
            if validation_errors:
                ui.messageBox('Errori di validazione:\n' + '\n'.join(validation_errors))
                return
            
            # Usa IA se richiesto
            if params.get('usa_ia') and params.get('descrizione_mobile'):
                try:
                    config = config_manager.load_config()
                    ai = ai_client.AIClient(
                        config.get('ai_endpoint', 'http://localhost:1234'),
                        model=config.get('ai_model', 'llama-3.2-3b-instruct'),
                        enable_fallback=True
                    )
                    
                    if not ai.is_available():
                        ui.messageBox('IA non disponibile - usando suggerimenti di fallback standard')
                    
                    suggestions = ai.get_furniture_suggestions(params['descrizione_mobile'])
                    if suggestions:
                        ui.messageBox('Suggerimenti IA:\n{}'.format(suggestions))
                except Exception as e:
                    # Non bloccare l'esecuzione se l'IA fallisce
                    ui.messageBox('Nota: IA non disponibile (continuando con parametri manuali)')
            
            # Genera mobile
            result = furniture_generator.generate_furniture(design, params)
            
            if result['success']:
                # Applica materiali se richiesto
                if params.get('applica_materiali', False):
                    mat_mgr = material_manager.MaterialManager(design)
                    component = design.rootComponent
                    
                    if params.get('materiale_unico', True):
                        # Materiale unico
                        mat_corpo = params.get('materiale_corpo', 'Rovere')
                        success = mat_mgr.apply_material_uniform(component, mat_corpo)
                        if success:
                            ui.messageBox('Mobile creato con successo!\n\n'
                                        'Componenti: {}\n'
                                        'Materiale applicato: {}\n\n'
                                        'Per esportare in Xilog Plus, usa il post-processore.'.format(
                                            ', '.join(result['components']), mat_corpo))
                        else:
                            ui.messageBox('Mobile creato con successo!\n\n'
                                        'Componenti: {}\n'
                                        'NOTA: Materiale non applicato (libreria non disponibile)\n\n'
                                        'Per esportare in Xilog Plus, usa il post-processore.'.format(
                                            ', '.join(result['components'])))
                    else:
                        # Materiali differenziati
                        materials_map = {
                            'fianco': params.get('materiale_corpo', 'Rovere'),
                            'ripiano': params.get('materiale_corpo', 'Rovere'),
                            'struttura': params.get('materiale_corpo', 'Rovere'),
                            'anta': params.get('materiale_ante', 'Laccato Bianco'),
                            'schienale': params.get('materiale_schienale', 'Melaminico Bianco')
                        }
                        success = mat_mgr.apply_materials_differentiated(component, materials_map)
                        if success:
                            ui.messageBox('Mobile creato con successo!\n\n'
                                        'Componenti: {}\n'
                                        'Materiali applicati:\n'
                                        '  - Corpo: {}\n'
                                        '  - Ante: {}\n'
                                        '  - Schienale: {}\n\n'
                                        'Per esportare in Xilog Plus, usa il post-processore.'.format(
                                            ', '.join(result['components']),
                                            materials_map['fianco'],
                                            materials_map['anta'],
                                            materials_map['schienale']))
                        else:
                            ui.messageBox('Mobile creato con successo!\n\n'
                                        'Componenti: {}\n'
                                        'NOTA: Materiali non applicati (libreria non disponibile)\n\n'
                                        'Per esportare in Xilog Plus, usa il post-processore.'.format(
                                            ', '.join(result['components'])))
                else:
                    ui.messageBox('Mobile creato con successo!\n\n'
                                'Componenti: {}\n'
                                'Per esportare in Xilog Plus, usa il post-processore.'.format(
                                    ', '.join(result['components'])))
            else:
                ui.messageBox('Errore creazione mobile:\n{}'.format(result['error']))
                
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore esecuzione wizard:\n{}'.format(traceback.format_exc()))
    
    def _extract_parameters(self, inputs: adsk.core.CommandInputs) -> Dict[str, Any]:
        """Estrae parametri dagli inputs del comando"""
        params = {}
        
        # Tipo mobile
        tipo_input = inputs.itemById('tipo_mobile')
        if tipo_input:
            params['tipo_mobile'] = tipo_input.selectedItem.name
        
        # Dimensioni (già in cm)
        params['larghezza'] = inputs.itemById('larghezza').value if inputs.itemById('larghezza') else 80.0
        params['altezza'] = inputs.itemById('altezza').value if inputs.itemById('altezza') else 90.0
        params['profondita'] = inputs.itemById('profondita').value if inputs.itemById('profondita') else 60.0
        
        # Spessori (già in cm)
        params['spessore_pannello'] = inputs.itemById('spessore_pannello').value if inputs.itemById('spessore_pannello') else 1.8
        params['spessore_schienale'] = inputs.itemById('spessore_schienale').value if inputs.itemById('spessore_schienale') else 0.6
        
        # Parametri numerici
        params['num_ripiani'] = inputs.itemById('num_ripiani').value if inputs.itemById('num_ripiani') else 2
        params['num_cerniere'] = inputs.itemById('num_cerniere').value if inputs.itemById('num_cerniere') else 2
        params['num_ante'] = inputs.itemById('num_ante').value if inputs.itemById('num_ante') else 0
        params['num_cassetti'] = inputs.itemById('num_cassetti').value if inputs.itemById('num_cassetti') else 0
        
        # Booleani
        params['sistema_32mm'] = inputs.itemById('sistema_32mm').value if inputs.itemById('sistema_32mm') else True
        params['fori_ripiani'] = inputs.itemById('fori_ripiani').value if inputs.itemById('fori_ripiani') else True
        params['spinatura'] = inputs.itemById('spinatura').value if inputs.itemById('spinatura') else True
        params['con_zoccolo'] = inputs.itemById('con_zoccolo').value if inputs.itemById('con_zoccolo') else True
        params['usa_ia'] = inputs.itemById('usa_ia').value if inputs.itemById('usa_ia') else False
        
        # Zoccolo
        params['altezza_zoccolo'] = inputs.itemById('altezza_zoccolo').value if inputs.itemById('altezza_zoccolo') else 10.0
        
        # Schienale
        tipo_schienale_input = inputs.itemById('tipo_schienale')
        if tipo_schienale_input:
            params['tipo_schienale'] = tipo_schienale_input.selectedItem.name
        else:
            params['tipo_schienale'] = 'A filo dietro'
        
        params['arretramento_schienale'] = inputs.itemById('arretramento_schienale').value if inputs.itemById('arretramento_schienale') else DEFAULT_SCHIENALE_OFFSET_CM
        
        # Materiali
        params['applica_materiali'] = inputs.itemById('applica_materiali').value if inputs.itemById('applica_materiali') else False
        params['materiale_unico'] = inputs.itemById('materiale_unico').value if inputs.itemById('materiale_unico') else True
        
        mat_corpo_input = inputs.itemById('materiale_corpo')
        if mat_corpo_input:
            params['materiale_corpo'] = mat_corpo_input.selectedItem.name
        
        mat_ante_input = inputs.itemById('materiale_ante')
        if mat_ante_input:
            params['materiale_ante'] = mat_ante_input.selectedItem.name
        
        mat_schienale_input = inputs.itemById('materiale_schienale')
        if mat_schienale_input:
            params['materiale_schienale'] = mat_schienale_input.selectedItem.name
        
        # IA
        desc_input = inputs.itemById('descrizione_mobile')
        if desc_input:
            params['descrizione_mobile'] = desc_input.text
        
        return params


class FurnitureWizardInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Handler per i cambiamenti negli input"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            changed_input = args.input
            inputs = args.inputs
            
            # Abilita/disabilita altezza zoccolo in base al checkbox
            if changed_input.id == 'con_zoccolo':
                altezza_zoccolo = inputs.itemById('altezza_zoccolo')
                if altezza_zoccolo:
                    altezza_zoccolo.isEnabled = changed_input.value
            
            # Abilita/disabilita materiali differenziati
            if changed_input.id == 'materiale_unico':
                mat_ante = inputs.itemById('materiale_ante')
                mat_schienale = inputs.itemById('materiale_schienale')
                if mat_ante:
                    mat_ante.isEnabled = not changed_input.value
                if mat_schienale:
                    mat_schienale.isEnabled = not changed_input.value
            
            # Abilita/disabilita arretramento custom in base al tipo schienale
            if changed_input.id == 'tipo_schienale':
                arretramento = inputs.itemById('arretramento_schienale')
                if arretramento:
                    arretramento.isEnabled = (changed_input.selectedItem.name == 'Arretrato custom')
            
            # Handler pulsante "Compila da Descrizione"
            if changed_input.id == 'btn_compila_ia':
                descrizione_input = inputs.itemById('descrizione_mobile')
                if descrizione_input and descrizione_input.text:
                    try:
                        # Usa AI Client per parsare la descrizione
                        config = config_manager.load_config()
                        ai = ai_client.AIClient(
                            config.get('ai_endpoint', 'http://localhost:1234'),
                            model=config.get('ai_model', 'llama-3.2-3b-instruct'),
                            enable_fallback=True
                        )
                        
                        params = ai.parse_furniture_description(descrizione_input.text)
                        
                        if params:
                            # Popola campi con parametri estratti
                            if 'larghezza' in params:
                                larg_input = inputs.itemById('larghezza')
                                if larg_input:
                                    larg_input.value = params['larghezza']
                            
                            if 'altezza' in params:
                                alt_input = inputs.itemById('altezza')
                                if alt_input:
                                    alt_input.value = params['altezza']
                            
                            if 'profondita' in params:
                                prof_input = inputs.itemById('profondita')
                                if prof_input:
                                    prof_input.value = params['profondita']
                            
                            if 'num_ripiani' in params:
                                ripiani_input = inputs.itemById('num_ripiani')
                                if ripiani_input:
                                    ripiani_input.value = params['num_ripiani']
                            
                            if 'num_ante' in params:
                                ante_input = inputs.itemById('num_ante')
                                if ante_input:
                                    ante_input.value = params['num_ante']
                            
                            if 'num_cassetti' in params:
                                cassetti_input = inputs.itemById('num_cassetti')
                                if cassetti_input:
                                    cassetti_input.value = params['num_cassetti']
                            
                            if 'tipo_schienale' in params:
                                schienale_input = inputs.itemById('tipo_schienale')
                                if schienale_input:
                                    # Trova l'item corrispondente
                                    for i in range(schienale_input.listItems.count):
                                        if params['tipo_schienale'] in schienale_input.listItems.item(i).name:
                                            schienale_input.listItems.item(i).isSelected = True
                                            break
                            
                            # Messaggio di conferma
                            app = adsk.core.Application.get()
                            ui = app.userInterface
                            confidence = params.get('confidence', 0.5)
                            if confidence >= 0.8:
                                msg = 'Parametri compilati con IA (affidabilita alta)'
                            elif confidence >= 0.5:
                                msg = 'Parametri compilati con parser fallback (affidabilita media)'
                            else:
                                msg = 'Parametri compilati parzialmente'
                            
                            if params.get('note'):
                                msg += '\n\nNote: ' + params['note']
                            
                            ui.messageBox(msg)
                    except Exception as e:
                        app = adsk.core.Application.get()
                        ui = app.userInterface
                        ui.messageBox('Errore compilazione da IA:\n{}'.format(str(e)))
                    
        except:
            pass


class FurnitureWizardDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
