import os
import xml.etree.ElementTree as ET
from xml.dom import minidom # For pretty printing XML if needed
from pathlib import Path
import io
import codecs
from typing import List, Dict, Set, Optional, Tuple, Union, cast
from collections import defaultdict
import copy
import traceback

# Assuming domain classes are in the same directory or accessible via PYTHONPATH
from .Attribute import Attribute
from .Entity import Entity
from .Union import Union
from .Axiom import Axiom
from .Relationship import Relationship
from .Reference import Reference
from .TreeNode import TreeNode
from .DefaultTreeNode import DefaultTreeNode
# from .UType import UType # Assuming UType might be needed based on Java code

# Helper Pair class (can be replaced by tuple if preferred)
class Pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def getKey(self):
        return self.key

    def getValue(self):
        return self.value

class DomainData:
    """
    This class represents the domain data for a specific domain.
    It contains methods for loading and parsing .gbs files, as well as storing and manipulating domain information.
    The domain data includes entities, relationships, attributes, union_entities axioms, etc.
    """
    # private String author; # Not directly mapped, consider adding if needed
    # private int version; # Not directly mapped, consider adding if needed
    types: List[Attribute] # Changed from Vector<Attribute>
    importedFiles: List[str] # Changed from ArrayList<String>
    removedEntities: List[str] # Changed from ArrayList<String>
    removedRelationships: List[str] # Changed from ArrayList<String>
    domain: Optional[str]
    entityTree: Entity
    unions: Set[Union] # Changed from HashSet<Union>
    axioms: Set[Axiom] # Changed from HashSet<Axiom>
    relationshipTree: Relationship
    subjects: List[str] # Changed from Vector<String>
    objects: List[str] # Changed from Vector<String>
    subjRelObjs: Set[str] # Changed from TreeSet<String> - Note: Python set is unordered
    subjRels: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    subjObjs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    relSubjs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    relObjs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    objSubjs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    objRels: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    subjRel_Objs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    subjObj_Rels: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    relObj_Subjs: Dict[str, List[str]] # Changed from Map<String,Vector<String>>
    inverseRels: Dict[str, str] # Changed from Map<String,String>
    nRelRefs: int
    webInfFolder: str
    # Scaraggi attributes - added for completeness from Java end section
    domainList: Optional[List[str]] = None # Changed from ArrayList<String>
    inverse: Optional[str] = None
    attrsRel: Dict[str, List[Attribute]] # Changed from Map<String, Vector<Attribute>>

    def __init__(self, path: Optional[Union[str, bytes]] = None, webInfFolder: Optional[str] = None, domainName: Optional[str] = None, file: Optional[Union[str, Path]] = None):
        """
        Initializes the DomainData object. Can be called in several ways:
        1. DomainData(): Default constructor.
        2. DomainData(path="path/to/file.gbs"): Loads from a .gbs file path.
        3. DomainData(path="domain_name", webInfFolder="/path/to/webinf"): Loads domain_name.gbs from webInfFolder.
        4. DomainData(path=byte_array, webInfFolder="/path/to/webinf"): Loads from byte array.
        5. DomainData(domainName="domain_name", file="path/to/file.gbs"): Loads an arbitrary file with a given domain name.
        """
        # Default initializations
        self.types = []
        self.importedFiles = []
        self.removedEntities = []
        self.removedRelationships = []
        self.domain = None
        self.unions = set()
        self.axioms = set()
        self.subjects = []
        self.objects = []
        self.subjRelObjs = set()
        self.subjRels = defaultdict(list)
        self.subjObjs = defaultdict(list)
        self.relSubjs = defaultdict(list)
        self.relObjs = defaultdict(list)
        self.objSubjs = defaultdict(list)
        self.objRels = defaultdict(list)
        self.subjRel_Objs = defaultdict(list)
        self.subjObj_Rels = defaultdict(list)
        self.relObj_Subjs = defaultdict(list)
        self.inverseRels = {}
        self.nRelRefs = 0
        self.webInfFolder = webInfFolder if webInfFolder is not None else ""
        # Scaraggi attributes initialization
        self.domainList = None
        self.inverse = None
        self.attrsRel = defaultdict(list)


        # Initialize root Entity
        self.entityTree = Entity("Entity", None)
        entity_attributes = [
            Attribute(name="name", data_type="string", mandatory=True),
            Attribute(name="description", data_type="string", mandatory=False),
            Attribute(name="notes", data_type="string", mandatory=False)
        ]
        self.entityTree.addAttributes(entity_attributes) # Assuming addAttributes takes a list
        self.entityTree.setChildren([]) # Assuming setChildren takes a list

        # Initialize root Relationship
        # Assuming Relationship constructor matches: name, domain, inverse, parent, symmetric, attributes
        self.relationshipTree = Relationship(name="Relationship", domain=None, inverse="Relationship") # Simplified call
        self.relationshipTree.setChildrenRelationship([]) # Assuming setChildrenRelationship takes a list


        # Handle different constructor signatures
        try:
            if isinstance(path, bytes) and webInfFolder is not None:
                # Constructor(byte[] byteArray, String webInfFolder)
                self.webInfFolder = webInfFolder
                is_ = io.BytesIO(path)
                doc = self._parse_stream(is_)
                root_element = doc.getroot()
                self.domain = root_element.get("name")
                if self.domain is None:
                     raise ValueError("Root <domain> tag must have a 'name' attribute.")
                self._loadFile(doc, self.domain) # Use domain name as domainPath for consistency
            elif isinstance(path, str):
                 # Constructor(String path)
                if path.endswith(".gbs"):
                    file_path = Path(path)
                    doc = self._parseFile(file_path)
                    self._loadFile(doc, str(file_path))
                else:
                    # Assumes path is domain name and needs webInfFolder
                    if not self.webInfFolder:
                         raise ValueError("webInfFolder must be provided if path is not a full .gbs path")
                    file_path = Path(self.webInfFolder) / (path + ".gbs")
                    doc = self._parseFile(file_path)
                    self._loadFile(doc, str(file_path)) # Pass full path
            elif domainName is not None and file is not None:
                 # Constructor(String domainName, File file)
                self.domain = domainName # Set domain explicitly
                file_path = Path(file)
                doc = self._parseFile(file_path)
                self._loadFile(doc, str(file_path)) # Pass full path
            elif path is None and webInfFolder is None and domainName is None and file is None:
                # Default constructor case - initializations already done
                pass
            else:
                 raise TypeError("Invalid combination of arguments for DomainData constructor")

        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            raise
        except ET.ParseError as e:
            print(f"Error: XML parsing failed - {e}")
            raise
        except Exception as e:
            print(f"Error initializing DomainData: {e}")
            traceback.print_exc()
            raise

    def _parse_stream(self, stream: io.BytesIO) -> ET.ElementTree:
        """Parses an XML stream into an ElementTree."""
        try:
            tree = ET.parse(stream)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            raise

    def _parseFile(self, file_path: Path) -> ET.ElementTree:
        """Parses the given file path and returns an ElementTree object."""
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            tree = ET.parse(file_path)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error in file {file_path}: {e}")
            raise
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            raise

    def _getFolderPath(self, domainPath: str) -> Tuple[str, str]:
        """
        Retrieves the folder path and base filename for the given domain path.

        Args:
            domainPath: The domain path string (e.g., "path/to/domain.gbs" or "domain").

        Returns:
            A tuple containing (base_filename_without_extension, folder_path).
        """
        print(f"Getting folder path for: {domainPath}")
        path_obj = Path(domainPath)
        folder = str(path_obj.parent)
        base_name = path_obj.stem # Name without extension

        if folder == '.': # No directory part in the path
             folder = self.webInfFolder if self.webInfFolder else os.getcwd()
             # If domainPath didn't have .gbs, assume it's just the name
             if not domainPath.endswith(".gbs"):
                 base_name = domainPath

        print(f"  Base name: {base_name}, Folder: {folder}")
        return base_name, folder


    def _validateTag(self, tag: ET.Element, validTags: List[str]) -> None:
        """
        Validates a tag against a list of valid tags.
        Raises ValueError if the tag is not found in the list of valid tags.
        """
        if tag.tag not in validTags:
            parent_info = tag.getparent().tag if tag.getparent() is not None else "root"
            parent_name = tag.getparent().get("name", "") if tag.getparent() is not None else ""
            raise ValueError(
                f"Invalid tag <{tag.tag}> found under <{parent_info} {parent_name}> "
                f"where one of {validTags} was expected"
            )

    def _validateTagAttributes(self, tag: ET.Element, validTagAttributes: List[str], identifier: str) -> None:
        """
        Validates the attributes of a given XML tag against a list of valid attributes.
        Raises ValueError if any invalid attribute is found.
        """
        tag_id = tag.get(identifier, "")
        for attr_name in tag.attrib:
            if attr_name not in validTagAttributes:
                raise ValueError(
                    f"Invalid attribute \"{attr_name}\" found in <{tag.tag} {identifier}='{tag_id}'> "
                    f"where one of {validTagAttributes} was expected"
                )

    def _loadFile(self, doc: ET.ElementTree, domainPath: str) -> None:
        """
        Loads a file and parses its contents to populate the domain data.

        Args:
            doc: The ElementTree object representing the file to be loaded.
            domainPath: The path of the .gbs file or the domain name if loaded from bytes.
        """
        base_name, folder_path = self._getFolderPath(domainPath)
        webInf = Path(folder_path) # Use Path object for consistency

        root_element = doc.getroot()

        # Validate root tag is <domain>
        if root_element.tag != "domain":
             raise ValueError(f"Expected root tag <domain>, but found <{root_element.tag}> in {domainPath}")

        # Validate domain name attribute
        domain_name_attr = root_element.get("name")
        if domain_name_attr is None:
             raise ValueError(f"Root tag <domain> must have a 'name' attribute in {domainPath}")

        # Set domain if not already set (usually by the first loaded file)
        if self.domain is None:
            self.domain = domain_name_attr
        elif self.domain != domain_name_attr and domainPath not in self.importedFiles:
             # Allow different domain names in imported files, but maybe warn?
             print(f"Warning: Loading file with domain '{domain_name_attr}' into existing domain '{self.domain}' from {domainPath}")


        # Process child elements of <domain>
        allowed_sections = ["imports", "user-types", "entities", "union_entities", "relationships", "axioms"]
        processed_sections = {section: False for section in allowed_sections}
        
        current_section_index = 0
        children = list(root_element) # Get direct children

        # --- 1. Imports (Optional) ---
        if current_section_index < len(children) and children[current_section_index].tag == "imports":
            self._validateTag(children[current_section_index], ["imports"])
            self._parseImports(webInf, children[current_section_index])
            processed_sections["imports"] = True
            current_section_index += 1

        # --- 2. User Types (Optional) ---
        if current_section_index < len(children) and children[current_section_index].tag == "user-types":
             self._validateTag(children[current_section_index], ["user-types"])
             self._parseTypes(webInf, children[current_section_index])
             processed_sections["user-types"] = True
             current_section_index += 1

        # --- 3. Entities (Mandatory) ---
        if current_section_index >= len(children) or children[current_section_index].tag != "entities":
            raise ValueError(f"Missing mandatory <entities> section in domain '{self.domain}' file: {domainPath}")
        self._validateTag(children[current_section_index], ["entities"])
        self._parseEntities(children[current_section_index], self.entityTree, self.domain)
        processed_sections["entities"] = True
        current_section_index += 1

        # --- 4. Union Entities (Optional) ---
        if current_section_index < len(children) and children[current_section_index].tag == "union_entities":
             self._validateTag(children[current_section_index], ["union_entities"])
             self._parseUnionEntities(children[current_section_index], self.domain)
             processed_sections["union_entities"] = True
             current_section_index += 1

        # --- 5. Relationships (Mandatory) ---
        if current_section_index >= len(children) or children[current_section_index].tag != "relationships":
             raise ValueError(f"Missing mandatory <relationships> section in domain '{self.domain}' file: {domainPath}")
        self._validateTag(children[current_section_index], ["relationships"])
        self._parseRelationships(children[current_section_index], self.relationshipTree, self.domain)
        processed_sections["relationships"] = True
        current_section_index += 1

        # --- 6. Axioms (Optional) ---
        if current_section_index < len(children) and children[current_section_index].tag == "axioms":
             self._validateTag(children[current_section_index], ["axioms"])
             self._parseAxioms(children[current_section_index], self.domain)
             processed_sections["axioms"] = True
             current_section_index += 1

        # Check for unexpected tags
        if current_section_index < len(children):
            unexpected_tag = children[current_section_index].tag
            raise ValueError(f"Unexpected tag <{unexpected_tag}> found in <domain> tag in {domainPath}. Allowed order: {allowed_sections}")


        # Sort subjects and objects after loading
        self.subjects.sort()
        self.objects.sort()


    def _parseAxioms(self, axioms_tag: ET.Element, domainName: str) -> None:
        """
        Parses the axioms from the given XML node and adds them to the set of axioms.
        """
        valid_axiom_attrs = ["name", "formalism", "rule"] # Added 'rule' based on Java code
        for axiom_node in axioms_tag.findall("axiom"):
            self._validateTag(axiom_node, ["axiom"])
            self._validateTagAttributes(axiom_node, valid_axiom_attrs, "name")

            name = axiom_node.get("name")
            formalism = axiom_node.get("formalism")
            # expression = axiom_node.text.strip() if axiom_node.text else "" # Java used textContent
            expression = axiom_node.get("rule") # Java code seems to use 'rule' attribute

            if not name or not formalism or expression is None: # Check if expression is None explicitly
                 raise ValueError(f"Axiom tag requires 'name', 'formalism', and 'rule' attributes.")

            print(f"Parsing Axiom: {name} {formalism} {expression}")
            new_axiom = Axiom(name=name, formalism=formalism, expression=expression, domain=domainName)

            # Check for duplicates before adding
            if new_axiom in self.axioms:
                 # Allow merging if domain is different? Java logic suggests throwing error.
                 existing_axiom = next((a for a in self.axioms if a == new_axiom), None)
                 if existing_axiom and existing_axiom.getDomain() == domainName:
                      raise ValueError(f"Duplicate Axiom: \"{name}\" in domain \"{domainName}\"")
                 # else: update? For now, stick to Java's apparent behavior: error on same name.
            else:
                 self.axioms.add(new_axiom)


    def _parseUnionEntities(self, union_entities_tag: ET.Element, domainName: str) -> None:
        """
        Parses the union entities from the given XML node and adds them to the domain's set of Union entities.
        """
        unions_to_add: List[Union] = []
        valid_union_attrs = ["name"]
        valid_uvalue_attrs = ["name"]

        for union_node in union_entities_tag.findall("union"):
            self._validateTag(union_node, ["union"])
            self._validateTagAttributes(union_node, valid_union_attrs, "name")

            union_name = union_node.get("name")
            if not union_name:
                raise ValueError("<union> tag requires a 'name' attribute.")

            # Check if an entity with the same name already exists
            if self.findInTree(self.entityTree, union_name) is not None:
                raise ValueError(f"Entity \"{union_name}\" already exists, can't create union entity with the same name.")

            # Read uvalues
            uvalues: Set[str] = set()
            for uvalue_node in union_node.findall("uvalue"):
                 self._validateTag(uvalue_node, ["uvalue"])
                 self._validateTagAttributes(uvalue_node, valid_uvalue_attrs, "name")
                 uvalue_name = uvalue_node.get("name")
                 if not uvalue_name:
                      raise ValueError("<uvalue> tag requires a 'name' attribute.")
                 uvalues.add(uvalue_name)

            new_union = Union(name=union_name, domain=domainName, values=uvalues)
            unions_to_add.append(new_union)

        self._addUnions(unions_to_add)

    def _addUnions(self, _unions: List[Union]) -> None:
        """
        Adds a list of Union objects to the domain, checking for duplicates and valid entity references.
        """
        # Check that all uvalues are existing entities
        for union_obj in _unions:
            for entity_name in union_obj.getValues():
                if self.findInTree(self.entityTree, entity_name) is None:
                    raise ValueError(f"Entity \"{entity_name}\" required by union \"{union_obj.getName()}\" does not exist.")

        # Add or merge unions
        for new_union in _unions:
            # Check if a union with the same name already exists
            existing_union = next((u for u in self.unions if u.getName() == new_union.getName()), None)

            if existing_union:
                 # Java logic: Error if same domain, merge if different domain
                 if existing_union.getDomain() == new_union.getDomain():
                      # This might happen if the same file is imported multiple times or defines the same union
                      print(f"Warning: Duplicate Union definition found: \"{new_union.getName()}\" in domain \"{new_union.getDomain()}\". Merging values.")
                      # Merge values instead of raising error, seems more robust
                      existing_union.getValues().update(new_union.getValues())
                      # Update domain if the new one is different (e.g., from a direct load vs import)
                      if existing_union.getDomain() != new_union.getDomain():
                           existing_union.setDomain(new_union.getDomain())

                 else:
                      # Different domains, merge values and update domain (potentially overwriting)
                      print(f"Merging union '{new_union.getName()}' from domain '{new_union.getDomain()}' into existing from '{existing_union.getDomain()}'")
                      existing_union.setDomain(new_union.getDomain()) # Overwrite domain? Or keep original? Let's overwrite for now.
                      existing_union.getValues().update(new_union.getValues())
            else:
                 # Union is new, just add it
                 self.unions.add(new_union)


    def addEntity(self, entity: Entity) -> None:
        """Adds a top-level entity to the domain, replacing any existing top-level entity with the same name."""
        if not isinstance(entity, Entity):
            raise TypeError("Can only add Entity objects")

        # Check if a top-level entity with the same name exists
        existing_entity = next((e for e in self.entityTree.getChildren() if e.getName() == entity.getName()), None)

        if existing_entity:
            print(f"Warning: Replacing existing top-level entity '{entity.getName()}'")
            self.entityTree.getChildren().remove(existing_entity) # Assumes getChildren returns a mutable list
            existing_entity.setParent(None) # Detach old entity

        self.entityTree.addChild(entity) # addChild should handle setting the parent internally


    def addRelationship(self, relationship: Relationship) -> None:
        """Adds a top-level relationship to the domain, replacing any existing top-level relationship with the same name."""
        if not isinstance(relationship, Relationship):
            raise TypeError("Can only add Relationship objects")

        # Check if a top-level relationship with the same name exists
        existing_rel = next((r for r in self.getTopRelationships() if r.getName() == relationship.getName()), None)

        if existing_rel:
            print(f"Warning: Replacing existing top-level relationship '{relationship.getName()}'")
            # Need to remove from the relationshipTree's children
            children = self.relationshipTree.getChildren() # Assuming this returns List[Entity]
            if existing_rel in children:
                 children.remove(existing_rel)
                 existing_rel.setParent(None) # Detach old relationship
            else:
                 print(f"Error: Could not find existing relationship '{existing_rel.getName()}' in relationshipTree children during replacement.")


        self.relationshipTree.addChildrenRelationship(relationship) # Assuming this adds and sets parent


    def _parseRelationships(self, parentNode: ET.Element, root: Relationship, domainName: str) -> None:
        """
        Recursively constructs the relationships tree by parsing relationships and their attributes, references, and sub-relationships.
        """
        valid_rel_attrs = ["name", "inverse", "description", "abstract", "notes"] # Added notes
        # Determine allowed children based on whether we are at the top <relationships> or inside a <relationship>
        allowed_children = ["relationship"] if root == self.relationshipTree else ["relationship", "attribute", "reference"]

        for child_node in parentNode: # Iterate through direct children
             # Skip comments and processing instructions
             if not isinstance(child_node.tag, str):
                  continue

             self._validateTag(child_node, allowed_children)

             if child_node.tag == "relationship":
                  self._validateTagAttributes(child_node, valid_rel_attrs, "name")

                  rel_name = child_node.get("name")
                  rel_inverse = child_node.get("inverse")
                  description = child_node.get("description")
                  notes = child_node.get("notes") # Get notes attribute
                  is_abstract_str = child_node.get("abstract", "false") # Default to false if missing
                  is_abstract = is_abstract_str.lower() == "true"

                  if not rel_name or not rel_inverse:
                       raise ValueError("<relationship> tag requires 'name' and 'inverse' attributes.")

                  # Find existing relationship anywhere in the tree first
                  existing_relationship = self.findInTree(self.relationshipTree, rel_name)
                  current_relationship: Optional[Relationship] = None

                  if existing_relationship and isinstance(existing_relationship, Relationship):
                       # Relationship already exists somewhere
                       existing_parent = existing_relationship.getParent()
                       # Check if the found relationship's parent is an ancestor of the current root OR if the parent is the absolute root
                       # AND if the domain is different (indicating it came from an import)
                       is_ancestor = root.hasAncestor(existing_parent.getName()) if existing_parent else False
                       is_different_domain = existing_relationship.getDomain() != domainName

                       if (is_ancestor or existing_parent == self.relationshipTree) and is_different_domain:
                            print(f"Detaching and moving relationship '{rel_name}' from '{existing_parent.getName() if existing_parent else 'root'}' (domain: {existing_relationship.getDomain()}) to '{root.getName()}' (domain: {domainName})")
                            existing_relationship.detach() # Remove from old parent
                            root.addChildrenRelationship(existing_relationship) # Add to new parent (sets parent)
                            current_relationship = existing_relationship
                       elif existing_parent == root:
                            # Already in the correct place, just update properties
                            print(f"Updating existing relationship '{rel_name}' under parent '{root.getName()}'")
                            current_relationship = existing_relationship
                       else:
                            # Inconsistency: Found elsewhere but not in a compatible import/parent situation
                            raise ValueError(f"Inconsistency: Relationship '{rel_name}' found under unexpected parent '{existing_parent.getName() if existing_parent else 'root'}'. Cannot automatically move to '{root.getName()}'.")
                  else:
                       # Relationship is new, create it
                       print(f"Creating new relationship '{rel_name}' under parent '{root.getName()}'")
                       # Assuming constructor: name, domain, inverse, parent=None, symmetric=False, attributes=None
                       current_relationship = Relationship(name=rel_name, domain=domainName, inverse=rel_inverse)
                       root.addChildrenRelationship(current_relationship) # Adds to children and sets parent

                  # Update properties of the (potentially existing or new) relationship
                  if current_relationship:
                       current_relationship.setDomain(domainName) # Overwrite domain? Or append? Let's overwrite.
                       current_relationship.setDescription(description or "") # Use empty string if None
                       current_relationship.setAbstract(is_abstract)
                       current_relationship.setNotes(notes or "") # Use empty string if None

                       # Add attributes defined directly within this <relationship> tag
                       # Assuming readAttributes handles potential CloneNotSupportedException internally or Attribute.clone exists
                       direct_attributes = self._readAttributes(child_node)
                       current_relationship.addAttributes(direct_attributes) # Add new attributes

                       # Parse references defined directly within this <relationship> tag
                       self._parseReferences(child_node, current_relationship)

                       # Recursively parse sub-relationships
                       self._parseRelationships(child_node, current_relationship, domainName)
                  else:
                       # This case should ideally not happen if logic above is correct
                       print(f"Error: Failed to get or create relationship '{rel_name}'")


             elif child_node.tag == "attribute":
                  # Attributes are handled within the 'relationship' block using _readAttributes
                  pass
             elif child_node.tag == "reference":
                  # References are handled within the 'relationship' block using _parseReferences
                  pass


    def _parseReferences(self, parentNode: ET.Element, relation: Relationship) -> None:
        """
        Parses the references from the given parent node (<relationship>) and adds them to the specified relationship.
        """
        relation_name = relation.getName()
        valid_ref_attrs = ["subject", "object"]

        for ref_node in parentNode.findall("reference"):
             # No need to validate tag again, already filtered by findall
             # self._validateTag(ref_node, ["reference"]) # Redundant
             self._validateTagAttributes(ref_node, valid_ref_attrs, "") # No specific identifier needed

             subject = ref_node.get("subject")
             object_ref = ref_node.get("object") # Renamed variable to avoid conflict with keyword

             if not subject or not object_ref:
                  raise ValueError("<reference> tag requires 'subject' and 'object' attributes.")

             # Add subject/object to global lists if not present
             if subject not in self.subjects:
                  self.subjects.append(subject)
                  # self.subjects.sort() # Sort later after all loading is done

             if object_ref not in self.objects:
                  self.objects.append(object_ref)
                  # self.objects.sort() # Sort later

             # Create Reference object
             # Assuming Reference constructor: subject, object, attributes=None
             ref = Reference(subject=subject, object=object_ref)

             # Read attributes specific to this reference
             ref_attributes = self._readAttributes(ref_node) # Attributes can be children of <reference>
             if ref_attributes:
                  ref.setAttributes(ref_attributes) # Assuming setAttributes takes a list

             # Add reference to the relationship
             relation.addReference(ref) # Assuming addReference handles internal storage

             # Update helper dictionaries and sets
             self.nRelRefs += 1
             subj_rel_obj_str = f"{subject}.{relation_name}.{object_ref}"
             self.subjRelObjs.add(subj_rel_obj_str)

             self._addValue(self.subjRels, subject, relation_name)
             self._addValue(self.subjObjs, subject, object_ref)
             self._addValue(self.relSubjs, relation_name, subject)
             self._addValue(self.relObjs, relation_name, object_ref)
             self._addValue(self.objRels, object_ref, relation_name)
             self._addValue(self.objSubjs, object_ref, subject)
             self._addValue(self.subjRel_Objs, f"{subject}.{relation_name}", object_ref)
             self._addValue(self.subjObj_Rels, f"{subject}.{object_ref}", relation_name)
             self._addValue(self.relObj_Subjs, f"{relation_name}.{object_ref}", subject)


    def _parseEntities(self, parentNode: ET.Element, root: Entity, domainName: str) -> None:
        """
        Recursively parses entities from the given parent node and adds them to the entity tree.
        """
        valid_entity_attrs = ["name", "description", "abstract", "notes"]
        # Determine allowed children based on whether we are at the top <entities> or inside an <entity>
        allowed_children = ["entity"] if root == self.entityTree else ["entity", "attribute"]

        for child_node in parentNode: # Iterate through direct children
             # Skip comments and processing instructions
             if not isinstance(child_node.tag, str):
                  continue

             self._validateTag(child_node, allowed_children)

             if child_node.tag == "entity":
                  self._validateTagAttributes(child_node, valid_entity_attrs, "name")

                  entity_name = child_node.get("name")
                  description = child_node.get("description")
                  notes = child_node.get("notes")
                  is_abstract_str = child_node.get("abstract", "false")
                  is_abstract = is_abstract_str.lower() == "true"

                  if not entity_name:
                       raise ValueError("<entity> tag requires a 'name' attribute.")

                  # Find existing entity anywhere in the tree first
                  existing_entity = self.findInTree(self.entityTree, entity_name)
                  current_entity: Optional[Entity] = None

                  if existing_entity:
                       # Entity already exists somewhere
                       existing_parent = existing_entity.getParent()
                       is_ancestor = root.hasAncestor(existing_parent.getName()) if existing_parent else False
                       is_different_domain = existing_entity.getDomain() != domainName

                       if (is_ancestor or existing_parent == self.entityTree) and is_different_domain:
                            print(f"Detaching and moving entity '{entity_name}' from '{existing_parent.getName() if existing_parent else 'root'}' (domain: {existing_entity.getDomain()}) to '{root.getName()}' (domain: {domainName})")
                            existing_entity.detach()
                            root.addChild(existing_entity) # Add to new parent
                            current_entity = existing_entity
                       elif existing_parent == root:
                            print(f"Updating existing entity '{entity_name}' under parent '{root.getName()}'")
                            current_entity = existing_entity
                       else:
                            raise ValueError(f"Inconsistency: Entity '{entity_name}' found under unexpected parent '{existing_parent.getName() if existing_parent else 'root'}'. Cannot automatically move to '{root.getName()}'.")
                  else:
                       # Entity is new, create it
                       print(f"Creating new entity '{entity_name}' under parent '{root.getName()}'")
                       current_entity = Entity(name=entity_name, domain=domainName)
                       root.addChild(current_entity) # Adds to children and sets parent

                  # Update properties
                  if current_entity:
                       current_entity.setDomain(domainName) # Overwrite domain
                       current_entity.setDescription(description or "")
                       current_entity.setAbstract(is_abstract)
                       current_entity.setNotes(notes or "")

                       # Add attributes defined directly within this <entity> tag
                       direct_attributes = self._readAttributes(child_node)
                       current_entity.addAttributes(direct_attributes)

                       # Recursively parse sub-entities
                       self._parseEntities(child_node, current_entity, domainName)
                  else:
                       print(f"Error: Failed to get or create entity '{entity_name}'")

             elif child_node.tag == "attribute":
                  # Attributes are handled within the 'entity' block using _readAttributes
                  pass


    def _parseImports(self, folder: Path, importsNode: ET.Element) -> None:
        """
        Parses the imports from the <imports> tag, loads imported files recursively (DFS),
        and handles the <deleted> section.
        """
        valid_import_children = ["import", "deleted"]
        valid_import_attrs = ["schema"]
        valid_deleted_children = ["entity", "relationship"]
        valid_deleted_item_attrs = ["name"]

        children = list(importsNode)
        import_nodes: List[ET.Element] = []
        deleted_node: Optional[ET.Element] = None

        # Separate import and deleted nodes, validate structure
        for i, child in enumerate(children):
             if not isinstance(child.tag, str): continue # Skip comments/PIs
             self._validateTag(child, valid_import_children)
             if child.tag == "import":
                  if deleted_node is not None:
                       raise ValueError("<import> tag cannot appear after <deleted> tag within <imports>.")
                  self._validateTagAttributes(child, valid_import_attrs, "schema")
                  import_nodes.append(child)
             elif child.tag == "deleted":
                  if deleted_node is not None:
                       raise ValueError("Only one <deleted> tag is allowed within <imports>.")
                  if i != len(children) - 1:
                       raise ValueError("<deleted> tag must be the last child of <imports>.")
                  # No attributes expected on <deleted> itself
                  self._validateTagAttributes(child, [], "")
                  deleted_node = child

        # Process imports first (DFS)
        for import_node in import_nodes:
            schema_path_str = import_node.get("schema")
            if not schema_path_str:
                 raise ValueError("<import> tag requires a 'schema' attribute.")

            # Avoid reloading files already processed in this load cycle
            # Use absolute path for reliable checking
            is_absolute = Path(schema_path_str).is_absolute() or "/" in schema_path_str or "\\" in schema_path_str # Basic check
            
            if is_absolute:
                 import_file_path = Path(schema_path_str)
                 # Ensure .gbs extension if not present? Or assume it's correct? Let's assume correct for now.
                 if not import_file_path.suffix == ".gbs":
                      print(f"Warning: Imported schema path '{schema_path_str}' does not end with .gbs")
            else:
                 # Relative path (likely just domain name), resolve against the folder of the *current* file
                 import_file_path = folder / (schema_path_str + ".gbs")

            abs_import_path_str = str(import_file_path.resolve())

            if abs_import_path_str not in self.importedFiles:
                 print(f"Importing: {abs_import_path_str}")
                 self.importedFiles.append(abs_import_path_str)
                 try:
                      imported_doc = self._parseFile(import_file_path)
                      # Recursively load the imported file
                      self._loadFile(imported_doc, abs_import_path_str)
                 except FileNotFoundError:
                      print(f"Error: Imported file not found: {import_file_path}")
                      raise # Re-raise to stop the loading process
                 except Exception as e:
                      print(f"Error loading imported file {import_file_path}: {e}")
                      raise # Re-raise
            else:
                 print(f"Skipping already imported file: {abs_import_path_str}")


        # Process deleted items after all imports are done
        if deleted_node is not None:
            for deleted_item in deleted_node:
                 if not isinstance(deleted_item.tag, str): continue
                 self._validateTag(deleted_item, valid_deleted_children)
                 self._validateTagAttributes(deleted_item, valid_deleted_item_attrs, "name")

                 item_type = deleted_item.tag
                 item_name = deleted_item.get("name")
                 if not item_name:
                      raise ValueError(f"<{item_type}> tag within <deleted> requires a 'name' attribute.")

                 print(f"Processing deletion: Type='{item_type}', Name='{item_name}'")
                 if item_type == "entity":
                      self.removeEntity(item_name) # Remove from tree
                      if item_name not in self.removedEntities:
                           self.removedEntities.append(item_name) # Track removal
                 elif item_type == "relationship":
                      self.removeRelationship(item_name) # Remove from tree
                      if item_name not in self.removedRelationships:
                           self.removedRelationships.append(item_name) # Track removal


    def _parseTypes(self, webInf: Path, typesNode: ET.Element) -> None:
        """Parses the <user-types> section."""
        try:
            # readAttributes expects a parent node containing <attribute> children
            # <user-types> itself contains <attribute> children directly
            attributes_read = self._readAttributes(typesNode)
            self.types = self._fromAttributesToTypes(attributes_read)
            print(f"Parsed {len(self.types)} user types.")
        except Exception as e: # Catch potential CloneNotSupportedException if Attribute.clone fails
            print(f"Error parsing user types: {e}")
            traceback.print_exc()


    def _fromAttributesToTypes(self, attributes: List[Attribute]) -> List[Attribute]:
        """Converts a list of attributes into a list of types (potentially UType instances)."""
        # In Python, if UType is just a marker or has no extra logic,
        # we might just use the Attribute objects directly.
        # If UType has specific behavior, we'd instantiate UType here.
        # For now, assume Attribute is sufficient as the 'type' definition.
        # The Java code casts to UType but doesn't seem to use specific UType methods immediately.
        # Let's return the list of Attributes as is.
        # If UType becomes necessary:
        # return [UType.from_attribute(a) for a in attributes] # Assuming a UType factory method
        return attributes


    def _substitute(self, fileToModify: Path, entityToRemove: str, entityToAddNode: ET.Element) -> None:
        """
        Substitutes an entity in the specified XML file with a new entity definition.
        NOTE: This directly modifies the file on disk. Use with caution.
        This method is complex and less common in Python XML handling compared to in-memory manipulation.
        Consider if this file modification logic is truly needed or if in-memory updates suffice.
        """
        print(f"Attempting to substitute entity '{entityToRemove}' in file: {fileToModify}")
        try:
            tree = self._parseFile(fileToModify)
            root = tree.getroot()
            parent_map = {c: p for p in root.iter() for c in p} # Create parent map for removal

            entity_to_replace_node: Optional[ET.Element] = None
            parent_of_entity_to_replace: Optional[ET.Element] = None

            # Find the entity node to remove (search within <entities> or nested <entity>)
            entities_section = root.find("entities")
            if entities_section is None:
                 print(f"Warning: No <entities> section found in {fileToModify} for substitution.")
                 return # Or raise error?

            queue = list(entities_section) # Start search from children of <entities>
            visited = set()
            found_node = None

            while queue:
                 current_node = queue.pop(0)
                 if current_node in visited: continue
                 visited.add(current_node)

                 if current_node.tag == 'entity' and current_node.get('name') == entityToRemove:
                      found_node = current_node
                      break
                 # Add children to queue for deeper search
                 queue.extend(list(current_node))

            if found_node is None:
                 print(f"Entity '{entityToRemove}' not found in {fileToModify} for substitution.")
                 return

            entity_to_replace_node = found_node
            parent_of_entity_to_replace = parent_map.get(entity_to_replace_node)

            if parent_of_entity_to_replace is None:
                 print(f"Error: Could not find parent for entity '{entityToRemove}' during substitution.")
                 return # Should not happen if found within <entities>

            # Create a deep copy of the node to add (important if it comes from another tree)
            # ET doesn't have a direct deep copy for elements across trees easily.
            # A common way is to serialize and re-parse, or manually reconstruct.
            # Let's try manual reconstruction (simplified)
            # new_entity_node = ET.Element(entityToAddNode.tag, entityToAddNode.attrib)
            # new_entity_node.text = entityToAddNode.text
            # new_entity_node.tail = entityToAddNode.tail
            # # Recursively copy children (this needs a proper deep copy function)
            # # For simplicity, assume entityToAddNode is simple or use a library like lxml if complex copy needed
            # # THIS IS A PLACEHOLDER - A robust clone is needed here.
            # # Using copy.deepcopy might work if the element isn't tied to a specific tree yet.
            try:
                 new_entity_node = copy.deepcopy(entityToAddNode)
            except TypeError:
                 print("Error: Could not deep copy the entity node to add. Substitution failed.")
                 return


            # Find index of old node to insert new one in same position
            try:
                 index = list(parent_of_entity_to_replace).index(entity_to_replace_node)
                 parent_of_entity_to_replace.remove(entity_to_replace_node)
                 parent_of_entity_to_replace.insert(index, new_entity_node)
                 print(f"Successfully substituted '{entityToRemove}' in {fileToModify}")
            except ValueError:
                 print(f"Error: Node '{entityToRemove}' not found in its supposed parent during substitution.")
                 # Fallback: just append if index fails?
                 parent_of_entity_to_replace.remove(entity_to_replace_node)
                 parent_of_entity_to_replace.append(new_entity_node)


            # Save the modified XML
            self._saveXML(tree, fileToModify)

        except Exception as e:
            print(f"Error during entity substitution in {fileToModify}: {e}")
            traceback.print_exc()


    def _saveXML(self, doc: ET.ElementTree, fileToSave: Path) -> None:
        """Saves the ElementTree document to the specified file path."""
        try:
            # ET.indent(doc.getroot()) # Pretty print (Available in Python 3.9+)
            doc.write(fileToSave, encoding='utf-8', xml_declaration=True)
            print(f"Saved XML changes to: {fileToSave}")
        except Exception as e:
            print(f"Error saving XML to {fileToSave}: {e}")
            traceback.print_exc()
            raise # Re-raise


    def _clone(self, docToModify: ET.ElementTree, nodeToClone: ET.Element) -> ET.Element:
         """
         Clones an XML element, intended for use within the same document or for substitution.
         NOTE: This is a simplified clone. For complex scenarios, especially across different
         ElementTree instances, a more robust deep copy mechanism (like serialization/deserialization
         or manual recursive copying) might be needed. `copy.deepcopy` often works well.
         """
         try:
              # Using copy.deepcopy is generally the most Pythonic way for element cloning
              cloned_node = copy.deepcopy(nodeToClone)
              return cloned_node
         except Exception as e:
              print(f"Error cloning node <{nodeToClone.tag}>: {e}")
              # Fallback or raise error
              # Manual clone (basic example):
              # cloned = ET.Element(nodeToClone.tag, nodeToClone.attrib)
              # cloned.text = nodeToClone.text
              # cloned.tail = nodeToClone.tail
              # for child in nodeToClone:
              #     cloned.append(self._clone(docToModify, child)) # Recursive call
              # return cloned
              raise # Re-raise the error for now


    def _cloneAttributes(self, docToModify: ET.ElementTree, attributesNode: ET.Element) -> ET.Element:
        """Clones an <attributes> element and its children."""
        # Since _clone uses deepcopy, this might be redundant if _clone is called on the parent.
        # However, if called directly on an <attributes> node:
        return self._clone(docToModify, attributesNode)


    def _cloneValues(self, docToModify: ET.ElementTree, valuesNode: ET.Element) -> ET.Element:
        """Clones a <values> or <taxonomy> element and its children recursively."""
        # Using deepcopy via _clone should handle the recursion correctly.
        return self._clone(docToModify, valuesNode)


    def getTopEntities(self) -> List[Entity]:
        """Returns a list of the top-level entities (direct children of the root Entity)."""
        # Ensure entityTree and its children handling are correct
        if self.entityTree:
             # Assuming getChildren returns the list of direct children
             return self.entityTree.getChildren()
        return []

    def getTopRelationships(self) -> List[Relationship]:
        """Returns a list of top-level relationships (direct children of the root Relationship)."""
        if self.relationshipTree:
             # Assuming getChildren returns List[Entity], need to cast/filter
             children = self.relationshipTree.getChildren()
             # Use cast for type hinting, or filter with isinstance
             # return [cast(Relationship, r) for r in children if isinstance(r, Relationship)]
             # Or rely on Relationship.getChildrenRelationships if it exists and returns List[Relationship]
             # Let's assume getChildren returns entities and we filter/cast
             top_rels = [child for child in children if isinstance(child, Relationship)]
             return cast(List[Relationship], top_rels) # Cast the filtered list
        return []

    def getTopRelationshipsToString(self) -> List[str]:
        """Returns a list of names of the top-level relationships."""
        return [r.getName() for r in self.getTopRelationships()]

    @staticmethod
    def toRelationships(entities: List[Entity]) -> List[Relationship]:
        """Converts a list of Entity objects to a list of Relationship objects by casting."""
        # This assumes all entities in the list are actually Relationships.
        # Add type checking for safety.
        rels = []
        for e in entities:
            if isinstance(e, Relationship):
                rels.append(e)
            else:
                print(f"Warning: Entity '{e.getName()}' is not a Relationship in toRelationships.")
        # return cast(List[Relationship], entities) # Original direct cast - less safe
        return rels


    def getEntityTree(self) -> Entity:
        """Returns the root of the entity tree."""
        return self.entityTree

    def getRelationshipTree(self) -> Relationship:
        """Returns the root of the relationship tree."""
        return self.relationshipTree

    def getRemovedEntities(self) -> List[str]:
        """Returns the list of entity names marked for removal via <deleted> tag."""
        return self.removedEntities

    def getRemovedRelationships(self) -> List[str]:
        """Returns the list of relationship names marked for removal via <deleted> tag."""
        return self.removedRelationships

    def properties(self, entity_name: str) -> List[Attribute]:
        """Retrieves all attributes (including inherited) for a given entity name."""
        entity = self.getEntity(entity_name)
        if entity:
            # Assuming Entity class has a method like getAllAttributes() that handles inheritance
            return entity.getAllAttributes()
        return []

    def propertiesRelation(self, relation_name: str) -> List[Attribute]:
        """Retrieves all attributes (including inherited) for a given relationship name."""
        relationship = self.getRelationship(relation_name)
        if relationship:
            # Assuming Relationship (as an Entity) has getAllAttributes()
            return relationship.getAllAttributes()
        return []

    # _propertiesCommon is likely implemented within Entity.getAllAttributes in Python version
    # def _propertiesCommon(self, e: Optional[Entity]) -> List[Attribute]: ...

    @staticmethod
    def relationName(subject: str, relationship: str, object_ref: str) -> str:
        """Generates a standard relationship name string."""
        return f"{subject}.{relationship}.{object_ref}"

    def removeEntity(self, name: str) -> None:
        """Removes an entity by name from the entity tree."""
        entity_to_remove = self.findInTree(self.entityTree, name)
        if entity_to_remove:
            print(f"Removing entity: {name}")
            entity_to_remove.detach() # Detach from parent
            # TODO: Need to handle removal of references involving this entity in relationships.
            # This requires iterating through all relationships and their references.
            self._removeReferencesInvolving(name)
        else:
            print(f"Entity '{name}' not found for removal.")


    def removeRelationship(self, name: str) -> None:
        """Removes a relationship by name from the relationship tree."""
        rel_to_remove = self.findInTree(self.relationshipTree, name)
        if rel_to_remove and isinstance(rel_to_remove, Relationship):
            print(f"Removing relationship: {name}")
            rel_to_remove.detach() # Detach from parent
            # Also remove associated entries from helper dicts/sets
            self._cleanupRelationshipData(name)
        else:
            print(f"Relationship '{name}' not found for removal.")

    def _removeReferencesInvolving(self, entity_name: str) -> None:
        """Internal helper to remove relationship references involving a deleted entity."""
        print(f"Removing references involving entity: {entity_name}")
        all_rels = self.getAllRelationships()
        refs_to_remove_map: Dict[Relationship, List[Reference]] = defaultdict(list)
        rels_to_potentially_remove: Set[Relationship] = set()

        for rel in all_rels:
            for ref in rel.getReferences(): # Assuming getReferences exists
                if ref.getSubject() == entity_name or ref.getObject() == entity_name:
                    refs_to_remove_map[rel].append(ref)
                    # Clean up helper dicts immediately for this specific reference
                    self._cleanupReferenceData(ref.getSubject(), rel.getName(), ref.getObject())


            # Remove the collected references from the relationship
            if rel in refs_to_remove_map:
                 # Assuming Relationship has a method like removeReferences or similar
                 # rel.removeAll(refs_to_remove_map[rel]) # Java method name
                 # Python equivalent might be:
                 current_refs = rel.getReferences()
                 updated_refs = [r for r in current_refs if r not in refs_to_remove_map[rel]]
                 rel.setReferences(updated_refs) # Assuming setReferences exists

                 # Check if relationship becomes empty (optional, Java code did this)
                 # if not rel.getReferences():
                 #     rels_to_potentially_remove.add(rel)

        # Optionally remove relationships that became empty
        # for rel_to_remove in rels_to_potentially_remove:
        #     print(f"Relationship '{rel_to_remove.getName()}' became empty after entity removal, removing it.")
        #     self.removeRelationship(rel_to_remove.getName())


    def _cleanupRelationshipData(self, rel_name: str) -> None:
        """Internal helper to remove data associated with a deleted relationship."""
        print(f"Cleaning up data for removed relationship: {rel_name}")
        # Remove from inverse mapping
        inverse_name = self.inverseRels.pop(rel_name, None)
        if inverse_name:
            self.inverseRels.pop(inverse_name, None)

        # Remove entries where rel_name is the key
        self.relSubjs.pop(rel_name, None)
        self.relObjs.pop(rel_name, None)

        # Remove entries from other maps where rel_name is involved
        keys_to_remove = [key for key in self.subjRels if rel_name in self.subjRels[key]]
        for key in keys_to_remove: self._removeValue(self.subjRels, key, rel_name)

        keys_to_remove = [key for key in self.objRels if rel_name in self.objRels[key]]
        for key in keys_to_remove: self._removeValue(self.objRels, key, rel_name)

        keys_to_remove = [key for key in self.subjRel_Objs if key.endswith(f".{rel_name}")]
        for key in keys_to_remove: self.subjRel_Objs.pop(key, None)

        keys_to_remove = [key for key in self.subjObj_Rels if rel_name in self.subjObj_Rels[key]]
        for key in keys_to_remove: self._removeValue(self.subjObj_Rels, key, rel_name)

        keys_to_remove = [key for key in self.relObj_Subjs if key.startswith(f"{rel_name}.")]
        for key in keys_to_remove: self.relObj_Subjs.pop(key, None)

        # Remove from subjRelObjs set
        self.subjRelObjs = {sro for sro in self.subjRelObjs if f".{rel_name}." not in sro}
        # Note: nRelRefs should be decremented when references are removed, handled in _cleanupReferenceData


    def _cleanupReferenceData(self, subject: str, rel_name: str, object_ref: str) -> None:
        """Internal helper to remove data for a specific deleted reference."""
        subj_rel_obj_str = f"{subject}.{rel_name}.{object_ref}"
        subj_rel_key = f"{subject}.{rel_name}"
        subj_obj_key = f"{subject}.{object_ref}"
        rel_obj_key = f"{rel_name}.{object_ref}"

        if subj_rel_obj_str in self.subjRelObjs:
             self.subjRelObjs.remove(subj_rel_obj_str)
             self.nRelRefs -= 1 # Decrement count only if successfully removed

        self._removeValue(self.subjRels, subject, rel_name)
        self._removeValue(self.subjObjs, subject, object_ref)
        self._removeValue(self.relSubjs, rel_name, subject)
        self._removeValue(self.relObjs, rel_name, object_ref)
        self._removeValue(self.objRels, object_ref, rel_name)
        self._removeValue(self.objSubjs, object_ref, subject)
        self._removeValue(self.subjRel_Objs, subj_rel_key, object_ref)
        self._removeValue(self.subjObj_Rels, subj_obj_key, rel_name)
        self._removeValue(self.relObj_Subjs, rel_obj_key, subject)


    def _removeValue(self, map_dict: Dict[str, List[str]], key: str, value: str) -> None:
        """ Safely removes a value from a list within a dictionary. Cleans up empty lists/keys."""
        if key in map_dict:
            try:
                map_dict[key].remove(value)
                if not map_dict[key]: # If list becomes empty
                    del map_dict[key]
            except ValueError:
                pass # Value wasn't in the list


    def _readAttributes(self, parentNode: ET.Element) -> List[Attribute]:
        """
        Reads attributes defined as <attribute> children of the parentNode.
        Handles different datatypes (string, select, tree, entity, user-types).
        """
        fullAttrs: List[Attribute] = []
        valid_attr_attrs = ["name", "datatype", "description", "mandatory",
                            "distinguishing", "display", "target", "notes"]
        valid_value_attrs = ["name"] # For <value> tags inside select/tree

        for attr_node in parentNode.findall("attribute"):
            # self._validateTag(attr_node, ["attribute"]) # Redundant with findall
            self._validateTagAttributes(attr_node, valid_attr_attrs, "name")

            attr_name = attr_node.get("name")
            data_type = attr_node.get("datatype", "string") # Default to string if missing? Or error? Let's default.
            description = attr_node.get("description")
            notes = attr_node.get("notes") # Get notes

            if not attr_name:
                 raise ValueError("<attribute> tag requires a 'name' attribute.")

            # Initialize attribute - use basic constructor first
            currentAttr = Attribute(name=attr_name, data_type=data_type)
            currentAttr.setDescription(description or "")
            currentAttr.setNotes(notes or "") # Set notes

            # Set optional boolean flags
            self._setOptionalAttributes(attr_node.attrib, currentAttr)

            # Handle datatype specific logic
            if data_type == "select":
                 values = self._readValuesList(attr_node, "value", True) # Read <value> children, add "Other"
                 currentAttr.setValues(values) # Assuming setValues takes List[str]
            elif data_type == "tree":
                 # readValuesTree expects the root of the tree structure (<attribute> or <value>)
                 # It returns a DefaultTreeNode
                 # Pass None as parent for the root call
                 sub_classes_tree = self._readValuesTree(attr_node, None)
                 currentAttr.setSubClasses(sub_classes_tree) # Assuming setSubClasses takes TreeNode
            elif data_type == "entity":
                 target = attr_node.get("target")
                 if not target:
                      raise ValueError("<attribute> with datatype='entity' requires a 'target' attribute.")
                 currentAttr.setTarget(target)
            elif data_type == "user-types":
                 target_type_name = attr_node.get("target")
                 if not target_type_name:
                      raise ValueError("<attribute> with datatype='user-types' requires a 'target' attribute.")

                 # Find the predefined type from self.types
                 found_type = next((t for t in self.types if t.getName() == target_type_name), None)
                 if found_type:
                      try:
                           # Clone the found type definition
                           cloned_type = found_type.clone() # Assumes Attribute.clone() exists and works
                           # Override name, description, notes, and optional flags from the current node
                           cloned_type.setName(attr_name)
                           cloned_type.setDescription(description or "")
                           cloned_type.setNotes(notes or "")
                           self._setOptionalAttributes(attr_node.attrib, cloned_type)
                           currentAttr = cloned_type # Replace the initially created attribute
                      except Exception as e: # Catch potential clone errors
                           print(f"Error cloning user type '{target_type_name}' for attribute '{attr_name}': {e}")
                           # Fallback: Keep the basic attribute? Or raise error? Let's raise.
                           raise ValueError(f"Failed to clone user type '{target_type_name}'") from e
                 else:
                      raise ValueError(f"Target user type '{target_type_name}' not found for attribute '{attr_name}'. Ensure it's defined in <user-types>.")
            # Add other datatypes (string, int, etc.) if needed - currently handled by default Attribute init

            fullAttrs.append(currentAttr)

        return fullAttrs


    def _fromAttributesToString(self, attributes: List[Attribute]) -> List[str]:
        """Converts a list of Attribute objects to a list of their names."""
        return [a.getName() for a in attributes if a.getName() is not None]

    # _fromTypesToString might not be needed if UType isn't used explicitly
    # def _fromTypesToString(self, types: List[UType]) -> List[str]:
    #     return [t.getName() for t in types if t.getName() is not None]

    def _readValuesList(self, parentNode: ET.Element, tag_name: str, add_other: bool) -> List[str]:
        """
        Reads child elements with tag_name under parentNode and returns their 'name' attributes as a list.
        """
        values: List[str] = []
        valid_value_attrs = ["name"]
        for value_node in parentNode.findall(tag_name):
             # self._validateTag(value_node, [tag_name]) # Redundant
             self._validateTagAttributes(value_node, valid_value_attrs, "name")
             value_name = value_node.get("name")
             if value_name:
                  values.append(value_name)
             else:
                  raise ValueError(f"<{tag_name}> tag requires a 'name' attribute.")

        if add_other:
             values.append("Other")
        return values

    def _readValuesTree(self, parentXmlNode: ET.Element, parentTreeNode: Optional[DefaultTreeNode]) -> DefaultTreeNode:
        """
        Recursively parses <value> tags under parentXmlNode to build a DefaultTreeNode structure.
        """
        # Determine the data for the current TreeNode
        if parentXmlNode.tag == "attribute":
             # Root of the tree definition (within <attribute datatype="tree">)
             node_data = "- Select one -" # Special root node label from Java
        elif parentXmlNode.tag == "value":
             node_data = parentXmlNode.get("name")
             if not node_data:
                  raise ValueError("<value> tag within a tree structure requires a 'name' attribute.")
        else:
             # Should not happen if called correctly
             raise ValueError(f"Unexpected tag '{parentXmlNode.tag}' encountered in _readValuesTree.")

        # Create the TreeNode for the current XML node
        # Assuming DefaultTreeNode constructor handles data and parent assignment
        currentTreeNode = DefaultTreeNode(data=node_data, parent=parentTreeNode)
        # Note: Java DefaultTreeNode constructor might automatically add to parent's children.
        # Ensure Python DefaultTreeNode does this or handle it manually here if needed.
        # if parentTreeNode:
        #     parentTreeNode.add_child(currentTreeNode) # If not handled by constructor

        valid_value_attrs = ["name"]
        # Recursively process child <value> tags
        for childXmlNode in parentXmlNode.findall("value"):
             # self._validateTag(childXmlNode, ["value"]) # Redundant
             self._validateTagAttributes(childXmlNode, valid_value_attrs, "name")
             # Recursive call to build the subtree
             childTreeNode = self._readValuesTree(childXmlNode, currentTreeNode)
             # If constructor doesn't add child, do it here:
             # currentTreeNode.add_child(childTreeNode)

             # Java code adds an "Other <name>" node if the child has further children (is not a leaf)
             # Check if the newly created childTreeNode has children itself
             if childTreeNode.get_children(): # Assuming get_children() returns the list
                  other_node_data = f"Other {childXmlNode.get('name')}"
                  # Create the "Other" node as a child of the *childTreeNode*
                  DefaultTreeNode(data=other_node_data, parent=childTreeNode)
                  # Again, ensure constructor handles parent assignment or do it manually

        return currentTreeNode


    def _addValue(self, map_dict: Dict[str, List[str]], key: str, value: str) -> None:
        """Adds a value to a list within a dictionary, ensuring no duplicates in the list."""
        if value not in map_dict[key]: # defaultdict ensures key exists
            map_dict[key].append(value)
            # Java code sorted here, decide if needed in Python (sort on retrieval?)
            # map_dict[key].sort()


    def _setOptionalAttributes(self, attrib_map: Dict[str, str], attr_obj: Attribute) -> None:
        """Sets optional boolean attributes (mandatory, distinguishing, display) on an Attribute object."""
        # Mandatory
        mandatory_str = attrib_map.get("mandatory", "false")
        attr_obj.setMandatory(mandatory_str.lower() == "true")

        # Distinguishing
        distinguishing_str = attrib_map.get("distinguishing", "false")
        attr_obj.setDistinguishing(distinguishing_str.lower() == "true")

        # Display
        display_str = attrib_map.get("display", "false")
        attr_obj.setDisplay(display_str.lower() == "true")


    def getInverseRel(self, relationship_name: str) -> Optional[str]:
        """Gets the inverse relationship name for the given relationship name."""
        # First check the precomputed map (populated during parsing)
        if relationship_name in self.inverseRels:
             return self.inverseRels[relationship_name]

        # Fallback: search the tree (might be slow if called often before map is full)
        relationship = self.getRelationship(relationship_name)
        if relationship:
            # Store it for faster lookup next time
            inverse = relationship.getInverse()
            if inverse:
                 self.inverseRels[relationship_name] = inverse
                 self.inverseRels[inverse] = relationship_name # Store both ways
            return inverse
        return None

    def getDomain(self) -> Optional[str]:
        """Returns the primary domain name associated with this DomainData instance."""
        return self.domain

    def getEntitiesNotRemoved(self, toRemove: Optional[List[str]] = None) -> List[Entity]:
        """Returns a list of top-level entities, filtering out those in the optional toRemove list."""
        top_entities = self.getTopEntities()
        if toRemove is None:
            toRemove = self.removedEntities # Use tracked removed entities if none provided

        if not toRemove:
            return top_entities # No filtering needed

        return [e for e in top_entities if e.getName() not in toRemove]

    def getAllEntities(self) -> List[Entity]:
        """Returns a flat list of all entities in the tree (including sub-entities)."""
        all_entities: List[Entity] = []
        if not self.entityTree:
            return all_entities

        queue = list(self.entityTree.getChildren()) # Start with top-level entities
        visited = set()

        while queue:
            current_entity = queue.pop(0)
            if current_entity in visited: continue
            visited.add(current_entity)

            all_entities.append(current_entity)
            # Add children to the queue for processing
            queue.extend(current_entity.getChildren())

        return all_entities

    def getAllEntitiesToString(self) -> List[str]:
        """Returns a flat list of names of all entities in the tree."""
        return [e.getName() for e in self.getAllEntities()]

    def getRelationship(self, relName: str) -> Optional[Relationship]:
        """Retrieves a relationship by its name by searching the relationship tree."""
        # Use findInTree which performs DFS
        found_entity = self.findInTree(self.relationshipTree, relName)
        if found_entity and isinstance(found_entity, Relationship):
            return found_entity
        return None

    # getRelationship(String relName, ArrayList<Relationship> topRels) - Java version seems redundant if findInTree works

    def getAllRelationships(self) -> List[Relationship]:
        """Returns a flat list of all relationships in the tree (including sub-relationships)."""
        all_rels: List[Relationship] = []
        if not self.relationshipTree:
            return all_rels

        queue: List[Entity] = list(self.relationshipTree.getChildren()) # Start with top-level
        visited = set()

        while queue:
            current_entity = queue.pop(0)
            if current_entity in visited: continue
            visited.add(current_entity)

            if isinstance(current_entity, Relationship):
                all_rels.append(current_entity)
                # Add children (which should also be Relationships or Entities) to the queue
                queue.extend(current_entity.getChildren())
            elif isinstance(current_entity, Entity): # Should not happen in relationship tree?
                 print(f"Warning: Found non-Relationship Entity '{current_entity.getName()}' in relationship tree traversal.")
                 queue.extend(current_entity.getChildren())


        return all_rels

    def getAllRelationshipsToString(self) -> List[str]: # Changed from TreeSet to List for simplicity
        """Returns a sorted list of names of all relationships in the tree."""
        names = {r.getName() for r in self.getAllRelationships()}
        return sorted(list(names))

    # _getAllChildren and _getAllChildrenToString are effectively handled by getAllEntities/getAllRelationships logic

    def getTopEntitiesToString(self) -> List[str]:
        """Returns a list of names of the top-level entities."""
        return [e.getName() for e in self.getTopEntities()]

    def getSubjsFromRel(self, relationship_name: str) -> Set[str]: # Changed from TreeSet to Set
        """Gets all unique subjects associated with a given relationship name (including inheritance)."""
        relationship = self.getRelationship(relationship_name)
        if relationship:
            # Assuming Relationship class has getSubjects() that handles inheritance/all references
            return relationship.getSubjects()
        return set()

    def getObjsFromRel(self, relationship_name: str) -> Set[str]: # Changed from TreeSet to Set
        """Gets all unique objects associated with a given relationship name (including inheritance)."""
        relationship = self.getRelationship(relationship_name)
        if relationship:
            # Assuming Relationship class has getObjects() that handles inheritance/all references
            return relationship.getObjects()
        return set()

    def getSubjects(self) -> List[str]: # Changed from TreeSet to List
        """Returns a sorted list of all unique subjects found in references."""
        return sorted(list(set(self.subjects))) # Ensure uniqueness and sort

    def getObjects(self) -> List[str]: # Changed from TreeSet to List
        """Returns a sorted list of all unique objects found in references."""
        return sorted(list(set(self.objects))) # Ensure uniqueness and sort

    def getSubjObj_Rels(self, subject: str, object_ref: str) -> Set[str]: # Changed return type
        """Gets the set of relationship names connecting a specific subject to a specific object."""
        key = f"{subject}.{object_ref}"
        # Return a copy to prevent external modification
        return set(self.subjObj_Rels.get(key, []))

    # --- Getters and Setters for Scaraggi attributes ---
    def getInverseRels(self) -> Dict[str, str]:
        return self.inverseRels
    def setInverseRels(self, inverseRels: Dict[str, str]) -> None:
        self.inverseRels = inverseRels

    def getRelSubjs(self) -> Dict[str, List[str]]:
        return self.relSubjs
    def setRelSubjs(self, relSubjs: Dict[str, List[str]]) -> None:
        self.relSubjs = relSubjs

    def getRelObjs(self) -> Dict[str, List[str]]:
        return self.relObjs
    def setRelObjs(self, relObjs: Dict[str, List[str]]) -> None:
        self.relObjs = relObjs

    def getAttrsRel(self) -> Dict[str, List[Attribute]]:
        return self.attrsRel
    def setAttrsRel(self, attrsRel: Dict[str, List[Attribute]]) -> None:
        self.attrsRel = attrsRel

    def getInverse(self) -> Optional[str]:
        return self.inverse
    def setInverse(self, inverse: str) -> None:
        self.inverse = inverse

    def getDomainList(self) -> Optional[List[str]]:
        return self.domainList
    def setDomainList(self, domainList: List[str]) -> None:
        self.domainList = domainList
    # --- End Scaraggi Getters/Setters ---

    def getRelationshipsToString(self, entity_name: str) -> List[Relationship]: # Renamed from Java Vector return
        """Retrieves relationships where the given entity name is either subject or object."""
        includes: List[Relationship] = []
        # This needs to check inheritance/subclasses potentially.
        # Simple check first:
        for rel in self.getAllRelationships():
            # Check direct references
            has_entity = any(ref.getSubject() == entity_name or ref.getObject() == entity_name
                             for ref in rel.getReferences())
            # TODO: Add check for entity subclasses/supertypes if needed.
            # This might involve getting all subclasses of entity_name and checking them too.
            if has_entity:
                includes.append(rel)
        return includes

    def getRelationshipsForSubj(self, entity_name: str) -> List[Relationship]:
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the subject."""
        includes: List[Relationship] = []
        # TODO: Consider inheritance for entity_name if required by application logic.
        # Get the entity object to potentially check its subclasses later
        # subj_entity = self.getEntity(entity_name)
        # if not subj_entity: return [] # Entity doesn't exist

        for rel in self.getAllRelationships():
            # Check direct references
            has_subj = any(ref.getSubject() == entity_name for ref in rel.getReferences())
            # Add inheritance check if needed:
            # all_subj_types = {sub.getName() for sub in subj_entity.getAllSubclasses()} | {entity_name}
            # has_subj = any(ref.getSubject() in all_subj_types for ref in rel.getReferences())
            if has_subj:
                includes.append(rel)
        return includes

    def getRelationshipsForObj(self, entity_name: str) -> List[Relationship]:
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the object."""
        includes: List[Relationship] = []
        # TODO: Consider inheritance for entity_name if required.
        for rel in self.getAllRelationships():
            has_obj = any(ref.getObject() == entity_name for ref in rel.getReferences())
            if has_obj:
                includes.append(rel)
        return includes

    def getImportedFiles(self) -> List[str]:
        """Returns the list of absolute paths of imported .gbs files."""
        return self.importedFiles

    def getEntity(self, entityName: str) -> Optional[Entity]:
        """Retrieves an entity by its name by searching the entity tree."""
        # Use findInTree which performs DFS
        return self.findInTree(self.entityTree, entityName)

    # getSubEntity seems redundant if getEntity searches the whole tree.

    def removeEntities(self, entities_to_remove: List[Entity]) -> None:
        """Removes a list of entity objects from the tree."""
        # This seems dangerous if entities are not top-level.
        # Java code checked domain, maybe intended for cleanup after import?
        print("Warning: removeEntities(List<Entity>) might be unsafe. Prefer removeEntity(name).")
        for e in entities_to_remove:
             # Java code checked if domain was different from current primary domain
             # if e.getDomain() != self.domain:
             # Maybe just remove by name?
             self.removeEntity(e.getName())


    def removeRelationships(self, domainToRemove: str) -> None:
        """Removes all relationships belonging to a specific domain."""
        # This seems intended for cleaning up after imports.
        rels_in_domain = [r for r in self.getAllRelationships() if r.getDomain() == domainToRemove]
        print(f"Removing {len(rels_in_domain)} relationships belonging to domain: {domainToRemove}")
        for r in rels_in_domain:
            self.removeRelationship(r.getName())


    def findInTree(self, parent: Entity, nodeName: str) -> Optional[Entity]:
        """
        Finds the entity/relationship with the given name in the tree starting from parent (DFS).
        Case-insensitive search matching Java behavior.
        """
        if not parent:
            return None

        # Using a stack for iterative DFS to avoid deep recursion issues
        stack: List[Entity] = list(parent.getChildren()) # Start search from children of parent

        while stack:
            current_node = stack.pop()
            # Compare names case-insensitively
            if current_node.getName().lower() == nodeName.lower():
                return current_node

            # Add children to stack for further exploration
            # Add in reverse order to mimic recursive DFS order if needed, though order often doesn't matter for find
            stack.extend(reversed(current_node.getChildren()))

        return None


    def getnTopEntities(self) -> int:
        """Returns the number of top-level entities."""
        return len(self.getTopEntities())

    def getnSubEntities(self) -> int:
        """Returns the number of non-top-level entities."""
        # This calculation might be fragile if the tree structure is complex
        return len(self.getAllEntities()) - self.getnTopEntities()

    def getnTopRels(self) -> int:
        """Returns the number of top-level relationships."""
        return len(self.getTopRelationships())

    def getnRelRefs(self) -> int:
        """Returns the total number of relationship references parsed."""
        return self.nRelRefs

    @staticmethod
    def readFile(path: str, encoding: str = 'utf-8') -> str:
        """Reads a file and returns its content as a string."""
        try:
            with codecs.open(path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            raise

    def getRelationshipsWithSubj(self, subject: str) -> Set[str]: # Changed from TreeSet
        """Retrieves the names of top-level relationships involving the subject (or its subclasses)."""
        relationships: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        # Get all types this subject could represent (itself + subclasses)
        subj_types: Set[str] = {subject}
        if subj_entity:
             # Assuming getAllSubclasses includes the entity itself? If not, add manually.
             # getAllSubclassNames(False) seems to get all descendants + self
             try:
                  subj_types.update(subj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getRelationshipsWithSubj might be incomplete.")


        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                if ref.getSubject() in subj_types:
                    # Add the top-level ancestor relationship name
                    try:
                         top_rel_name = rel.getTop() # Assumes getTop() exists and returns name
                         relationships.add(top_rel_name)
                    except AttributeError:
                         print(f"Warning: Relationship class missing 'getTop'. Cannot determine top relationship for '{rel.getName()}'.")
                         relationships.add(rel.getName()) # Fallback to adding the direct relationship name
                    break # Found one reference for this relationship, move to next relationship
        return relationships


    def getRelationshipsWithObj(self, object_ref: str) -> Set[str]: # Changed from TreeSet
        """Retrieves the names of top-level relationships involving the object (or its subclasses)."""
        relationships: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref)
        obj_types: Set[str] = {object_ref}
        if obj_entity:
             try:
                  obj_types.update(obj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getRelationshipsWithObj might be incomplete.")


        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                if ref.getObject() in obj_types:
                    try:
                         top_rel_name = rel.getTop()
                         relationships.add(top_rel_name)
                    except AttributeError:
                         print(f"Warning: Relationship class missing 'getTop'. Cannot determine top relationship for '{rel.getName()}'.")
                         relationships.add(rel.getName())
                    break
        return relationships

    def getObjsFromRel(self, relationships: List[str]) -> List[str]: # Changed from Vector
        """Retrieves unique objects from a list of relationship names."""
        objects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                # getObjects should return all objects for this rel and its children
                objects_set.update(rel.getObjects())
        return sorted(list(objects_set))

    def getSubjsFromRel(self, relationships: List[str]) -> List[str]: # Changed from Vector
        """Retrieves unique subjects from a list of relationship names."""
        subjects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                # getSubjects should return all subjects for this rel and its children
                subjects_set.update(rel.getSubjects())
        return sorted(list(subjects_set))

    def getObjsFromSubjRel(self, subject: str, relName: str) -> Set[str]: # Changed from TreeSet
        """Retrieves objects related to a subject via a specific relationship (considering inheritance)."""
        objects_set: Set[str] = set()
        rel = self.getRelationship(relName)
        if not rel: return set()

        subj_entity = self.findInTree(self.entityTree, subject)
        subj_types: Set[str] = {subject}
        if subj_entity:
             try:
                  subj_types.update(subj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getObjsFromSubjRel might be incomplete.")

        # Need to check all references in the relationship and its descendants
        all_refs_in_rel_tree: List[Reference] = []
        queue = [rel]
        visited = set()
        while queue:
             current_rel = queue.pop(0)
             if current_rel in visited: continue
             visited.add(current_rel)
             all_refs_in_rel_tree.extend(current_rel.getReferences())
             # Add children relationships to queue
             queue.extend(current_rel.getChildrenRelationships()) # Assumes this method exists


        for ref in all_refs_in_rel_tree:
            if ref.getSubject() in subj_types:
                objects_set.add(ref.getObject())

        return objects_set

    def getSubjsFromObjRel(self, object_ref: str, relName: str) -> Set[str]: # Changed from TreeSet
        """Retrieves subjects related to an object via a specific relationship (considering inheritance)."""
        subjects_set: Set[str] = set()
        rel = self.getRelationship(relName)
        if not rel: return set()

        obj_entity = self.findInTree(self.entityTree, object_ref)
        obj_types: Set[str] = {object_ref}
        if obj_entity:
             try:
                  obj_types.update(obj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getSubjsFromObjRel might be incomplete.")

        all_refs_in_rel_tree: List[Reference] = []
        queue = [rel]
        visited = set()
        while queue:
             current_rel = queue.pop(0)
             if current_rel in visited: continue
             visited.add(current_rel)
             all_refs_in_rel_tree.extend(current_rel.getReferences())
             queue.extend(current_rel.getChildrenRelationships())

        for ref in all_refs_in_rel_tree:
            if ref.getObject() in obj_types:
                subjects_set.add(ref.getSubject())

        return subjects_set

    def getRelFromSubjObj(self, subject: str, object_ref: str) -> Set[str]: # Changed from TreeSet
        """Retrieves top-level relationship names connecting a subject and object (considering inheritance)."""
        rels_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        obj_entity = self.findInTree(self.entityTree, object_ref)

        subj_types: Set[str] = {subject}
        if subj_entity:
             try: subj_types.update(subj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError: pass # Warning already printed if missing

        obj_types: Set[str] = {object_ref}
        if obj_entity:
             try: obj_types.update(obj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError: pass # Warning already printed if missing

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                if ref.getSubject() in subj_types and ref.getObject() in obj_types:
                    try:
                         top_rel_name = rel.getTop()
                         rels_set.add(top_rel_name)
                    except AttributeError:
                         rels_set.add(rel.getName()) # Fallback
                    break # Found a match for this relationship, move to next rel
        return rels_set


    def getObjsFromSubRels(self, subject: str, relationships: List[str]) -> List[str]: # Changed from Vector
        """Retrieves unique objects related to a subject via a list of relationship names."""
        objects_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        subj_types: Set[str] = {subject}
        if subj_entity:
             try: subj_types.update(subj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError: pass

        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                 all_refs_in_rel_tree: List[Reference] = []
                 queue = [rel]
                 visited = set()
                 while queue:
                      current_rel = queue.pop(0)
                      if current_rel in visited: continue
                      visited.add(current_rel)
                      all_refs_in_rel_tree.extend(current_rel.getReferences())
                      queue.extend(current_rel.getChildrenRelationships())

                 for ref in all_refs_in_rel_tree:
                      if ref.getSubject() in subj_types:
                           objects_set.add(ref.getObject())

        return sorted(list(objects_set))

    def getObjsFromSubj(self, subject: str) -> Set[str]: # Changed from TreeSet
        """Retrieves all unique objects related to a subject across all relationships."""
        objects_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        subj_types: Set[str] = {subject}
        if subj_entity:
             try: subj_types.update(subj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError: pass

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                if ref.getSubject() in subj_types:
                    objects_set.add(ref.getObject())
        return objects_set

    def getSubjsFromObj(self, object_ref: str) -> Set[str]: # Changed from TreeSet
        """Retrieves all unique subjects related to an object across all relationships."""
        subjects_set: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref)
        obj_types: Set[str] = {object_ref}
        if obj_entity:
             try: obj_types.update(obj_entity.getAllSubclassNames(subclassRestriction=False))
             except AttributeError: pass

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                if ref.getObject() in obj_types:
                    subjects_set.add(ref.getSubject())
        return subjects_set

    def getAxioms(self) -> Set[Axiom]:
        """Returns the set of axioms."""
        return self.axioms

    def setAxioms(self, axioms: Set[Axiom]) -> None:
        """Sets the set of axioms."""
        self.axioms = axioms

    # --- Methods from Java end section that were commented out or seemed internal ---
    # getSubjRelObjs() -> returns self.subjRelObjs
    # getSubjRels(Entity) -> use self.subjRels[entity.getName()]
    # getSubjObjs(Entity) -> use self.subjObjs[entity.getName()]
    # getRelSubjs(Relationship) -> use self.relSubjs[relationship.getName()]
    # getRelObjs(Relationship) -> use self.relObjs[relationship.getName()]
    # getObjSubjs(Entity) -> use self.objSubjs[entity.getName()]
    # getObjRels(Entity) -> use self.objRels[entity.getName()]
    # getSubjRel_Objs(Entity, Relationship) -> use self.subjRel_Objs[f"{subject.name}.{relationship.name}"]
    # getSubjObj_Rels(Entity, Entity) -> use self.subjObj_Rels[f"{subject.name}.{object.name}"]
    # getRelObj_Subjs(Relationship, Entity) -> use self.relObj_Subjs[f"{relationship.name}.{object.name}"]
    # getRelationships(Entity) -> Implemented as getRelationshipsToString(entity_name) returning List[Relationship]
