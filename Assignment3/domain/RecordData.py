import os
import xml.etree.ElementTree as ET
from pathlib import Path
import io
import codecs
from typing import List, Dict, Set, Optional, Tuple, Union, cast, Any
from collections import defaultdict
import copy
import traceback
import warnings # To warn about TreeSet vs set differences

# Assuming domain classes are in the same directory or accessible via PYTHONPATH
# These imports might need adjustment based on your actual project structure
try:
    from .Attribute import Attribute
    from .Entity import Entity
    from .Union import Union
    from .Axiom import Axiom
    from .Relationship import Relationship
    from .Reference import Reference
    from .TreeNode import TreeNode # Assuming TreeNode is the base or interface
    from .DefaultTreeNode import DefaultTreeNode # Assuming this is the implementation used
    # from .UType import UType # If needed
except ImportError:
    # Fallback if running script directly or structure differs
    warnings.warn("Could not import domain classes using relative paths. Ensure they are accessible.")
    # Define dummy classes if needed for type hinting, or handle errors later
    class Attribute: pass
    class Entity: pass
    class Union: pass
    class Axiom: pass
    class Relationship(Entity): pass # Assuming Relationship inherits from Entity based on Java code
    class Reference: pass
    class TreeNode: pass
    class DefaultTreeNode(TreeNode): pass


# Helper Pair class (can be replaced by tuple if preferred)
class Pair:
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value

    def getKey(self) -> Any:
        return self.key

    def getValue(self) -> Any:
        return self.value

class RecordData:
    """
    This class represents the domain data for a specific domain.
    It contains methods for loading and parsing .gbr files (equivalent to .gbs in DomainData),
    as well as storing and manipulating domain information.
    The domain data includes entities, relationships, attributes, union_entities axioms, etc.
    Translated from RecordData.java.
    """
    # --- Instance Variables ---
    attributesList: List[Attribute]
    entityForm: Dict[str, str]
    types: List[Attribute] # Java: Vector<Attribute>
    importedFiles: List[str] # Java: ArrayList<String>
    removedEntities: List[str] # Java: ArrayList<String>
    removedRelationships: List[str] # Java: ArrayList<String>
    domain: Optional[str] # Java: String
    entityTree: Entity # Java: Entity
    unions: Set[Union] # Java: HashSet<Union>
    axioms: Set[Axiom] # Java: HashSet<Axiom>
    relationshipTree: Relationship # Java: Relationship
    subjects: List[str] # Java: Vector<String>
    objects: List[str] # Java: Vector<String>
    # Note: Java TreeSet is ordered, Python set is unordered. Sorting applied on retrieval if needed.
    subjRelObjs: Set[str] # Java: TreeSet<String>
    subjRels: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    subjObjs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    relSubjs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    relObjs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    objSubjs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    objRels: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    subjRel_Objs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    subjObj_Rels: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    relObj_Subjs: Dict[str, List[str]] # Java: Map<String,Vector<String>>
    inverseRels: Dict[str, str] # Java: Map<String,String>
    nRelRefs: int # Java: int
    webInfFolder: str # Java: String

    # Scaraggi attributes from Java end section
    domainList: Optional[List[str]] = None # Java: ArrayList<String>
    inverse: Optional[str] = None # Java: String
    attrsRel: Dict[str, List[Attribute]] # Java: Map<String, Vector<Attribute>>

    # --- Constructor ---
    def __init__(self,
                 path_or_bytearray: Optional[Union[str, bytes]] = None,
                 webInfFolder: Optional[str] = None,
                 domainName: Optional[str] = None,
                 file: Optional[Union[str, Path]] = None):
        """
        Initializes the RecordData object. Mimics Java overloaded constructors:
        1. RecordData(): Default constructor (call with no arguments).
        2. RecordData(path): Loads from a .gbr file path or domain name (String path).
           Requires webInfFolder if path is just a domain name.
        3. RecordData(byteArray, webInfFolder): Loads from byte array (byte[] byteArray, String webInfFolder).
        4. RecordData(domainName, file): Loads an arbitrary file with a given domain name (String domainName, File file).
        """
        # Default initializations
        self.attributesList = []
        self.entityForm = {}
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

        # Initialize root Entity (matches Java constructor logic)
        self.entityTree = Entity(name="Entity", domain=None) # Assuming Entity constructor
        entity_attributes = [
            Attribute(name="name", data_type="string", mandatory="true"), # Match Java string bools for now
            Attribute(name="description", data_type="string", mandatory="false"),
            Attribute(name="notes", data_type="string", mandatory="false")
        ]
        # Ensure Attribute class handles string bools or adjust here
        # Assuming Entity has addAttributes and setChildren methods
        if hasattr(self.entityTree, 'addAttributes'):
            self.entityTree.addAttributes(entity_attributes)
        if hasattr(self.entityTree, 'setChildren'):
            self.entityTree.setChildren([])

        # Initialize root Relationship (matches Java constructor logic)
        # Assuming Relationship constructor and setChildren
        self.relationshipTree = Relationship(domain=None, name="Relationship", inverse="Relationship")
        if hasattr(self.relationshipTree, 'setChildren'):
            self.relationshipTree.setChildren([])

        # Scaraggi attributes initialization
        self.domainList = None
        self.inverse = None
        self.attrsRel = defaultdict(list)

        # --- Constructor Logic ---
        try:
            # Case 3: RecordData(byte[] byteArray, String webInfFolder)
            if isinstance(path_or_bytearray, bytes) and webInfFolder is not None:
                if domainName is not None or file is not None:
                    raise TypeError("Cannot provide domainName or file when using byte array constructor.")
                self.webInfFolder = webInfFolder # Already set, but confirm
                is_ = io.BytesIO(path_or_bytearray)
                doc = self._parse_stream(is_) # Use helper for stream parsing
                root_element = doc.getroot()
                domain_name_from_bytes = root_element.get("name")
                if domain_name_from_bytes is None:
                     raise ValueError("Root <domain> tag must have a 'name' attribute.")
                self.domain = domain_name_from_bytes # Set domain early like Java
                # Java passes the extracted domain name as domainPath to loadFile
                self._loadFile(doc, self.domain)

            # Case 4: RecordData(String domainName, File file)
            elif domainName is not None and file is not None:
                if path_or_bytearray is not None:
                     raise TypeError("Cannot provide path_or_bytearray when using domainName/file constructor.")
                self.domain = domainName # Set domain explicitly like Java
                file_path = Path(file)
                doc = self._parseFile(file_path)
                # Java passes the absolute path of the file
                self._loadFile(doc, str(file_path.resolve()))

            # Case 2: RecordData(String path)
            elif isinstance(path_or_bytearray, str):
                 if domainName is not None or file is not None:
                     raise TypeError("Cannot provide domainName or file when using path string constructor.")
                 path_str = path_or_bytearray
                 file_path: Path
                 domain_path_for_load: str
                 # Use .gbr extension like Java
                 if path_str.endswith(".gbr"):
                     file_path = Path(path_str)
                     # Use absolute path for consistency and import tracking
                     domain_path_for_load = str(file_path.resolve())
                     doc = self._parseFile(file_path)
                     self._loadFile(doc, domain_path_for_load)
                 else:
                     # Assumes path is domain name and needs webInfFolder
                     if not self.webInfFolder:
                          raise ValueError("webInfFolder must be provided if path is not a full .gbr path")
                     file_path = Path(self.webInfFolder) / (path_str + ".gbr")
                     # Use absolute path for consistency
                     domain_path_for_load = str(file_path.resolve())
                     doc = self._parseFile(file_path)
                     # Java passed 'path' (the domain name) as domainPath here.
                     # Pass the absolute path to loadFile for consistency in getFolderPath.
                     self._loadFile(doc, domain_path_for_load)

            # Case 1: RecordData() (Default constructor)
            elif path_or_bytearray is None and webInfFolder is None and domainName is None and file is None:
                # Initializations already done, nothing more to do.
                pass

            else:
                 # Invalid combination of arguments
                 raise TypeError("Invalid combination of arguments for RecordData constructor")

        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            traceback.print_exc()
            raise
        except ET.ParseError as e:
            print(f"Error: XML parsing failed - {e}")
            traceback.print_exc()
            raise
        except Exception as e:
            print(f"Error initializing RecordData: {e}")
            traceback.print_exc()
            raise

    # --- Private Helper Methods ---

    def _parse_stream(self, stream: io.BytesIO) -> ET.ElementTree:
        """Parses an XML stream into an ElementTree."""
        try:
            # Note: Java uses DOM parser (DocumentBuilder), Python uses ElementTree (ET)
            tree = ET.parse(stream)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            raise

    def _parseFile(self, file_path: Path) -> ET.ElementTree:
        """Parses the given file path and returns an ElementTree object."""
        try:
            tree = ET.parse(file_path)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error in file {file_path}: {e}")
            raise
        except FileNotFoundError:
            print(f"Error: File not found at path {file_path}")
            raise
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            raise

    def _getFolderPath(self, domainPath: str) -> List[str]:
        """
        Retrieves the folder path for the given domain path.
        Returns a list [base_filename_without_extension, folder_path].
        """
        print(f"Getting folder path for: {domainPath}") # Mimic Java logging
        folderPath: List[str] = ["", ""]
        path_obj = Path(domainPath)

        # Check if it looks like a full path (contains directory separators)
        # Use os.path.sep for OS-agnostic check, and also check for '/'
        if os.path.sep in domainPath or "/" in domainPath:
             folderPath[1] = str(path_obj.parent)
             # Use .gbr extension like Java
             folderPath[0] = path_obj.name.replace(".gbr", "")
        else:
             # Assumes domainPath is just the domain name (without .gbr)
             folderPath[1] = self.webInfFolder
             folderPath[0] = domainPath # Java sets folderPath[0] to domainPath initially

        print(f"  Base name: {folderPath[0]}, Folder: {folderPath[1]}") # Mimic Java output
        return folderPath

    def _validateTag(self, tag: ET.Element, validTags: List[str]) -> None:
        """
        Validates a tag against a list of valid tags.
        Raises ValueError if the tag is not found in the list.
        """
        if tag.tag not in validTags:
            parent_info = ""
            # Getting parent in ET requires a parent map, which is expensive.
            # We'll omit the parent info for simplicity, matching DomainData.py
            # parent_map = {c: p for p in root.iter() for c in p} # Example if needed
            # parent = parent_map.get(tag)
            # if parent is not None:
            #    parent_name_attr = parent.get('name', '')
            #    parent_info = f" under <{parent.tag} {parent_name_attr}>"

            raise ValueError(
                f"Invalid tag <{tag.tag}> found where one of {validTags} was expected"
                # Consider adding parent info if a parent map is maintained during parsing
            )

    def _validateTagAttributes(self, tag: ET.Element, validTagAttributes: List[str], identifier: str) -> None:
        """
        Validates the attributes of a given XML tag against a list of valid attributes.
        Raises ValueError if any invalid attribute is found.
        """
        tag_identifier_info = ""
        if identifier and identifier in tag.attrib:
            tag_identifier_info = f" {tag.attrib[identifier]}"

        for attr_name in tag.attrib:
            if attr_name not in validTagAttributes:
                raise ValueError(
                    f"Invalid attribute \"{attr_name}\" found in <{tag.tag}{tag_identifier_info}>. Expected one of: {validTagAttributes}"
                )

    def _loadFile(self, doc: ET.ElementTree, domainPath: str) -> None:
        """
        Loads a file and parses its contents to populate the domain data.
        Internal helper corresponding to Java's private void loadFile(Document doc, String domainPath).
        """
        folderPath = self._getFolderPath(domainPath)
        # base_name = folderPath[0] # Not used directly in Java logic here
        folder_path_str = folderPath[1]
        webInf = Path(folder_path_str) # Use Path object for consistency

        root_element = doc.getroot()

        # --- Validation ---
        # Validate root tag is <domain>
        if root_element.tag != "domain":
             raise ValueError(f"Expected root tag <domain>, but found <{root_element.tag}> in {domainPath}")

        # Validate domain name attribute
        domain_name_attr = root_element.get("name")
        if domain_name_attr is None:
             raise ValueError(f"Root tag <domain> must have a 'name' attribute in {domainPath}")

        # Set domain if not already set (matches Java logic)
        if self.domain is None:
            self.domain = domain_name_attr
        # Java doesn't explicitly check for domain mismatch here. Add warning like DomainData.py
        elif self.domain != domain_name_attr and domainPath not in self.importedFiles:
             print(f"Warning: Loading file with domain '{domain_name_attr}' into existing domain '{self.domain}' from {domainPath}")

        # --- Process Child Elements ---
        # Java uses index-based access and checks node names. Python uses iteration and tag checks.
        allowed_sections = ["imports", "user-types", "entities", "union_entities", "relationships", "axioms"]

        # Filter out non-element nodes (like comments, PIs)
        children = [child for child in root_element if isinstance(child.tag, str)]

        current_child_index = 0

        # --- 1. Imports (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "imports":
            self._validateTag(children[current_child_index], ["imports"])
            self._parseImports(webInf, children[current_child_index])
            current_child_index += 1

        # --- 2. User Types (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "user-types":
             self._validateTag(children[current_child_index], ["user-types"])
             self._parseTypes(webInf, children[current_child_index])
             current_child_index += 1

        # --- 3. Entities (Mandatory) ---
        if current_child_index >= len(children) or children[current_child_index].tag != "entities":
            raise ValueError(f"Missing mandatory <entities> section in domain '{self.domain or domain_name_attr}' file: {domainPath}")
        self._validateTag(children[current_child_index], ["entities"])
        # Pass current domain name
        self._parseEntities(children[current_child_index], self.entityTree, self.domain or domain_name_attr)
        current_child_index += 1

        # --- 4. Union Entities (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "union_entities":
             self._validateTag(children[current_child_index], ["union_entities"])
             self._parseUnionEntities(children[current_child_index], self.domain or domain_name_attr)
             current_child_index += 1

        # --- 5. Relationships (Mandatory) ---
        if current_child_index >= len(children) or children[current_child_index].tag != "relationships":
             raise ValueError(f"Missing mandatory <relationships> section in domain '{self.domain or domain_name_attr}' file: {domainPath}")
        self._validateTag(children[current_child_index], ["relationships"])
        self._parseRelationships(children[current_child_index], self.relationshipTree, self.domain or domain_name_attr)
        current_child_index += 1

        # --- 6. Axioms (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "axioms":
             self._validateTag(children[current_child_index], ["axioms"])
             self._parseAxioms(children[current_child_index], self.domain or domain_name_attr)
             current_child_index += 1

        # Check for unexpected tags
        if current_child_index < len(children):
            unexpected_tag = children[current_child_index].tag
            raise ValueError(f"Unexpected tag <{unexpected_tag}> found in <domain> tag in {domainPath}. Allowed order: {allowed_sections}")

        # Sort subjects and objects (matches Java)
        self.subjects.sort()
        self.objects.sort()

    def _parseAxioms(self, axioms_tag: ET.Element, domainName: str) -> None:
        """
        Parses the axioms from the given XML node (<axioms>) and adds them to the axioms set.
        """
        valid_axiom_children = ["axiom"]
        valid_axiom_attrs = ["name", "formalism", "rule"] # Java code uses name, formalism, rule

        for axiom_node in axioms_tag:
            if not isinstance(axiom_node.tag, str): continue # Skip comments/PIs
            self._validateTag(axiom_node, valid_axiom_children)
            self._validateTagAttributes(axiom_node, valid_axiom_attrs, "name")

            name = axiom_node.get("name")
            formalism = axiom_node.get("formalism")
            # Java code seems to get rule from attribute, not text content based on validation
            expression = axiom_node.get("rule")
            # expression = axiom_node.text # If rule was text content

            if name is None or formalism is None or expression is None:
                 raise ValueError("<axiom> tag requires 'name', 'formalism', and 'rule' attributes.")

            print(f"Parsing Axiom: {name} {formalism} {expression}") # Mimic Java logging
            new_axiom = Axiom(name=name, formalism=formalism, expression=expression, domain=domainName) # Assuming Axiom constructor
            if new_axiom in self.axioms:
                 # Java checks equality, which might compare content. Python set checks hash/equality.
                 # If axioms with same name but different content are allowed, this check needs adjustment.
                 # For now, assume name is the unique identifier based on Java's exception message.
                 raise ValueError(f"Duplicate Axiom: \"{name}\" in domain \"{domainName}\"")
            self.axioms.add(new_axiom)

    def _parseUnionEntities(self, union_entities_tag: ET.Element, domainName: str) -> None:
        """
        Parses the union entities from the <union_entities> tag and adds them to the domain data.
        """
        valid_union_children = ["union"]
        valid_union_attrs = ["name"]
        valid_uvalue_children = ["uvalue"] # Java uses readValuesList with "uvalue"

        unions_to_add: List[Union] = []

        for union_node in union_entities_tag:
            if not isinstance(union_node.tag, str): continue # Skip comments/PIs
            self._validateTag(union_node, valid_union_children)
            self._validateTagAttributes(union_node, valid_union_attrs, "name")

            union_name = union_node.get("name")
            if union_name is None:
                raise ValueError("<union> tag requires a 'name' attribute.")

            # Check for conflict with existing entities (Java logic)
            if self.findInTree(self.entityTree, union_name) is not None:
                raise ValueError(f"Entity \"{union_name}\" already exists, can't create union entity with the same name")

            # Read <uvalue> children using readValuesList logic
            uvalues = self._readValuesList(union_node, "uvalue", False) # False for add_other

            new_union = Union(name=union_name, domain=domainName, values=set(uvalues)) # Assuming Union constructor
            unions_to_add.append(new_union)

        self._addUnions(unions_to_add)

    def _addUnions(self, _unions: List[Union]) -> None:
        """
        Adds a list of Union objects to the domain's unions set.
        Handles merging/updating if a union with the same name exists from a different domain.
        """
        # Check that all uvalues are existing entities (Java logic)
        for u in _unions:
            if not hasattr(u, 'getValues') or not hasattr(u, 'getName'): continue # Skip if malformed
            for val in u.getValues():
                if self.findInTree(self.entityTree, val) is None:
                    raise ValueError(f"Entity \"{val}\" required by union \"{u.getName()}\" does not exist")

        for new_union in _unions:
            # Find existing union by name (Python sets don't have get, so iterate)
            existing_union: Optional[Union] = None
            for old_u in self.unions:
                 if hasattr(old_u, 'getName') and old_u.getName() == new_union.getName():
                      existing_union = old_u
                      break

            if existing_union:
                # Union with same name exists
                if new_union.getDomain() == existing_union.getDomain():
                     # This check might be too strict if merging within the same domain is allowed.
                     # Java's Optional/filter logic might implicitly handle this differently.
                     # Let's assume duplicate names in the same domain are errors for now.
                     print(f"Warning: Duplicate Union definition found: \"{new_union.getName()}\" in domain \"{new_union.getDomain()}\". Skipping addition.")
                     # raise ValueError(f"Duplicate Union: \"{new_union.getName()}\" in domain \"{new_union.getDomain()}\"")
                else:
                     # Different domain - merge values (Java logic)
                     print(f"Merging union '{new_union.getName()}' from domain '{new_union.getDomain()}' into existing from '{existing_union.getDomain()}'")
                     if hasattr(existing_union, 'setDomain') : existing_union.setDomain(new_union.getDomain()) # Update domain? Java does this.
                     if hasattr(existing_union, 'getValues') and hasattr(existing_union.getValues(), 'update'):
                         existing_union.getValues().update(new_union.getValues())
            else:
                # New union, add it
                self.unions.add(new_union)

    def addEntity(self, entity: Entity) -> None:
        """Adds a top-level entity to the domain, replacing any existing top-level entity with the same name."""
        if not isinstance(entity, Entity) or not hasattr(entity, 'getName'):
             raise TypeError("Input must be an Entity object with a getName method.")

        # Find existing top-level entity by name
        existing_entity: Optional[Entity] = None
        top_entities = self.getTopEntities() # Get current top entities
        for e in top_entities:
            if hasattr(e, 'getName') and e.getName() == entity.getName():
                existing_entity = e
                break

        if existing_entity:
            print(f"Replacing existing top-level entity '{entity.getName()}'")
            # Remove the old entity from the entityTree's children
            if hasattr(self.entityTree, 'removeChild'):
                 try:
                      self.entityTree.removeChild(existing_entity)
                 except ValueError:
                      print(f"Warning: Could not find entity '{existing_entity.getName()}' in entityTree children during replacement.")
            elif hasattr(self.entityTree, 'getChildren') and isinstance(self.entityTree.getChildren(), list):
                 try:
                      self.entityTree.getChildren().remove(existing_entity)
                 except ValueError:
                      print(f"Warning: Could not remove entity '{existing_entity.getName()}' from entityTree children list during replacement.")
            else:
                 print("Warning: Cannot remove existing entity. EntityTree lacks removeChild method or mutable getChildren list.")
            # Detach old entity? Java doesn't explicitly detach here.
            # if hasattr(existing_entity, 'setParent'): existing_entity.setParent(None)

        # Add the new entity as a child of the root entityTree
        if hasattr(self.entityTree, 'addChild'):
            self.entityTree.addChild(entity)
            # Java also sets parent explicitly, assume addChild does this or do it manually
            # if hasattr(entity, 'setParent'): entity.setParent(self.entityTree)
        else:
            print("Warning: Cannot add entity. EntityTree lacks addChild method.")


    def addRelationship(self, relationship: Relationship) -> None:
        """Adds a top-level relationship to the domain, replacing any existing top-level relationship with the same name."""
        if not isinstance(relationship, Relationship) or not hasattr(relationship, 'getName'):
            raise TypeError("Input must be a Relationship object with a getName method.")

        # Find existing top-level relationship by name
        existing_rel: Optional[Relationship] = None
        top_relationships = self.getTopRelationships() # Get current top relationships
        for r in top_relationships:
            if hasattr(r, 'getName') and r.getName() == relationship.getName():
                existing_rel = r
                break

        if existing_rel:
            print(f"Replacing existing top-level relationship '{relationship.getName()}'")
            # Remove the old relationship from the relationshipTree's children
            if hasattr(self.relationshipTree, 'removeChild'):
                 try:
                      self.relationshipTree.removeChild(existing_rel)
                 except ValueError:
                      print(f"Warning: Could not find relationship '{existing_rel.getName()}' in relationshipTree children during replacement.")
            elif hasattr(self.relationshipTree, 'getChildren') and isinstance(self.relationshipTree.getChildren(), list):
                 try:
                      self.relationshipTree.getChildren().remove(existing_rel)
                 except ValueError:
                      print(f"Warning: Could not remove relationship '{existing_rel.getName()}' from relationshipTree children list during replacement.")
            else:
                 print("Warning: Cannot remove existing relationship. RelationshipTree lacks removeChild method or mutable getChildren list.")
            # Detach old relationship?
            # if hasattr(existing_rel, 'setParent'): existing_rel.setParent(None)

        # Add the new relationship as a child of the root relationshipTree
        if hasattr(self.relationshipTree, 'addChild'):
            self.relationshipTree.addChild(relationship)
            # Java also sets parent explicitly, assume addChild does this or do it manually
            # if hasattr(relationship, 'setParent'): relationship.setParent(self.relationshipTree)
        else:
             print("Warning: Cannot add relationship. RelationshipTree lacks addChild method.")


    def _parseRelationships(self, parentNode: ET.Element, root: Relationship, domainName: str) -> None:
        """
        Recursively parses <relationship> tags under parentNode.
        Internal helper for Java's private void parseRelationships(Node parentNode, Relationship root, String domainName).
        """
        # Determine allowed children based on whether we are at the top <relationships> tag or nested
        is_top_level = (root == self.relationshipTree)
        allowed_children = ["relationship"] if is_top_level else ["relationship", "attribute", "reference"]
        valid_rel_attrs = ["name", "inverse", "description", "abstract", "notes"] # Added notes based on Java code

        relationship_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == "relationship"]

        for rel_node in relationship_nodes:
             # Validate allowed children in this context (Java does this implicitly)
             # We validate the rel_node itself against allowed tags in its parent context
             # self._validateTag(rel_node, allowed_children) # This seems wrong, validate children of rel_node later

             self._validateTagAttributes(rel_node, valid_rel_attrs, "name") # Validate attributes of <relationship>

             rel_name = rel_node.get("name")
             rel_inverse = rel_node.get("inverse")
             description = rel_node.get("description")
             notes = rel_node.get("notes") # Get notes attribute
             is_abstract_str = rel_node.get("abstract", "false") # Default to false if missing
             is_abstract = is_abstract_str.lower() == "true"

             if not rel_name or not rel_inverse:
                  raise ValueError("<relationship> tag requires 'name' and 'inverse' attributes.")

             # Find existing relationship anywhere in the tree first (Java logic)
             # Assuming findInTree searches the entire relationshipTree from its root
             existing_relationship = self.findInTree(self.relationshipTree, rel_name)
             current_relationship: Optional[Relationship] = None

             if existing_relationship and isinstance(existing_relationship, Relationship):
                  # Relationship already exists somewhere
                  existing_parent = existing_relationship.getParent() if hasattr(existing_relationship, 'getParent') else None
                  # Check if the found relationship's parent is an ancestor of the current root OR if the parent is the absolute root
                  # AND if the domain is different (indicating it came from an import)
                  is_ancestor = False
                  if existing_parent and hasattr(root, 'hasAncestor') and hasattr(existing_parent, 'getName'):
                       is_ancestor = root.hasAncestor(existing_parent.getName())

                  is_different_domain = False
                  if hasattr(existing_relationship, 'getDomain'):
                       is_different_domain = existing_relationship.getDomain() != domainName

                  if (is_ancestor or existing_parent == self.relationshipTree) and is_different_domain:
                       print(f"Detaching and moving relationship '{rel_name}' from '{existing_parent.getName() if existing_parent else 'root'}' (domain: {existing_relationship.getDomain()}) to '{root.getName()}' (domain: {domainName})")
                       if hasattr(existing_relationship, 'detach'):
                            existing_relationship.detach() # Remove from old parent
                       else:
                            print(f"Warning: Cannot detach existing relationship '{rel_name}'. Detach method missing.")
                       if hasattr(root, 'addChild'):
                            root.addChild(existing_relationship) # Add to new parent (sets parent)
                       else:
                            print(f"Warning: Cannot add child relationship '{rel_name}'. AddChild method missing.")
                       current_relationship = existing_relationship
                  elif existing_parent == root:
                       # Already in the correct place, just update properties
                       print(f"Updating existing relationship '{rel_name}' under parent '{root.getName()}'")
                       current_relationship = existing_relationship
                  else:
                       # Inconsistency: Found elsewhere but not in a compatible import/parent situation
                       parent_name = existing_parent.getName() if existing_parent and hasattr(existing_parent, 'getName') else 'root'
                       root_name = root.getName() if hasattr(root, 'getName') else 'unknown'
                       raise ValueError(f"Inconsistency: Relationship '{rel_name}' found under unexpected parent '{parent_name}'. Cannot automatically move to '{root_name}'.")
             else:
                  # Relationship is new, create it
                  print(f"Creating new relationship '{rel_name}' under parent '{root.getName()}'")
                  # Assuming Relationship constructor
                  current_relationship = Relationship(domain=domainName, name=rel_name, inverse=rel_inverse)
                  if hasattr(root, 'addChild'):
                       root.addChild(current_relationship) # Adds to children and sets parent
                  else:
                       print(f"Warning: Cannot add child relationship '{rel_name}'. AddChild method missing.")


             # Update properties of the (potentially existing or new) relationship
             if current_relationship:
                  if hasattr(current_relationship, 'setDomain'): current_relationship.setDomain(domainName) # Overwrite domain like Java
                  if hasattr(current_relationship, 'setDescription'): current_relationship.setDescription(description or "") # Use empty string if None
                  if hasattr(current_relationship, 'setAbstract'): current_relationship.setAbstract(is_abstract)
                  if hasattr(current_relationship, 'setNotes'): current_relationship.setNotes(notes or "") # Use empty string if None

                  # Add attributes defined directly within this <relationship> tag
                  # Need to filter children of rel_node for <attribute> tags
                  direct_attributes = self._readAttributes(rel_node) # readAttributes should filter for <attribute>
                  if hasattr(current_relationship, 'addAttributes'):
                       current_relationship.addAttributes(direct_attributes) # Add new attributes
                  else:
                       print(f"Warning: Cannot add attributes to relationship '{rel_name}'. addAttributes method missing.")


                  # Parse references defined directly within this <relationship> tag
                  # Need to filter children of rel_node for <reference> tags
                  self._parseReferences(rel_node, current_relationship)

                  # Recursively parse sub-relationships
                  self._parseRelationships(rel_node, current_relationship, domainName)
             else:
                  # This case should ideally not happen if logic above is correct
                  print(f"Error: Failed to get or create relationship '{rel_name}'")


    def _parseReferences(self, parentNode: ET.Element, relation: Relationship) -> None:
        """
        Parses the references from the given parent node (<relationship>) and adds them to the specified relationship.
        Internal helper for Java's private void parseReferences(Node parentNode, Relationship relation).
        """
        if not hasattr(relation, 'getName') or not hasattr(relation, 'addReference'):
             print(f"Warning: Cannot parse references for relation. Missing getName or addReference method.")
             return

        relation_name = relation.getName()
        valid_ref_children = ["reference"] # Children of <relationship> can be <reference>
        valid_ref_attrs = ["subject", "object"]
        # Attributes within reference (<attribute>) are handled by readAttributes
        # valid_attr_attrs = ["name", "datatype", "description", "mandatory",
        #                     "distinguishing", "display", "target", "notes"]

        for ref_node in parentNode.findall("reference"):
             # self._validateTag(ref_node, valid_ref_children) # Already filtered by findall
             self._validateTagAttributes(ref_node, valid_ref_attrs, "") # Validate reference attributes

             subject = ref_node.get("subject")
             object_ref = ref_node.get("object") # Renamed variable to avoid conflict with keyword

             if not subject or not object_ref:
                  raise ValueError("<reference> tag requires 'subject' and 'object' attributes.")

             # Add subject/object to global lists if not present (Java logic)
             if subject not in self.subjects:
                  self.subjects.append(subject)
                  # Java sorts later, Python sorts at the end of _loadFile

             if object_ref not in self.objects:
                  self.objects.append(object_ref)
                  # Java sorts later

             # Create Reference object (Assuming Reference constructor)
             ref = Reference(subject=subject, object=object_ref)

             # Read attributes specific to this reference (Java: ref.setAttributes(readAttributes(node)))
             # Attributes can be children of <reference>
             ref_attributes = self._readAttributes(ref_node) # readAttributes filters for <attribute>
             if ref_attributes and hasattr(ref, 'setAttributes'):
                  ref.setAttributes(ref_attributes) # Assuming setAttributes takes a list
             elif ref_attributes:
                  print(f"Warning: Cannot set attributes on reference {subject}-{object_ref}. setAttributes method missing.")


             # Add reference to the relationship (Java: relation.addReference(ref))
             relation.addReference(ref) # Assuming addReference handles internal storage

             # Update helper dictionaries and sets (Java logic)
             self.nRelRefs += 1
             subj_rel_obj_str = f"{subject}.{relation_name}.{object_ref}"
             self.subjRelObjs.add(subj_rel_obj_str) # Python set is unordered

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
        Recursively parses <entity> tags under parentNode.
        Internal helper for Java's private void parseEntities(Node parentNode, Entity root, String domainName).
        """
        is_top_level = (root == self.entityTree)
        allowed_children = ["entity"] if is_top_level else ["entity", "attribute"]
        valid_entity_attrs = ["name", "description", "abstract", "notes"]

        entity_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == "entity"]

        for entity_node in entity_nodes:
             # self._validateTag(entity_node, allowed_children) # Already filtered
             self._validateTagAttributes(entity_node, valid_entity_attrs, "name") # Validate attributes of <entity>

             entity_name = entity_node.get("name")
             description = entity_node.get("description")
             notes = entity_node.get("notes")
             is_abstract_str = entity_node.get("abstract", "false")
             is_abstract = is_abstract_str.lower() == "true"

             if not entity_name:
                  raise ValueError("<entity> tag requires a 'name' attribute.")

             # Find existing entity anywhere in the tree first (Java logic)
             # Use the instance method findInTree
             existing_entity = self.findInTree(self.entityTree, entity_name)
             current_entity: Optional[Entity] = None

             if existing_entity:
                  # Entity already exists somewhere
                  existing_parent = existing_entity.getParent() if hasattr(existing_entity, 'getParent') else None

                  is_ancestor = False
                  if existing_parent and hasattr(root, 'hasAncestor') and hasattr(existing_parent, 'getName'):
                       is_ancestor = root.hasAncestor(existing_parent.getName())

                  is_different_domain = False
                  if hasattr(existing_entity, 'getDomain'):
                       is_different_domain = existing_entity.getDomain() != domainName

                  if (is_ancestor or existing_parent == self.entityTree) and is_different_domain:
                       print(f"Detaching and moving entity '{entity_name}' from '{existing_parent.getName() if existing_parent else 'root'}' (domain: {existing_entity.getDomain()}) to '{root.getName()}' (domain: {domainName})")
                       if hasattr(existing_entity, 'detach'):
                            existing_entity.detach()
                       else:
                            print(f"Warning: Cannot detach existing entity '{entity_name}'. Detach method missing.")
                       if hasattr(root, 'addChild'):
                            root.addChild(existing_entity) # Add to new parent
                       else:
                            print(f"Warning: Cannot add child entity '{entity_name}'. AddChild method missing.")

                       current_entity = existing_entity
                  elif existing_parent == root:
                       print(f"Updating existing entity '{entity_name}' under parent '{root.getName()}'")
                       current_entity = existing_entity
                  else:
                       parent_name = existing_parent.getName() if existing_parent and hasattr(existing_parent, 'getName') else 'root'
                       root_name = root.getName() if hasattr(root, 'getName') else 'unknown'
                       raise ValueError(f"Inconsistency: Entity '{entity_name}' found under unexpected parent '{parent_name}'. Cannot automatically move to '{root_name}'.")
             else:
                  # Entity is new, create it (Java: new Entity(entityName, domainName))
                  print(f"Creating new entity '{entity_name}' under parent '{root.getName()}'")
                  current_entity = Entity(name=entity_name, domain=domainName) # Assuming constructor
                  if hasattr(root, 'addChild'):
                       root.addChild(current_entity) # Adds to children and sets parent
                  else:
                       print(f"Warning: Cannot add child entity '{entity_name}'. AddChild method missing.")


             # Update properties
             if current_entity:
                  if hasattr(current_entity, 'setDomain'): current_entity.setDomain(domainName) # Overwrite domain like Java
                  if hasattr(current_entity, 'setDescription'): current_entity.setDescription(description or "")
                  if hasattr(current_entity, 'setAbstract'): current_entity.setAbstract(is_abstract)
                  if hasattr(current_entity, 'setNotes'): current_entity.setNotes(notes or "")

                  # Add attributes defined directly within this <entity> tag
                  direct_attributes = self._readAttributes(entity_node) # readAttributes filters for <attribute>
                  if hasattr(current_entity, 'addAttributes'):
                       current_entity.addAttributes(direct_attributes)
                  else:
                       print(f"Warning: Cannot add attributes to entity '{entity_name}'. addAttributes method missing.")


                  # Recursively parse sub-entities
                  self._parseEntities(entity_node, current_entity, domainName)
             else:
                  print(f"Error: Failed to get or create entity '{entity_name}'")


    def _parseImports(self, folder: Path, importsNode: ET.Element) -> None:
        """
        Parses the imports from the <imports> tag, loads imported files recursively (DFS),
        and handles the <deleted> section.
        Internal helper for Java's private void parseImports(File folder, Node importsNode).
        """
        valid_import_children = ["import", "deleted"]
        valid_import_attrs = ["schema"]
        valid_deleted_children = ["entity", "relationship"]
        valid_deleted_item_attrs = ["name"]

        children = [child for child in importsNode if isinstance(child.tag, str)] # Filter comments/PIs
        import_nodes: List[ET.Element] = []
        deleted_node: Optional[ET.Element] = None

        # Separate import and deleted nodes, validate structure (Java logic)
        for i, child in enumerate(children):
             self._validateTag(child, valid_import_children)
             if child.tag == "import":
                  if deleted_node is not None:
                       raise ValueError("<import> tag cannot appear after <deleted> tag within <imports>.")
                  self._validateTagAttributes(child, valid_import_attrs, "schema")
                  import_nodes.append(child)
             elif child.tag == "deleted":
                  if deleted_node is not None:
                       # Java doesn't explicitly check for multiple <deleted> tags
                       print("Warning: Multiple <deleted> tags found within <imports>. Only the last one might be processed based on Java loop structure.")
                  if i != len(children) - 1:
                       # Java check: IntStream.range(0, nodes.size()-1).filter(i->nodes.get(i).getNodeName().equals("deleted"))...
                       raise ValueError("<deleted> tag must be the last child of <imports>.")
                  # No attributes expected on <deleted> itself
                  self._validateTagAttributes(child, [], "")
                  deleted_node = child # Keep track of the (last) deleted node

        # Process imports first (DFS)
        for import_node in import_nodes:
            schema_path_str = import_node.get("schema")
            if not schema_path_str:
                 raise ValueError("<import> tag requires a 'schema' attribute.")

            # Resolve import path (Java logic: check "/", else use folder)
            import_file_path: Path
            # Use absolute path for reliable checking and loading
            # Check if schema_path_str is already absolute or contains separators
            # Use .gbr extension like Java
            if Path(schema_path_str).is_absolute() or "/" in schema_path_str or os.path.sep in schema_path_str:
                 import_file_path = Path(schema_path_str)
                 # Ensure .gbr extension? Java seems to assume it's there. Add if missing.
                 if not import_file_path.name.endswith(".gbr"):
                      import_file_path = import_file_path.with_suffix(".gbr")

            else:
                 # Relative path (likely just domain name), resolve against the folder of the *current* file
                 import_file_path = folder / (schema_path_str + ".gbr") # TODO: Java in this case uses still .gbs, but it seems wrong since for this class we always used .gbr

            abs_import_path_str = str(import_file_path.resolve())

            # Avoid reloading files already processed
            if abs_import_path_str not in self.importedFiles:
                 print(f"Importing: {abs_import_path_str}")
                 self.importedFiles.append(abs_import_path_str) # Track import
                 try:
                      imported_doc = self._parseFile(import_file_path)
                      # Recursively load the imported file (Java passes absolute path)
                      self._loadFile(imported_doc, abs_import_path_str)
                 except FileNotFoundError:
                      print(f"Error: Imported file not found: {import_file_path}")
                      raise # Re-raise to stop the loading process
                 except Exception as e:
                      print(f"Error loading imported file {import_file_path}: {e}")
                      traceback.print_exc()
                      raise # Re-raise
            else:
                 print(f"Skipping already imported file: {abs_import_path_str}")

        # Process deleted items after all imports are done (Java logic)
        if deleted_node is not None:
            for deleted_item in deleted_node:
                 if not isinstance(deleted_item.tag, str): continue # Skip comments/PIs
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
        """
        Parses the <user-types> section.
        Internal helper for Java's private void parseTypes(File webInf, Node typesNode).
        """
        try:
            # readAttributes expects a parent node containing <attribute> children
            attributes_read = self._readAttributes(typesNode)
            self.types = self._fromAttributesToTypes(attributes_read) # Java uses Vector
            print(f"Parsed {len(self.types)} user types.")
        # Java catches CloneNotSupportedException, Python might raise AttributeError or TypeError during clone
        except (AttributeError, TypeError, ValueError, Exception) as e:
            print(f"Error parsing user types: {e}")
            traceback.print_exc() # Java prints stack trace

    def _fromAttributesToTypes(self, attributes: List[Attribute]) -> List[Attribute]:
        """Converts a list of Attribute objects to a list of types (Attributes)."""
        # In Java, this seemed to involve casting to UType, but the return type was Vector<Attribute>.
        # For Python, if UType is not a distinct class, just return the list.
        # If UType is distinct and inherits Attribute, casting might be needed if specific UType methods are used later.
        # For now, assume a direct return is sufficient.
        return list(attributes) # Return a copy

    def _substitute(self, fileToModify: Path, entityToRemove: str, entityToAddNode: ET.Element) -> None:
        """
        Substitutes an entity in an XML file. (Complex and potentially unsafe disk operation)
        Internal helper for Java's private void substitute(File fileToModify, String entityToRemove, Node entityToAdd).
        """
        print(f"Attempting to substitute '{entityToRemove}' in file '{fileToModify}'")
        try:
            # 1. Parse the target XML file
            tree = self._parseFile(fileToModify)
            root = tree.getroot()

            # 2. Find the entity node to remove and its parent
            # ET doesn't have easy parent pointers. We need to search.
            parent_map = {c: p for p in root.iter() for c in p} # Build parent map (can be slow for large files)
            entity_to_replace_node: Optional[ET.Element] = None
            parent_of_entity_to_replace: Optional[ET.Element] = None

            # Find the entity node iteratively
            queue = [root]
            found_node = None
            while queue:
                current_node = queue.pop(0)
                if current_node.tag == 'entity' and current_node.get('name') == entityToRemove:
                    entity_to_replace_node = current_node
                    parent_of_entity_to_replace = parent_map.get(current_node)
                    break
                queue.extend(list(current_node)) # Add children to queue

            if entity_to_replace_node is None or parent_of_entity_to_replace is None:
                print(f"Error: Entity '{entityToRemove}' not found in {fileToModify}. Substitution failed.")
                return

            # 3. Clone the entity node to add (using deepcopy)
            try:
                 new_entity_node = copy.deepcopy(entityToAddNode)
            except Exception as e:
                 print(f"Error: Could not deep copy the entity node to add: {e}. Substitution failed.")
                 return

            # 4. Remove old node and insert new node
            try:
                 # Find index for insertion
                 children_list = list(parent_of_entity_to_replace)
                 index = children_list.index(entity_to_replace_node)
                 parent_of_entity_to_replace.remove(entity_to_replace_node)
                 parent_of_entity_to_replace.insert(index, new_entity_node)
                 print(f"Successfully substituted '{entityToRemove}' in {fileToModify}")
            except ValueError:
                 print(f"Error: Node '{entityToRemove}' not found in its supposed parent during substitution. Appending instead.")
                 # Fallback: just append if index fails? Java might error out.
                 parent_of_entity_to_replace.remove(entity_to_replace_node) # Ensure removal first
                 parent_of_entity_to_replace.append(new_entity_node)

            # 5. Save the modified XML
            self._saveXML(tree, fileToModify)

        except Exception as e:
            print(f"Error during entity substitution in {fileToModify}: {e}")
            traceback.print_exc()

    def _saveXML(self, doc: ET.ElementTree, fileToSave: Path) -> None:
        """Saves the ElementTree to the specified file path."""
        try:
            # ET.indent(doc.getroot()) # Optional: Pretty print (requires Python 3.9+)
            doc.write(fileToSave, encoding='utf-8', xml_declaration=True)
            print(f"Saved XML to {fileToSave}")
        except Exception as e:
            print(f"Error saving XML to {fileToSave}: {e}")
            traceback.print_exc()
            raise

    def _clone(self, nodeToClone: ET.Element) -> ET.Element:
         """
         Clones an XML element using deepcopy.
         Roughly corresponds to Java's private Node clone(Document docToModify, Node entityToAdd).
         Note: Java's clone is more complex, handling document context. ET deepcopy is simpler.
         """
         try:
              # Using copy.deepcopy is generally the most Pythonic way for element cloning
              cloned_node = copy.deepcopy(nodeToClone)
              return cloned_node
         except Exception as e:
              print(f"Error cloning node <{nodeToClone.tag}>: {e}")
              raise # Re-raise the error

    def _cloneAttributes(self, attributesNode: ET.Element) -> ET.Element:
        """
        Clones an <attributes> element and its children using deepcopy.
        Internal helper for Java's private Element cloneAttributes(Document docToModify, Node attributesToAdd).
        """
        # In Python ET, deepcopy handles children automatically.
        return self._clone(attributesNode)

    def _cloneValues(self, valuesNode: ET.Element) -> ET.Element:
        """
        Clones a <values> or <taxonomy> element and its children recursively using deepcopy.
        Internal helper for Java's private Element cloneValues(Document docToModify, Node valuesToAdd).
        """
        # In Python ET, deepcopy handles children automatically.
        return self._clone(valuesNode)

    def _readAttributes(self, parentNode: ET.Element) -> List[Attribute]: # Java returns Vector
        """
        Reads attributes defined as <attribute> children of the parentNode.
        Handles different datatypes (string, select, tree, entity, user-types).
        Internal helper for Java's private Vector<Attribute> readAttributes(Node parentNode).
        """
        fullAttrs: List[Attribute] = []
        # Java valid attributes: "name","datatype","description","mandatory","distinguishing","display","target","notes"
        valid_attr_attrs = ["name", "datatype", "description", "mandatory",
                            "distinguishing", "display", "target", "notes"]

        attribute_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == "attribute"]

        for attr_node in attribute_nodes:
            self._validateTagAttributes(attr_node, valid_attr_attrs, "name")

            attr_name = attr_node.get("name")
            # Java defaults datatype to "" if not present, let's default to "string" for clarity
            data_type = attr_node.get("datatype", "string")
            description = attr_node.get("description", "") # Default to empty string like Java
            notes = attr_node.get("notes") # Get notes (present in Java code)

            if not attr_name:
                 raise ValueError("<attribute> tag requires a 'name' attribute.")

            # Initialize attribute (Java: new Attribute(attribute,datatype))
            # Assuming Attribute constructor takes name, data_type
            currentAttr = Attribute(name=attr_name, data_type=data_type)
            if hasattr(currentAttr, 'setDescription'): currentAttr.setDescription(description)
            if notes is not None and hasattr(currentAttr, 'setNotes'): currentAttr.setNotes(notes) # Set notes if present

            # Set optional boolean flags (Java uses setOptionalAttributes helper)
            self._setOptionalAttributes(attr_node.attrib, currentAttr)

            # Handle datatype specific logic (Java switch statement)
            try:
                if data_type == "select":
                    # Java: currentAttr.setValuesString(readValuesList(an,"value",true));
                    values = self._readValuesList(attr_node, "value", True) # Read <value> children, add "Other"
                    if hasattr(currentAttr, 'setValuesString'): # Java uses setValuesString
                         currentAttr.setValuesString(values)
                    elif hasattr(currentAttr, 'setValues'): # Fallback to setValues
                         currentAttr.setValues(values)
                    else:
                         print(f"Warning: Attribute class missing setValuesString/setValues for '{attr_name}'.")
                elif data_type == "tree":
                    # Java: currentAttr.setSubClasses(readValuesTree(an,null));
                    # readValuesTree expects the root of the tree structure (<attribute> or <value>)
                    # It returns a DefaultTreeNode
                    sub_classes_tree = self._readValuesTree(attr_node, None) # Pass None as parent for the root call
                    if hasattr(currentAttr, 'setSubClasses'):
                         currentAttr.setSubClasses(sub_classes_tree) # Assuming setSubClasses takes TreeNode
                    else:
                         print(f"Warning: Attribute class missing setSubClasses for '{attr_name}'.")
                elif data_type == "entity":
                    # Java: currentAttr.setTarget(n.getNamedItem("target").getNodeValue());
                    target = attr_node.get("target")
                    if target is None:
                         raise ValueError("<attribute> with datatype='entity' requires a 'target' attribute.")
                    if hasattr(currentAttr, 'setTarget'):
                         currentAttr.setTarget(target)
                    else:
                         print(f"Warning: Attribute class missing setTarget for '{attr_name}'.")
                elif data_type == "user-types":
                    # Java: String target = n.getNamedItem("target").getNodeValue();
                    target_type_name = attr_node.get("target")
                    if target_type_name is None:
                         raise ValueError("<attribute> with datatype='user-types' requires a 'target' attribute.")

                    # Find the predefined type from self.types
                    found_type = next((t for t in self.types if hasattr(t, 'getName') and t.getName() == target_type_name), None)
                    if found_type:
                         if not hasattr(found_type, 'clone'):
                              raise AttributeError(f"User type '{target_type_name}' does not support cloning.")
                         # Java: currentAttr = (Attribute) type.clone();
                         cloned_type = found_type.clone() # Assumes Attribute.clone() exists and works
                         # Java overrides name, description, and optional flags after cloning
                         if hasattr(cloned_type, 'setName'): cloned_type.setName(attr_name)
                         if hasattr(cloned_type, 'setDescription'): cloned_type.setDescription(description)
                         if notes is not None and hasattr(cloned_type, 'setNotes'): cloned_type.setNotes(notes)
                         self._setOptionalAttributes(attr_node.attrib, cloned_type)
                         currentAttr = cloned_type # Replace the initially created attribute
                    else:
                         raise ValueError(f"Target user type '{target_type_name}' not found for attribute '{attr_name}'. Ensure it's defined in <user-types>.")
                # Add other datatypes (string, int, etc.) if needed - handled by default Attribute init

                fullAttrs.append(currentAttr)
            except Exception as e: # Catch potential clone errors or missing methods
                 print(f"Error processing attribute '{attr_name}' (datatype: {data_type}): {e}")
                 traceback.print_exc()
                 # Decide whether to skip this attribute or re-raise
                 # raise # Re-raise to stop parsing

        return fullAttrs

    def _fromAttributesToString(self, attributes: List[Attribute]) -> List[str]: # Java returns Vector
        """Converts a list of Attribute objects to a list of their names."""
        return [a.getName() for a in attributes if hasattr(a, 'getName')]

    # Java has fromTypesToString(Vector<UType>), but UType seems unused/same as Attribute
    # def _fromTypesToString(self, types: List[UType]) -> List[str]: ...

    def _readValuesList(self, parentNode: ET.Element, tag_name: str, add_other: bool) -> List[str]: # Java returns List
        """
        Reads child elements with tag_name under parentNode and returns their 'name' attributes as a list.
        Internal helper for Java's private List<String> readValuesList(Node parentNode, String tag_name, boolean add_other).
        """
        values: List[str] = []
        valid_value_attrs = ["name"] # Java validates name attribute

        value_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == tag_name]

        for value_node in value_nodes:
             # self._validateTag(value_node, [tag_name]) # Already filtered
             self._validateTagAttributes(value_node, valid_value_attrs, "name") # Java validates attributes
             value_name = value_node.get("name")
             if value_name is not None:
                  values.append(value_name)
             else:
                  raise ValueError(f"<{tag_name}> tag requires a 'name' attribute.")

        if add_other: # Java adds "Other" conditionally
             values.append("Other")
        return values

    def _readValuesTree(self, parentXmlNode: ET.Element, parentTreeNode: Optional[DefaultTreeNode]) -> DefaultTreeNode:
        """
        Recursively parses <value> tags under parentXmlNode to build a DefaultTreeNode structure.
        Internal helper for Java's private DefaultTreeNode readValuesTree(Node parentNode, DefaultTreeNode parent).
        Requires a DefaultTreeNode class implementation.
        """
        # Determine the data for the current TreeNode based on Java logic
        node_data: str
        if parentXmlNode.tag == "attribute":
             # Root of the tree definition (within <attribute datatype="tree">)
             node_data = "- Select one -" # Special root node label from Java
        elif parentXmlNode.tag == "value":
             node_data = parentXmlNode.get("name")
             if node_data is None:
                  raise ValueError("<value> tag within a tree structure requires a 'name' attribute.")
        else:
             raise ValueError(f"Unexpected tag '{parentXmlNode.tag}' encountered in _readValuesTree.")

        # Create the TreeNode for the current XML node
        # Ensure Python DefaultTreeNode constructor handles parent linking or do it manually.
        # Assuming DefaultTreeNode(data, parent) constructor exists and links parent
        try:
            currentTreeNode = DefaultTreeNode(data=node_data, parent=parentTreeNode)
        except NameError:
             raise NotImplementedError("DefaultTreeNode class is not defined or imported.")
        except TypeError:
             raise NotImplementedError("DefaultTreeNode constructor signature mismatch (expected data, parent).")


        valid_value_children = ["value"] # Children of <attribute> or <value> in a tree are <value>
        valid_value_attrs = ["name"] # Java validates name attribute

        value_nodes = [child for child in parentXmlNode if isinstance(child.tag, str) and child.tag == "value"]

        for childXmlNode in value_nodes:
             # self._validateTag(childXmlNode, valid_value_children) # Already filtered
             self._validateTagAttributes(childXmlNode, valid_value_attrs, "name") # Java validates attributes

             # Recursive call to build the subtree
             childTreeNode = self._readValuesTree(childXmlNode, currentTreeNode)
             # If constructor doesn't add child, do it here (assuming add_child method):
             # if hasattr(currentTreeNode, 'add_child'):
             #     currentTreeNode.add_child(childTreeNode)

             # Java code adds an "Other <name>" node if the child has further children (is not a leaf)
             if hasattr(childTreeNode, 'isLeaf') and not childTreeNode.isLeaf():
                  other_node_data = f"Other {childXmlNode.get('name')}"
                  # Java: new DefaultTreeNode("Other " + ..., subtree);
                  # Creates the "Other" node as a child of the *childTreeNode*
                  try:
                       DefaultTreeNode(data=other_node_data, parent=childTreeNode) # Assuming constructor links to parent
                  except NameError:
                       raise NotImplementedError("DefaultTreeNode class is not defined or imported.")
                  except TypeError:
                       raise NotImplementedError("DefaultTreeNode constructor signature mismatch (expected data, parent).")


        return currentTreeNode

    def _addValue(self, map_dict: Dict[str, List[str]], key: str, value: str) -> None:
        """Adds a value to a list within a dictionary, ensuring uniqueness and sorting."""
        current_list = map_dict[key] # Relies on defaultdict(list)
        if value not in current_list:
            current_list.append(value)
            current_list.sort() # Keep sorted like Java's logic with Collections.sort

    def _setOptionalAttributes(self, attrib_map: Dict[str, str], attr_obj: Attribute) -> None:
        """Sets optional boolean attributes on an Attribute object based on XML attributes."""
        # Java uses string "true"/"false". Assume Attribute setters handle bool or string.
        # Prefer bool for Pythonic style if Attribute class supports it.
        is_mandatory = attrib_map.get("mandatory", "false").lower() == "true"
        is_distinguishing = attrib_map.get("distinguishing", "false").lower() == "true"
        is_display = attrib_map.get("display", "false").lower() == "true" # Java uses "display"

        if hasattr(attr_obj, 'setMandatory'): attr_obj.setMandatory(is_mandatory)
        if hasattr(attr_obj, 'setDistinguishing'): attr_obj.setDistinguishing(is_distinguishing)
        if hasattr(attr_obj, 'setDisplay'): attr_obj.setDisplay(is_display)

    # --- Public Methods ---

    def getInverseRel(self, relationship_name: str) -> Optional[str]: # Java returns String
        """Gets the inverse relationship name for the given relationship name."""
        relationship = self.getRelationship(relationship_name)
        if relationship and hasattr(relationship, 'getInverse'):
            return relationship.getInverse()
        return None

    def getDomain(self) -> Optional[str]: # Java returns String
        """Returns the primary domain name associated with this RecordData instance."""
        return self.domain

    def getEntitiesNotRemoved(self, toRemove: Optional[List[str]] = None) -> List[Entity]: # Java returns List, takes ArrayList
        """Returns a list of top-level entities, filtering out those in the optional toRemove list."""
        # Java logic: get top entities, create removal list, removeAll, return result.
        top_entities = list(self.getTopEntities()) # Get a mutable copy
        entities_to_remove_names = toRemove if toRemove is not None else self.removedEntities

        if not entities_to_remove_names:
            return top_entities # No filtering needed

        # Filter based on names
        result = [e for e in top_entities if not (hasattr(e, 'getName') and e.getName() in entities_to_remove_names)]
        return result

    def getAllEntities(self) -> List[Entity]: # Java returns Vector
        """Returns a flat list of all entities in the tree (including sub-entities)."""
        all_entities: List[Entity] = []
        if not hasattr(self.entityTree, 'getChildren'):
             print("Warning: entityTree has no getChildren method.")
             return []

        queue: List[Entity] = list(self.entityTree.getChildren()) # Start with top-level entities
        visited: Set[Entity] = set(queue)

        while queue:
            current = queue.pop(0)
            all_entities.append(current)
            if hasattr(current, 'getChildren'):
                 for child in current.getChildren():
                      if child not in visited:
                           visited.add(child)
                           queue.append(child)
        return all_entities


    def getAllEntitiesToString(self) -> List[str]: # Java returns Vector
        """Returns a flat list of names of all entities in the tree."""
        return [e.getName() for e in self.getAllEntities() if hasattr(e, 'getName')]

    def getRelationship(self, relName: str) -> Optional[Relationship]: # Java returns Relationship
        """Retrieves a relationship by its name by searching the relationship tree."""
        # Java searches top level, then recursively calls helper.
        # Python findInTree already searches recursively from the root.
        found_entity = self.findInTree(self.relationshipTree, relName)
        if found_entity and isinstance(found_entity, Relationship):
            return found_entity
        return None

    # Java has getRelationship(String relName, ArrayList<Relationship> topRels) - Not directly needed if findInTree works from root

    def getAllRelationships(self) -> List[Relationship]: # Java returns List
        """Returns a flat list of all relationships in the tree (including sub-relationships)."""
        all_rels: List[Relationship] = []
        if not hasattr(self.relationshipTree, 'getChildren'):
             print("Warning: relationshipTree has no getChildren method.")
             return []

        # Use a stack for DFS traversal like Java
        stack: List[Relationship] = []
        # Start with top-level relationships
        if hasattr(self.relationshipTree, 'getChildren'):
             top_rels = [child for child in self.relationshipTree.getChildren() if isinstance(child, Relationship)]
             stack.extend(reversed(top_rels)) # Reverse for DFS order matching Java's stack pop

        visited: Set[Relationship] = set(top_rels)

        while stack:
            current = stack.pop()
            all_rels.append(current)
            if hasattr(current, 'getChildren'):
                 # Add children to stack if they are relationships and not visited
                 children_rels = [child for child in current.getChildren() if isinstance(child, Relationship)]
                 for child in reversed(children_rels): # Reverse for DFS order
                      if child not in visited:
                           visited.add(child)
                           stack.append(child)
        return all_rels

    def getAllRelationshipsToString(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of names of all relationships in the tree."""
        names = {r.getName() for r in self.getAllRelationships() if hasattr(r, 'getName')}
        return sorted(list(names)) # Return sorted list to mimic TreeSet ordering

    def _getAllChildren(self, e: Entity) -> List[Entity]: # Java returns Vector (private helper)
        """Recursively gets all children (entities) of a given entity."""
        children_list: List[Entity] = []
        if hasattr(e, 'getChildren'):
            for child in e.getChildren():
                children_list.append(child)
                children_list.extend(self._getAllChildren(child)) # Recursive call
        return children_list

    def _getAllChildrenToString(self, e: Entity) -> List[str]: # Java returns Vector (private helper)
        """Recursively gets names of all children (entities) of a given entity."""
        names_list: List[str] = []
        if hasattr(e, 'getChildren'):
            for child in e.getChildren():
                 if hasattr(child, 'getName'):
                      names_list.append(child.getName())
                 names_list.extend(self._getAllChildrenToString(child)) # Recursive call
        return names_list

    def getTopEntitiesToString(self) -> List[str]: # Java returns Vector
        """Returns a list of names of the top-level entities."""
        return [e.getName() for e in self.getTopEntities() if hasattr(e, 'getName')]

    def getSubjsFromRel(self, relationship_name: str) -> Set[str]: # Java returns TreeSet
        """Gets all unique subjects associated with a given relationship name (including inheritance)."""
        # Java iterates all relationships, finds match, calls r.getSubjects()
        relationship = self.getRelationship(relationship_name)
        if relationship and hasattr(relationship, 'getSubjects'):
            # Assuming Relationship class has getSubjects() that handles inheritance/all references
            try:
                 subjects = relationship.getSubjects() # Should return Set[str] or List[str]
                 return set(subjects) # Ensure it's a set
            except Exception as e:
                 print(f"Warning: Error getting subjects for '{relationship_name}': {e}")
                 return set()
        return set()

    def getObjsFromRel(self, relationship_name: str) -> Set[str]: # Java returns TreeSet
        """Gets all unique objects associated with a given relationship name (including inheritance)."""
        # Java iterates all relationships, finds match, calls r.getObjects()
        relationship = self.getRelationship(relationship_name)
        if relationship and hasattr(relationship, 'getObjects'):
            # Assuming Relationship class has getObjects() that handles inheritance/all references
            try:
                 objects = relationship.getObjects() # Should return Set[str] or List[str]
                 return set(objects) # Ensure it's a set
            except Exception as e:
                 print(f"Warning: Error getting objects for '{relationship_name}': {e}")
                 return set()
        return set()

    def getSubjects(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of all unique subjects found in references."""
        # Java returns new TreeSet<String>(subjects)
        # self.subjects is already populated during parsing
        return sorted(list(set(self.subjects))) # Ensure uniqueness and sort

    def getObjects(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of all unique objects found in references."""
        # Java returns new TreeSet<String>(objects)
        # self.objects is already populated during parsing
        return sorted(list(set(self.objects))) # Ensure uniqueness and sort

    def getSubjObj_Rels(self, subject: str, object_ref: str) -> Set[str]: # Java returns Set
        """Gets the set of relationship names connecting a specific subject to a specific object."""
        # Java: return new HashSet<String>(subjObj_Rels.get(subject + "." + object));
        key = f"{subject}.{object_ref}"
        # Return a copy to prevent external modification
        return set(self.subjObj_Rels.get(key, []))

    # --- Scaraggi Getters/Setters ---

    def getInverseRels(self) -> Dict[str, str]: # Java returns Map
        return self.inverseRels.copy() # Return copy

    def setInverseRels(self, inverseRels: Dict[str, str]) -> None:
        self.inverseRels = inverseRels

    def getRelSubjs(self) -> Dict[str, List[str]]: # Java returns Map<String, Vector<String>>
        # Return a copy with copies of lists
        return {k: list(v) for k, v in self.relSubjs.items()}

    def setRelSubjs(self, relSubjs: Dict[str, List[str]]) -> None: # Java takes Map<String, Vector<String>>
        # Assume input might not be defaultdict, convert if needed
        self.relSubjs = defaultdict(list, {k: list(v) for k, v in relSubjs.items()})

    def getRelObjs(self) -> Dict[str, List[str]]: # Java returns Map<String, Vector<String>>
        return {k: list(v) for k, v in self.relObjs.items()}

    def setRelObjs(self, relObjs: Dict[str, List[str]]) -> None: # Java takes Map<String, Vector<String>>
        self.relObjs = defaultdict(list, {k: list(v) for k, v in relObjs.items()})

    def getAttrsRel(self) -> Dict[str, List[Attribute]]: # Java returns Map<String, Vector<Attribute>>
        return {k: list(v) for k, v in self.attrsRel.items()}

    def setAttrsRel(self, attrsRel: Dict[str, List[Attribute]]) -> None: # Java takes Map<String, Vector<Attribute>>
        self.attrsRel = defaultdict(list, {k: list(v) for k, v in attrsRel.items()})

    def getInverse(self) -> Optional[str]: # Java returns String
        # This seems to be a specific attribute, different from inverseRels map
        return self.inverse

    def setInverse(self, inverse: str) -> None:
        self.inverse = inverse

    def getDomainList(self) -> Optional[List[str]]: # Java returns ArrayList
        return list(self.domainList) if self.domainList is not None else None # Return copy

    def setDomainList(self, domainList: List[str]) -> None: # Java takes ArrayList
        self.domainList = list(domainList) # Store a copy

    def getRelationshipsToString(self, entity_name: str) -> List[Relationship]: # Java returns Vector<Relationship>
        """Retrieves relationships where the given entity name is either subject or object."""
        # Java iterates all relationships, checks subjects/objects sets.
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            # Check direct references (Java uses r.getSubjects().contains(entity) || r.getObjects().contains(entity))
            # Assuming getSubjects/getObjects on Relationship return sets/lists of names for that relationship (potentially including inherited)
            try:
                 subjects = set(rel.getSubjects()) if hasattr(rel, 'getSubjects') else set()
                 objects = set(rel.getObjects()) if hasattr(rel, 'getObjects') else set()
                 if entity_name in subjects or entity_name in objects:
                      includes.append(rel)
            except Exception as e:
                 print(f"Warning: Error checking involvement for '{entity_name}' in '{rel.getName()}': {e}")
        return includes

    def getRelationshipsForSubj(self, entity_name: str) -> List[Relationship]: # Java returns List
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the subject."""
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            try:
                 # Assumes getSubjects checks inheritance if needed by the Relationship class implementation
                 subjects = set(rel.getSubjects()) if hasattr(rel, 'getSubjects') else set()
                 if entity_name in subjects:
                     includes.append(rel)
            except Exception as e:
                 print(f"Warning: Error checking subject involvement for '{entity_name}' in '{rel.getName()}': {e}")
        return includes

    def getRelationshipsForObj(self, entity_name: str) -> List[Relationship]: # Java returns List
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the object."""
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            try:
                 # Assumes getObjects checks inheritance if needed by the Relationship class implementation
                 objects = set(rel.getObjects()) if hasattr(rel, 'getObjects') else set()
                 if entity_name in objects:
                     includes.append(rel)
            except Exception as e:
                 print(f"Warning: Error checking object involvement for '{entity_name}' in '{rel.getName()}': {e}")
        return includes

    def getImportedFiles(self) -> List[str]: # Java returns List
        """Returns the list of absolute paths of imported .gbr files."""
        return list(self.importedFiles) # Return copy

    def getEntity(self, entityName: str) -> Optional[Entity]: # Java returns Entity
        """Retrieves an entity by its name by searching the entity tree."""
        # Java implementation uses findInTree starting from root
        return self.findInTree(self.entityTree, entityName)

    # Java has getSubEntity - seems redundant if findInTree works from root
    # def getSubEntity(self, entities: List[Entity], entityName: str) -> Optional[Entity]: ...

    def removeEntities(self, entities: List[Entity]) -> None: # Java takes List<Entity>
        """Removes entities if their domain does not match the main domain."""
        # Java logic seems flawed: it removes entities from the *input list* if their domain *doesn't* match.
        # It doesn't actually remove them from the tree structure.
        # Let's implement the Java logic as described, though it might not be useful.
        # A more useful implementation would remove entities from the tree.
        entities_to_remove_from_input_list = []
        for e in entities:
             if hasattr(e, 'getDomain') and e.getDomain() != self.domain:
                  # This removal affects the list passed *in*, not the internal tree
                  # entities.remove(e) # Modifying list while iterating is bad
                  entities_to_remove_from_input_list.append(e)

        for e_rem in entities_to_remove_from_input_list:
             try:
                  entities.remove(e_rem)
             except ValueError:
                  pass # Should not happen if e_rem came from entities
        print(f"Note: removeEntities only modified the input list based on domain mismatch, did not alter the internal tree.")


    def removeRelationships(self, domainToRemove: str) -> None:
        """Removes all relationships belonging to a specific domain."""
        # Java finds all relationships, filters by domain, then calls removeRelationship for each.
        rels_to_remove = [r for r in self.getAllRelationships() if hasattr(r, 'getDomain') and r.getDomain() == domainToRemove]
        print(f"Removing {len(rels_to_remove)} relationships belonging to domain: {domainToRemove}")
        for r in rels_to_remove:
            if hasattr(r, 'getName'):
                 self.removeRelationship(r.getName()) # Call the existing remove method
            else:
                 print(f"Warning: Cannot remove relationship without a name: {r}")


    def findInTree(self, parent: Entity, childEntityName: str) -> Optional[Entity]:
        """
        Finds the entity with the given name in the tree starting from parent, exploring it in DFS order.
        """
        if not hasattr(parent, 'getChildren'):
             return None # Cannot search if parent has no children method

        # Use a stack for iterative DFS to avoid deep recursion issues
        stack: List[Entity] = list(parent.getChildren()) # Start with direct children
        visited: Set[Entity] = set(stack)

        while stack:
            current_entity = stack.pop() # LIFO for DFS

            # Check if current entity matches
            if hasattr(current_entity, 'getName') and current_entity.getName().lower() == childEntityName.lower():
                 return current_entity

            # Add children to stack if not visited
            if hasattr(current_entity, 'getChildren'):
                 children = current_entity.getChildren()
                 # Add children in reverse order so the first child is processed first
                 for child in reversed(children):
                      if child not in visited:
                           visited.add(child)
                           stack.append(child)
        return None # Not found

    def getnTopEntities(self) -> int:
        """Returns the number of top-level entities."""
        if hasattr(self.entityTree, 'getChildren'):
             return len(self.entityTree.getChildren())
        return 0

    def getnSubEntities(self) -> int:
        """Returns the number of non-top-level entities."""
        # Java: getAllEntitiesToString().size()-getnTopEntities();
        # Note: getAllEntitiesToString includes top-level entities.
        # Re-implement to count directly for efficiency if needed, or use Java's logic:
        return len(self.getAllEntitiesToString()) - self.getnTopEntities()

    def getnTopRels(self) -> int:
        """Returns the number of top-level relationships."""
        if hasattr(self.relationshipTree, 'getChildren'):
             # Filter for actual Relationship instances
             return len([c for c in self.relationshipTree.getChildren() if isinstance(c, Relationship)])
        return 0

    def getnRelRefs(self) -> int:
        """Returns the total number of relationship references parsed."""
        return self.nRelRefs

    @staticmethod
    def readFile(path: str, encoding: str = 'utf-8') -> str: # Java takes Charset
        """Reads a file and returns its content as a string."""
        # Java uses Files.readAllBytes and new String(bytes, encoding)
        try:
            # Use Path object for better path handling
            file_path = Path(path)
            # Use read_text for simplicity
            return file_path.read_text(encoding=encoding)
        except FileNotFoundError:
            print(f"Error: File not found at path {path}")
            raise # Re-raise FileNotFoundError
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            raise # Re-raise other errors (e.g., UnicodeDecodeError, IOError)

    def getRelationshipsWithSubj(self, subject: str) -> Set[str]: # Java returns TreeSet
        """Retrieves the names of top-level relationships involving the subject (or its subclasses)."""
        relationships: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject) # Find entity for inheritance check

        for rel in self.getAllRelationships():
            if not hasattr(rel, 'getReferences') or not hasattr(rel, 'getTop') or not hasattr(rel, 'getName'): continue

            for ref in rel.getReferences():
                 if not hasattr(ref, 'getSubject'): continue
                 ref_subject = ref.getSubject()

                 # Java check: ref.getSubject().equals(subject) || findInTree(subjEntity, ref.getSubject())!=null
                 # This means: is the ref subject the exact subject OR a descendant of the subject?
                 is_match = ref_subject.lower() == subject.lower()
                 if not is_match and subj_entity:
                      # Check if ref.getSubject() is a descendant of subj_entity
                      descendant_check = self.findInTree(subj_entity, ref_subject)
                      is_match = descendant_check is not None

                 if is_match:
                      try:
                           top_rel_name = rel.getTop() # Assumes getTop returns the name of the top-level ancestor
                           relationships.add(top_rel_name)
                      except Exception as e:
                           print(f"Warning: Error getting top relationship for '{rel.getName()}': {e}. Using relationship name itself.")
                           relationships.add(rel.getName())
                      break # Found one match for this relationship, move to next rel

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(relationships))
        return relationships

    def getRelationshipsWithObj(self, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves the names of top-level relationships involving the object (or its subclasses)."""
        relationships: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref) # Find entity for inheritance check

        for rel in self.getAllRelationships():
            if not hasattr(rel, 'getReferences') or not hasattr(rel, 'getTop') or not hasattr(rel, 'getName'): continue

            for ref in rel.getReferences():
                 if not hasattr(ref, 'getObject'): continue
                 ref_object = ref.getObject()

                 # Java check: ref.getObject().equals(object) || findInTree(objEntity, object)!=null
                 is_match = ref_object.lower() == object_ref.lower()
                 if not is_match and obj_entity:
                      # Check if ref.getObject() is a descendant of obj_entity
                      descendant_check = self.findInTree(obj_entity, ref_object)
                      is_match = descendant_check is not None

                 if is_match:
                      try:
                           top_rel_name = rel.getTop() # Assumes getTop returns the name of the top-level ancestor
                           relationships.add(top_rel_name)
                      except Exception as e:
                           print(f"Warning: Error getting top relationship for '{rel.getName()}': {e}. Using relationship name itself.")
                           relationships.add(rel.getName())
                      break # Found one match for this relationship, move to next rel

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(relationships))
        return relationships

    def getObjsFromRel(self, relationships: List[str]) -> List[str]: # Java returns Vector
        """Retrieves unique objects from a list of relationship names."""
        # Java uses TreeSet to collect unique objects, then returns Vector
        objects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel and hasattr(rel, 'getReferences'):
                # Java iterates only direct references in this version
                for ref in rel.getReferences():
                     if hasattr(ref, 'getObject'):
                          objects_set.add(ref.getObject())
                # If inheritance is needed here (like in getObjsFromRel(String)), the logic would be different.
                # Based on Java code, it seems only direct references are considered in this overload.

        return sorted(list(objects_set)) # Return sorted list to mimic TreeSet -> Vector

    def getSubjsFromRel(self, relationships: List[str]) -> List[str]: # Java returns Vector
        """Retrieves unique subjects from a list of relationship names."""
        # Java uses HashSet to collect unique subjects, then returns Vector
        subjects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel and hasattr(rel, 'getReferences'):
                # Java iterates only direct references in this version
                for ref in rel.getReferences():
                     if hasattr(ref, 'getSubject'):
                          subjects_set.add(ref.getSubject())
                # If inheritance is needed, logic would differ. Java code suggests direct refs only.

        return sorted(list(subjects_set)) # Return sorted list

    def getObjsFromSubjRel(self, subject: str, relName: str) -> Set[str]: # Java returns TreeSet
     """
     Retrieves objects related to a subject via DIRECT references
     in a specific relationship (considering subject inheritance).
     Corrected to match Java logic (no relationship hierarchy traversal).
     """
     objects_set: Set[str] = set()
     subj_entity = self.findInTree(self.entityTree, subject) # Find entity for inheritance check
     rel = self.getRelationship(relName) # Get the specific relationship

     if not rel:
          print(f"Warning: Relationship '{relName}' not found in getObjsFromSubjRel.")
          return set()

     # --- Correction: Only iterate direct references of 'rel' ---
     try:
          direct_references = rel.getReferences() # Assume this returns List[Reference]
     except AttributeError:
          print(f"Warning: Relationship class missing 'getReferences' for '{relName}'. Cannot get objects.")
          return set()
     # --- End Correction ---

     for ref in direct_references: # Iterate only direct references
          if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
          ref_subject = ref.getSubject()

          # Java check: ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null
          # This means: is the ref subject the exact subject OR a descendant of the subject?
          is_match = False
          if ref_subject: # Check if subject name is not None
               is_match = ref_subject.lower() == subject.lower()
               if not is_match and subj_entity:
                    # Check if ref.getSubject() is a descendant of subj_entity
                    # Ensure findInTree handles None gracefully if subj_entity is None
                    descendant_check = self.findInTree(subj_entity, ref_subject)
                    is_match = descendant_check is not None

          if is_match:
               objects_set.add(ref.getObject())

     # Return set (unordered), Java returns TreeSet (ordered). Sort if needed for consistency.
     # return sorted(list(objects_set))
     return objects_set

    def getSubjsFromObjRel(self, object_ref: str, relName: str) -> Set[str]: # Java returns TreeSet
     """
     Retrieves subjects related to an object via DIRECT references
     in a specific relationship (considering object inheritance).
     Corrected to match Java logic (no relationship hierarchy traversal).
     """
     subjects_set: Set[str] = set()
     obj_entity = self.findInTree(self.entityTree, object_ref) # Find entity for inheritance check
     rel = self.getRelationship(relName) # Get the specific relationship

     if not rel:
          print(f"Warning: Relationship '{relName}' not found in getSubjsFromObjRel.")
          return set()

     # --- Correction: Only iterate direct references of 'rel' ---
     try:
          direct_references = rel.getReferences() # Assume this returns List[Reference]
     except AttributeError:
          print(f"Warning: Relationship class missing 'getReferences' for '{relName}'. Cannot get subjects.")
          return set()
     # --- End Correction ---

     for ref in direct_references: # Iterate only direct references
          if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
          ref_object = ref.getObject()

          # Java check: ref.getObject().equals(object) || findInTree(parent, ref.getObject())!=null
          # This means: is the ref object the exact object OR a descendant of the object?
          is_match = False
          if ref_object: # Check if object name is not None
               is_match = ref_object.lower() == object_ref.lower()
               if not is_match and obj_entity:
                    # Ensure findInTree handles None gracefully if obj_entity is None
                    descendant_check = self.findInTree(obj_entity, ref_object)
                    is_match = descendant_check is not None

          if is_match:
               subjects_set.add(ref.getSubject())

     # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
     # return sorted(list(subjects_set))
     return subjects_set

    def getRelFromSubjObj(self, subject: str, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves top-level relationship names connecting a subject and object (considering inheritance)."""
        rels_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        obj_entity = self.findInTree(self.entityTree, object_ref)

        for rel in self.getAllRelationships():
            if not hasattr(rel, 'getReferences') or not hasattr(rel, 'getTop') or not hasattr(rel, 'getName'): continue

            for ref in rel.getReferences():
                 if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
                 ref_subject = ref.getSubject()
                 ref_object = ref.getObject()

                 # Check subject inheritance
                 subj_match = ref_subject.lower() == subject.lower()
                 if not subj_match and subj_entity:
                      subj_match = self.findInTree(subj_entity, ref_subject) is not None

                 # Check object inheritance
                 obj_match = ref_object.lower() == object_ref.lower()
                 if not obj_match and obj_entity:
                      obj_match = self.findInTree(obj_entity, ref_object) is not None

                 if subj_match and obj_match:
                      try:
                           top_rel_name = rel.getTop() # Assumes getTop returns name
                           rels_set.add(top_rel_name)
                      except Exception as e:
                           print(f"Warning: Error getting top relationship for '{rel.getName()}': {e}. Using relationship name itself.")
                           rels_set.add(rel.getName())
                      break # Found a match for this relationship, move to the next

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(rels_set))
        return rels_set

    def getObjsFromSubRels(self, subject: str, relationships: List[str]) -> List[str]: # Java returns List (Vector)
     """
     Retrieves unique objects related to a subject via DIRECT references
     in a list of relationship names (considering subject inheritance).
     Corrected to match Java logic (no relationship hierarchy traversal within each rel).
     """
     objects_set: Set[str] = set()
     subj_entity = self.findInTree(self.entityTree, subject) # Find entity for inheritance check

     for rel_name in relationships: # Iterate through the list of relationship names
          rel = self.getRelationship(rel_name) # Get the specific relationship object
          if rel:
               # --- Correction: Only iterate direct references of this 'rel' ---
               try:
                    direct_references = rel.getReferences() # Assume this returns List[Reference]
               except AttributeError:
                    print(f"Warning: Relationship class missing 'getReferences' for '{rel_name}' in getObjsFromSubRels.")
                    continue # Skip this relationship if it has no getReferences method
               # --- End Correction ---

               for ref in direct_references: # Iterate only direct references
                    if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
                    ref_subject = ref.getSubject()

                    # Java check: ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null
                    is_match = False
                    if ref_subject:
                         is_match = ref_subject.lower() == subject.lower()
                         if not is_match and subj_entity:
                              is_match = self.findInTree(subj_entity, ref_subject) is not None

                    if is_match:
                         objects_set.add(ref.getObject())
          else:
               print(f"Warning: Relationship '{rel_name}' not found in getObjsFromSubRels.")


     return sorted(list(objects_set)) # Return sorted list to mimic Java's HashSet -> Vector behavior

    def getObjsFromSubj(self, subject: str) -> Set[str]: # Java returns TreeSet
        """Retrieves unique objects related to a subject across all relationships (considering inheritance)."""
        objects_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)

        for rel in self.getAllRelationships():
            if not hasattr(rel, 'getReferences'): continue
            for ref in rel.getReferences():
                 if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
                 ref_subject = ref.getSubject()

                 # Check subject inheritance
                 is_match = ref_subject.lower() == subject.lower()
                 if not is_match and subj_entity:
                      is_match = self.findInTree(subj_entity, ref_subject) is not None

                 if is_match:
                      objects_set.add(ref.getObject())

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(objects_set))
        return objects_set

    def getSubjsFromObj(self, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves unique subjects related to an object across all relationships (considering inheritance)."""
        subjects_set: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref)

        for rel in self.getAllRelationships():
            if not hasattr(rel, 'getReferences'): continue
            for ref in rel.getReferences():
                 if not hasattr(ref, 'getSubject') or not hasattr(ref, 'getObject'): continue
                 ref_object = ref.getObject()

                 # Check object inheritance
                 is_match = ref_object.lower() == object_ref.lower()
                 if not is_match and obj_entity:
                      is_match = self.findInTree(obj_entity, ref_object) is not None

                 if is_match:
                      subjects_set.add(ref.getSubject())

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(subjects_set))
        return subjects_set

    def getAxioms(self) -> Set[Axiom]: # Java returns HashSet
        """Returns the set of axioms."""
        return self.axioms.copy() # Return copy

    def setAxioms(self, axioms: Set[Axiom]) -> None: # Java takes HashSet
        """Sets the axioms."""
        self.axioms = set(axioms) # Store copy
