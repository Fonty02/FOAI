import os
import sys
from domain.DomainData import DomainData  # Assicurati che il path sia corretto

def main():
    gbs_file_path = "general.gbs"

    print(f"Attempting to load GBS file: {gbs_file_path}")

    if not os.path.exists(gbs_file_path) or not os.path.isfile(gbs_file_path):
        print(f"Error: GBS file not found or is not a valid file at path: {gbs_file_path}", file=sys.stderr)
        return

    try:
        # Usa DomainData per caricare il dominio
        domain_data = DomainData(gbs_file_path)

        # Estrai le informazioni tramite i metodi di DomainData
        domain_name = domain_data.domain
        imported_files = getattr(domain_data, "importedFiles", [])
        top_entities_count = len(domain_data.entityTree.getChildren()) if hasattr(domain_data.entityTree, "getChildren") else 0
        all_relationships_count = len(domain_data.getAllRelationships())
        n_rel_refs = getattr(domain_data, "nRelRefs", 0)
        axioms_count = len(domain_data.axioms) if hasattr(domain_data, "axioms") else 0

        print(f"Successfully loaded domain: {domain_name}")
        print(f"Imported files: {imported_files}")
        print(f"Total top-level entities: {top_entities_count}")
        print(f"Total relationships loaded (including nested): {all_relationships_count}")
        print(f"Total relationship references: {n_rel_refs}")
        print(f"Axioms loaded: {axioms_count}")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()