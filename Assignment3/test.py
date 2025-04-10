from domain.DomainData import DomainData
from domain.Entity import Entity
from domain.Relationship import Relationship
from domain.Attribute import Attribute
from pathlib import Path
import os
import traceback

# --- Caricamento dati da un file .gbs ---
print("--- Caricamento da file .gbs ---")

# Sostituisci con il percorso effettivo del tuo file .gbs
# e della cartella WEB-INF se necessaria per gli import relativi
# Assicurati che il file .gbs sia nella cartella specificata da webInfFolder
# o in una sottocartella se usi import relativi.
gbs_file_name = "general.gbs" # <-- MODIFICA QUESTO NOME FILE
web_inf_folder = Path("c:/Users/fonta/Desktop/Uni/Repo/FOAI/Assignment3/") # <-- MODIFICA QUESTO PERCORSO se necessario

# Costruisci il percorso completo del file .gbs
gbs_file_path = web_inf_folder / gbs_file_name
domain_name = gbs_file_path.stem # Ottiene il nome del file senza estensione

# Controlla se la cartella WEB-INF e il file esistono
if web_inf_folder.exists() and web_inf_folder.is_dir() and gbs_file_path.exists() and gbs_file_path.is_file():
    try:
        # Usa il costruttore che accetta il nome del dominio e la cartella WEB-INF
        # Questo simula il caricamento come farebbe l'applicazione originale
        # cercando 'domain_name.gbs' dentro 'webInfFolder'
        domain_data_from_file = DomainData(path_or_bytearray=domain_name, webInfFolder=str(web_inf_folder))

        print(f"DomainData caricato per il dominio '{domain_name}' da '{web_inf_folder}'.")
        print(f"Dominio caricato: {domain_data_from_file.getDomain()}") # Dovrebbe corrispondere a domain_name

        # Stampa alcune informazioni caricate
        all_entities = domain_data_from_file.getAllEntitiesToString()
        print(f"Tutte le entità caricate ({len(all_entities)}): {all_entities[:10]}...") # Mostra solo le prime 10

        all_relationships = domain_data_from_file.getAllRelationships() # Ottiene oggetti Relationship
        all_relationship_names = [r.getName() for r in all_relationships]
        print(f"Tutte le relazioni caricate ({len(all_relationship_names)}): {all_relationship_names[:10]}...") # Mostra solo le prime 10

        # Esempio: recupera gli attributi di un'entità specifica (sostituisci 'YourEntityName')
        entity_name_to_check = "YourEntityName" # <-- MODIFICA QUESTO
        entity_attributes = domain_data_from_file.properties(entity_name_to_check)
        if entity_attributes:
            print(f"Attributi per '{entity_name_to_check}': {[attr.getName() for attr in entity_attributes]}")
        else:
            print(f"Entità '{entity_name_to_check}' non trovata o senza attributi.")

    except Exception as e:
        print(f"Errore durante il caricamento del dominio '{domain_name}' da '{web_inf_folder}': {e}")
        traceback.print_exc()
else:
    if not web_inf_folder.exists() or not web_inf_folder.is_dir():
        print(f"Cartella WEB-INF non trovata in '{web_inf_folder}'.")
    elif not gbs_file_path.exists() or not gbs_file_path.is_file():
        print(f"File .gbs non trovato in '{gbs_file_path}'.")
    print("Assicurati che il percorso 'web_inf_folder' sia corretto e che il file specificato in 'gbs_file_name' esista al suo interno.")

print("\nScript completato.")