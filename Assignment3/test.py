import xml.etree.ElementTree as ET
import os
import sys
from domain import DomainData  # Assicurati che il modulo DomainData sia accessibile

def main():
    # !!! IMPORTANTE: Sostituisci questo percorso con il percorso reale del tuo file .gbs !!!
    gbs_file_path = "general.gbs"  # O usa "/" come separatore

    print(f"Attempting to load GBS file: {gbs_file_path}")

    # Controlla se il file esiste ed è un file regolare
    if not os.path.exists(gbs_file_path) or not os.path.isfile(gbs_file_path):
        print(f"Error: GBS file not found or is not a valid file at path: {gbs_file_path}", file=sys.stderr)
        return  # Esce se il file non esiste

    try:
        # Fare il parsing del file XML. ElementTree è l'equivalente più vicino
        # all'idea di "caricare" la struttura del documento.
        tree = ET.parse(gbs_file_path)
        root = tree.getroot() # L'elemento radice (<domain>)

        # Validazione base: controlla che il tag root sia <domain>
        if root.tag != 'domain':
             raise ValueError(f"Root element is <{root.tag}>, expected <domain>")

        # --- Estrai le informazioni corrispondenti ai getter Java ---
        # Non stiamo creando un oggetto DomainData completo, ma estraiamo
        # le stesse informazioni direttamente dall'albero XML.

        # domainData.getDomain()
        domain_name = root.get('name', 'N/A') # Usa 'N/A' se l'attributo manca

        # domainData.getImportedFiles()
        imported_files = []
        imports_tag = root.find('imports') # Trova il tag <imports> (solo figlio diretto)
        if imports_tag is not None:
            # Trova tutti i tag <import> dentro <imports> e prendi l'attributo 'schema'
            imported_files = [imp.get('schema', 'N/A') for imp in imports_tag.findall('import')]

        # domainData.getnTopEntities()
        top_entities_count = 0
        entities_tag = root.find('entities') # Trova il tag <entities>
        if entities_tag is not None:
            # Conta i figli diretti <entity> dentro <entities>
            top_entities_count = len(entities_tag.findall('entity'))

        # domainData.getAllRelationships().size()
        # Trova *tutti* gli elementi <relationship> *ovunque* nell'albero
        all_relationships = root.findall('.//relationship')
        all_relationships_count = len(all_relationships)

        # domainData.getnRelRefs()
        # Trova *tutti* gli elementi <reference> che sono figli di <relationship> *ovunque*
        # Nota: In Java questo contatore veniva incrementato durante il parsing.
        # Qui lo calcoliamo a posteriori sull'intero albero parsato.
        n_rel_refs = len(root.findall('.//relationship/reference'))

        # domainData.getAxioms().size()
        axioms_count = 0
        axioms_tag = root.find('axioms') # Trova il tag <axioms>
        if axioms_tag is not None:
            # Conta i figli diretti <axiom> dentro <axioms>
            axioms_count = len(axioms_tag.findall('axiom'))

        # --- Stampa le informazioni estratte ---
        print(f"Successfully loaded domain: {domain_name}")
        print(f"Imported files: {imported_files}")
        print(f"Total top-level entities: {top_entities_count}")
        print(f"Total relationships loaded (including nested): {all_relationships_count}")
        print(f"Total relationship references: {n_rel_refs}")
        print(f"Axioms loaded: {axioms_count}")

    # Gestione degli errori
    except FileNotFoundError: # Già gestito dal controllo os.path, ma buona pratica
        print(f"Error: File not found at {gbs_file_path}", file=sys.stderr)
    except ET.ParseError as e:
        # Corrisponde a SAXException o errori di parsing XML
        print(f"Error parsing GBS file (XML structure issue): {e}", file=sys.stderr)
    except ValueError as e:
        # Per il nostro controllo custom sul tag root o altri errori di valore
         print(f"Error during loading (Invalid structure/value): {e}", file=sys.stderr)
    except Exception as e:
        # Cattura qualsiasi altra eccezione imprevista
        print(f"An unexpected error occurred during loading: {e}", file=sys.stderr)
        # Per debug più avanzato, potresti voler stampare il traceback:
        # import traceback
        # print(traceback.format_exc(), file=sys.stderr)


# Blocco standard per eseguire main() se lo script è lanciato direttamente
if __name__ == "__main__":
    main()