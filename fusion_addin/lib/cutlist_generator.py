"""
Generatore Lista Taglio Automatica
"""
from typing import List, Dict

try:
    import adsk.core
    import adsk.fusion
    _HAS_ADSK = True
except ImportError:
    _HAS_ADSK = False


class CutListGenerator:
    """Analizza bodies e genera lista taglio"""
    
    def analyze_bodies(self, bodies: List) -> List[Dict]:
        """Estrae dimensioni da bodies"""
        cutlist = []
        
        for body in bodies:
            bbox = body.boundingBox
            
            # Dimensioni cm
            l = (bbox.maxPoint.x - bbox.minPoint.x) / 10.0
            w = (bbox.maxPoint.y - bbox.minPoint.y) / 10.0
            h = (bbox.maxPoint.z - bbox.minPoint.z) / 10.0
            
            # Determina orientamento pannello
            dims = sorted([l, w, h])
            spessore = dims[0]
            lunghezza = dims[2]
            larghezza = dims[1]
            
            materiale = body.material.name if body.material else 'Non specificato'
            
            cutlist.append({
                'nome': body.name,
                'lunghezza': round(lunghezza, 1),
                'larghezza': round(larghezza, 1),
                'spessore': round(spessore, 1),
                'materiale': materiale,
                'quantita': 1,
                'area_m2': round((lunghezza * larghezza) / 10000.0, 3)
            })
        
        return cutlist
    
    def export_excel(self, cutlist, filepath):
        """Export Excel"""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = 'Lista Taglio'
            
            headers = ['Nome', 'Lunghezza (cm)', 'Larghezza (cm)', 
                      'Spessore (cm)', 'Materiale', 'Quantita', 'Area m2']
            ws.append(headers)
            
            for item in cutlist:
                ws.append([
                    item['nome'], item['lunghezza'], item['larghezza'],
                    item['spessore'], item['materiale'], 
                    item['quantita'], item['area_m2']
                ])
            
            wb.save(filepath)
        except ImportError:
            # Fallback CSV
            self.export_csv(cutlist, filepath.replace('.xlsx', '.csv'))
    
    def export_csv(self, cutlist, filepath):
        """Export CSV"""
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Nome', 'Lunghezza', 'Larghezza', 
                           'Spessore', 'Materiale', 'Quantita', 'Area'])
            for item in cutlist:
                writer.writerow([
                    item['nome'], item['lunghezza'], item['larghezza'],
                    item['spessore'], item['materiale'],
                    item['quantita'], item['area_m2']
                ])
