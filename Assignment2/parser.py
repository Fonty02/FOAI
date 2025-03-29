import pandas as pd
import re
import json

# Inizializzazione dei set
setOfItems = set()
setOfDocuments = set()
SetOfArtifacts = set()
setOfMaterialTypes = set()
setOfOrganizations = set()
setOfRelationships = set()
setOfPeople = set()
setOfContentDescriptions = set()

# Lettura del CSV
df = pd.read_csv('HCLEcatalog.csv')

with open("parsing.log", "w") as log_file:
    for index, row in df.iterrows():
        if pd.isna(row['IdNum']):
            log_file.write(f"Row {index} ERROR -> IdNum is null\n")
            continue
        id_num = row['IdNum']

        # Pulizia dei dati
        for col in row.index:
            if isinstance(row[col], str):
                row[col] = row[col].replace('"', '')
        
        data = {}
        person = {}
        organization = {}
        relationship = {}
        entityType = "Artifact"  # Default
        data['ontology'] = "general"
        
        # Estrazione campi per Document
        ToC = row['ToC']
        extent = row['Extent']
        serial_num = row['SerialNum']
        bib_cit = row['BibCit']
        
        # Controllo per Document
        if any([
            pd.notna(ToC) and ToC not in ["None", "NULL"],
            pd.notna(extent) and extent not in ["None", "NULL"],
            pd.notna(serial_num) and serial_num not in ["None", "NULL"],
            pd.notna(bib_cit) and bib_cit not in ["None", "NULL"]
        ]):
            if pd.notna(ToC) and ToC not in ["None", "NULL"]:
                data['ToC'] = ToC
            if pd.notna(extent) and extent not in ["None", "NULL"]:
                data['Extent'] = extent
            if pd.notna(serial_num) and serial_num not in ["None", "NULL"]:
                data['SerialNum'] = serial_num
            if pd.notna(bib_cit) and bib_cit not in ["None", "NULL"]:
                data['BibCit'] = bib_cit
            entityType = "Document"
        
        # Controllo per Item (se è ancora Artifact)
        if entityType == "Artifact":
            part_num = row['PartNum']
            if pd.notna(part_num) and part_num not in ["None", "NULL", ""] and not re.match(r'^\d$', str(part_num)):
                data['PartNum'] = part_num
                entityType = "Item"
        
        # Controllo Title obbligatorio
        title = row['Title']
        if pd.isna(title) or title in ["None", "NULL"]:
            log_file.write(f"Row {index} ERROR -> Title is null\n")
            continue
        else:
            log_file.write(f"Row {index} -> {entityType} -> parsed correctly\n")
            data['Title'] = title
            data['EntityType'] = entityType
        
        # Aggiunta campi comuni
        # SubjectTop
        subject_top = row['SubjectTop']
        if pd.notna(subject_top) and subject_top not in ["None", "NULL"]:
            setOfContentDescriptions.add(subject_top)
        
        # Material
        material = row['Material']
        if material in ["papr", "digi", "mix"]:
            material = "paper" if material == "papr" else "digital" if material == "digi" else "mix"
            setOfMaterialTypes.add(material)
        
        # Description
        description = row['Description']
        if pd.notna(description) and description not in ["None", "NULL"]:
            data['Description'] = description
        
        # DescComment
        desc_comp = row['DescComment']
        if pd.notna(desc_comp) and desc_comp not in ["None", "NULL"]:
            data['DescComment'] = desc_comp
        
        # WherMade
        wher_made = row['WherMade']
        if pd.notna(wher_made) and wher_made not in ["None", "NULL"]:
            data['WherMade'] = wher_made
        
        # Campi specifici per tipo entità
        if entityType == "Item":
            condition_nts = row['ConditionNts']
            if pd.notna(condition_nts) and condition_nts not in ["None", "NULL"]:
                data['ConditionNts'] = condition_nts
        
        if entityType == "Document":
            # Created
            created = row['Created']
            if pd.isna(created) or created in ["None", "NULL"]:
                created = row['DateCR']
            if pd.notna(created) and created not in ["None", "NULL"]:
                data['Created'] = created
            
            # Copyrighted
            copy_right = row['Copyrighted']
            if pd.notna(copy_right) and copy_right not in ["None", "NULL"]:
                if copy_right == "y":
                    copy_right = True
                elif copy_right == "n" or copy_right == "0":
                    copy_right = False
                data['Copyrighted'] = copy_right
        
        # Aggiunta ai set (FUORI DAI BLOCCHI CONDIZIONALI)
        if entityType == "Document":
            setOfDocuments.add(frozenset(data.items()))
        elif entityType == "Item":
            setOfItems.add(frozenset(data.items()))
        else:
            SetOfArtifacts.add(frozenset(data.items()))
        
        creatorPerson = False
        # Gestione Creator
        creator = row['Creator']
        if pd.notna(creator) and creator not in ["None", "NULL"]:
            if isinstance(creator, str) and re.match(r'^(Dr\.|Prof\.|Mr\.|Ms\.|Sir\s)?[A-Z][a-z]+\s[A-Z][a-z]+(\s[A-Z][a-z]+)?(,?\s(?:Jr\.|Sr\.|III))?$', creator):
                name_parts = re.sub(r'[^\w\s]', '', creator).split()
                person_data = {
                    'Name': name_parts[0],
                    'Surname': ' '.join(name_parts[1:]),
                    'ontology': "general"
                }
                setOfPeople.add(frozenset(person_data.items()))
                creatorPerson = True
            else:
                org_data = {
                    'name': str(creator),
                    'ontology': "general"
                }
                setOfOrganizations.add(frozenset(org_data.items()))
        
        # Relazione belongsTo
        rel_belongs = {
            'ontology': "general",
            'Type': "belongsTo",
            'Objects': 'HCLE',
            'ObjectType': entityType,
            'Subject': data['Title'],
            'SubjectType': 'Collection',
            'number': id_num
        }
        if entityType == "Item":
            rel_belongs['Subject'] += " " + data.get('PartNum', '')
        setOfRelationships.add(frozenset(rel_belongs.items()))
        
        # Relazione madeOf per Item
        if entityType == "Item" and material in setOfMaterialTypes:
            rel_madeOf = {
                'ontology': "general",
                'Type': "madeOf",
                'Subject': f"{data['Title']} {data.get('PartNum', '')}".strip(),
                'SubjectType': entityType,
                'Object': material,
                'ObjectType': "Material"
            }
            setOfRelationships.add(frozenset(rel_madeOf.items()))
        
        # Relazione describe per non-Item
        if entityType != "Item" and pd.notna(subject_top) and subject_top not in ["None", "NULL"]:
            rel_describe = {
                'ontology': "general",
                'Type': "describe",
                'Subject': subject_top,
                'SubjectType': "Category",
                'Object': data['Title'],
                'ObjectType': entityType
            }
            setOfRelationships.add(frozenset(rel_describe.items()))
        
        # Relazioni per creator (Person/Organization)
        if entityType != "Item":
            if creatorPerson:
                rel_developed = {
                    'ontology': "general",
                    'Type': "developed",
                    'Subject': f"{person_data['Name']} {person_data['Surname']}",
                    'SubjectType': "Person",
                    'Object': data['Title'],
                    'ObjectType': entityType
                }
                setOfRelationships.add(frozenset(rel_developed.items()))
            else:
                rel_produced = {
                    'ontology': "general",
                    'Type': "produced",
                    'Subject': org_data['name'],
                    'SubjectType': "Organization",
                    'Object': data['Title'],
                    'ObjectType': entityType
                }
                setOfRelationships.add(frozenset(rel_produced.items()))
        
        # Gestione Contributor e AddlAuth
        def process_contributor(contributor, rel_type):
            if pd.isna(contributor) or contributor in ["None", "NULL"]:
                return
            
            contributor_str = str(contributor)
            person_regex = r'^(Dr\.|Prof\.|Mr\.|Ms\.|Sir\s)?[A-Z][a-z]+(?:\s[A-Z][a-z]+)+(?:\s(?:Jr\.|Sr\.|III))?(?:[,;&]\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s(?:Jr\.|Sr\.|III))?)*$'
            
            if re.match(person_regex, contributor_str):
                people_list = re.split(r'\s*(?:,|;|\band\b|&)\s*', contributor_str)
                for person in people_list:
                    name_parts = [p for p in person.split() if p]
                    if len(name_parts) >= 2:
                        person_dict = {
                            'Name': name_parts[0],
                            'Surname': ' '.join(name_parts[1:]),
                            'ontology': "general"
                        }
                        setOfPeople.add(frozenset(person_dict.items()))
                        rel = {
                            'ontology': "general",
                            'Type': rel_type,
                            'Subject': f"{person_dict['Name']} {person_dict['Surname']}",
                            'SubjectType': "Person",
                            'Object': data['Title'],
                            'ObjectType': entityType
                        }
                        setOfRelationships.add(frozenset(rel.items()))
            else:
                org_dict = {
                    'name': contributor_str,
                    'ontology': "general"
                }
                setOfOrganizations.add(frozenset(org_dict.items()))
                rel = {
                    'ontology': "general",
                    'Type': rel_type.replace("developed", "produced"),
                    'Subject': org_dict['name'],
                    'SubjectType': "Organization",
                    'Object': data['Title'],
                    'ObjectType': entityType
                }
                setOfRelationships.add(frozenset(rel.items()))
        
        contributor = row['Contributor']
        process_contributor(contributor, "developed")
        
        add_author = row['AddlAuth']
        process_contributor(add_author, "collaborated")

# Generazione JSON
with open("data.json", "w") as json_file:
    json.dump({
        "Collection": {
            "name": "HCLE",
        },
        "Entities": {
            "Artifacts": [{"EntityType": "Artifact", **dict(artifact)} for artifact in SetOfArtifacts],
            "Items": [{"EntityType": "Item", **dict(item)} for item in setOfItems],
            "Documents": [{"EntityType": "Document", **dict(doc)} for doc in setOfDocuments],
            "People": [dict(person) for person in setOfPeople],
            "Organizations": [dict(org) for org in setOfOrganizations],
            "Categories": [{"name": cd} for cd in setOfContentDescriptions],
            "Materials": [{"name": mt} for mt in setOfMaterialTypes]
        },
        "Relationships": [
            dict(rel) for rel in setOfRelationships 
            if all(v is not None and v != "" for v in dict(rel).values())
        ]
    }, json_file, indent=4)