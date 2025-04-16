import os
import xml.etree.ElementTree as ET
# from xml.dom import minidom # For pretty printing XML if needed
from pathlib import Path
import io
import codecs
from typing import List, Dict, Set, Optional, Tuple, Union, cast, Any # Added Any for DefaultTreeNode compatibility
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
from .TreeNode import TreeNode # Assuming TreeNode is the base or interface
from .DefaultTreeNode import DefaultTreeNode # Assuming this is the implementation used
# from .UType import UType # Assuming UType might be needed based on Java code

# Helper Pair class (can be replaced by tuple if preferred, kept for Java similarity)
class Pair:
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value

    def getKey(self) -> Any:
        return self.key

    def getValue(self) -> Any:
        return self.value

class DomainData:
    """
    This class represents the domain data for a specific domain.
    It contains methods for loading and parsing .gbs files, as well as storing and manipulating domain information.
    The domain data includes entities, relationships, attributes, union_entities axioms, etc.
    """
    # private String author; # Not directly mapped, consider adding if needed
    # private int version; # Not directly mapped, consider adding if needed
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
    subjRelObjs: Set[str] # Java: TreeSet<String> (Python set is unordered)
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

    # Scaraggi attributes - added for completeness from Java end section
    domainList: Optional[List[str]] = None # Java: ArrayList<String>
    inverse: Optional[str] = None # Java: String
    attrsRel: Dict[str, List[Attribute]] # Java: Map<String, Vector<Attribute>>

    # Unified constructor mimicking Java overloaded constructors
    def __init__(self,
                 path_or_bytearray: str | bytes | None = None,
                 webInfFolder: str | None = None,
                 domainName: str | None = None,
                 file: str | Path | None = None):
        """
        Initializes the DomainData object. Mimics Java overloaded constructors:
        1. DomainData(): Default constructor (call with no arguments).
        2. DomainData(path): Loads from a .gbs file path or domain name (String path).
           Requires webInfFolder if path is just a domain name.
        3. DomainData(byteArray, webInfFolder): Loads from byte array (byte[] byteArray, String webInfFolder).
        4. DomainData(domainName, file): Loads an arbitrary file with a given domain name (String domainName, File file).
        """
        # Default initializations (Common to all constructors)
        self.types = []
        self.importedFiles = []
        self.removedEntities = []
        self.removedRelationships = []
        self.domain = None
        self.unions = set()
        self.axioms = set()
        self.subjects = []
        self.objects = []
        self.subjRelObjs = set() # Use set, Java used TreeSet (ordered)
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
        self.webInfFolder = webInfFolder if webInfFolder is not None else "" # Set early if provided

        # Initialize root Entity (matches Java constructor logic)
        self.entityTree = Entity("Entity", None)
        entity_attributes = [
            # Java uses string "true"/"false", let's stick to bool for Pythonic style
            # Ensure Attribute class handles bool or converts internally if needed
            Attribute(name="name", data_type="string", mandatory=True),
            Attribute(name="description", data_type="string", mandatory=False),
            Attribute(name="notes", data_type="string", mandatory=False)
        ]
        self.entityTree.addAttributes(entity_attributes)
        self.entityTree.setChildren([])

        # Initialize root Relationship (matches Java constructor logic)
        self.relationshipTree = Relationship(name="Relationship", domain=None, inverse="Relationship")
        self.relationshipTree.setChildren([]) # Java uses setChildren here too

        # Scaraggi attributes initialization
        self.domainList = None
        self.inverse = None
        self.attrsRel = defaultdict(list)

        # --- Constructor Logic ---
        load_executed = False
        try:
            # Case 3: DomainData(byte[] byteArray, String webInfFolder)
            if isinstance(path_or_bytearray, bytes) and webInfFolder is not None:
                if domainName is not None or file is not None:
                    raise TypeError("Cannot provide domainName or file when using byte array constructor.")
                self.webInfFolder = webInfFolder # Already set, but confirm
                is_ = io.BytesIO(path_or_bytearray)
                doc = self.parse_stream(is_)
                root_element = doc.getroot()
                domain_name_from_bytes = root_element.get("name")
                if domain_name_from_bytes is None:
                     raise ValueError("Root <domain> tag must have a 'name' attribute.")
                self.domain = domain_name_from_bytes # Set domain early like Java
                # Java passes the extracted domain name as domainPath to loadFile
                self.loadFile(doc, self.domain)
                load_executed = True

            # Case 4: DomainData(String domainName, File file)
            elif domainName is not None and file is not None:
                if path_or_bytearray is not None:
                     raise TypeError("Cannot provide path_or_bytearray when using domainName/file constructor.")
                self.domain = domainName # Set domain explicitly like Java
                file_path = Path(file)
                doc = self.parseFile(file_path)
                # Java passes the absolute path of the file
                self.loadFile(doc, str(file_path.resolve()))
                load_executed = True

            # Case 2: DomainData(String path)
            elif isinstance(path_or_bytearray, str):
                 if domainName is not None or file is not None:
                     raise TypeError("Cannot provide domainName or file when using path string constructor.")
                 path_str = path_or_bytearray
                 file_path: Path
                 domain_path_for_load: str
                 if path_str.endswith(".gbs"):
                     file_path = Path(path_str)
                     # Use absolute path for consistency and import tracking
                     domain_path_for_load = str(file_path.resolve())
                     doc = self.parseFile(file_path)
                     self.loadFile(doc, domain_path_for_load) # Pass absolute path
                 else:
                     # Assumes path is domain name and needs webInfFolder
                     if not self.webInfFolder:
                          raise ValueError("webInfFolder must be provided if path is not a full .gbs path")
                     file_path = Path(self.webInfFolder) / (path_str + ".gbs")
                     # Use absolute path for consistency
                     domain_path_for_load = str(file_path.resolve())
                     doc = self.parseFile(file_path)
                     # Java passed 'path' (the domain name) as domainPath here.
                     # Let's pass the absolute path to loadFile for consistency in getFolderPath.
                     self.loadFile(doc, domain_path_for_load)
                 load_executed = True

            # Case 1: DomainData() (Default constructor)
            elif path_or_bytearray is None and webInfFolder is None and domainName is None and file is None:
                # Initializations already done, nothing more to do.
                load_executed = True # Technically no load, but constructor finished.
                pass

            else:
                 # Invalid combination of arguments
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

    # Helper method for parsing stream (internal) - Renamed
    def parse_stream(self, stream: io.BytesIO) -> ET.ElementTree:
        """Parses an XML stream into an ElementTree."""
        try:
            # Note: Java uses DOM parser (DocumentBuilder), Python uses ElementTree (ET)
            # Differences in API and tree representation exist.
            tree = ET.parse(stream)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            raise

    # Method: parseFile (private in Java) - Renamed
    # Note: Java returns org.w3c.dom.Document, Python returns ET.ElementTree
    def parseFile(self, file_path: Path) -> ET.ElementTree:
        """
        Parses the given file path and returns an ElementTree object.
        Internal helper corresponding to Java's private Document parseFile(File file).
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            tree = ET.parse(file_path)
            return tree
        except ET.ParseError as e:
            print(f"XML Parse Error in file {file_path}: {e}")
            # Java catches specific exceptions and prints stack trace. Re-raising is Pythonic.
            raise
        except IOError as e: # Catch IO errors specifically if needed
             print(f"IO Error parsing file {file_path}: {e}")
             raise
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            raise

    # Method: getFolderPath (private in Java) - Renamed
    # Note: Java returns Vector<String>, Python returns List[str]
    def getFolderPath(self, domainPath: str) -> List[str]:
        """
        Retrieves the folder path and base filename for the given domain path.
        Internal helper corresponding to Java's private Vector<String> getFolderPath(String domainPath).
        Returns: A list containing [base_filename_without_extension, folder_path].
        """
        print(f"Getting folder path for: {domainPath}") # Matches Java print
        folderPath: List[str] = ["", ""] # Initialize list like Java Vector size 2

        # Java logic: if contains "/", split path; else use webInfFolder
        # Separator check needs to handle both / and \ for cross-platform compatibility
        if "/" in domainPath or os.path.sep in domainPath:
             path_obj = Path(domainPath)
             folder = str(path_obj.parent)
             base_name = path_obj.stem # Name without extension (Java used replace(".gbs", ""))
             folderPath[0] = base_name
             folderPath[1] = folder
        else:
             # Assumes domainPath is just the domain name (without .gbs)
             folder = self.webInfFolder
             base_name = domainPath # Java sets folderPath[0] to domainPath initially
             folderPath[0] = base_name
             folderPath[1] = folder

        print(f"  Base name: {folderPath[0]}, Folder: {folderPath[1]}") # Mimic Java output if needed
        return folderPath

    # Method: validateTag (private in Java) - Renamed
    # Note: Java takes org.w3c.dom.Node, Python takes ET.Element
    def validateTag(self, tag: ET.Element, validTags: List[str]) -> None:
        """
        Validates a tag against a list of valid tags.
        Raises ValueError if the tag is not found in the list of valid tags.
        Internal helper corresponding to Java's private void validateTag(Node tag, List<String> validTags).
        """
        if tag.tag not in validTags:
            # Attempt to mimic Java error message (parent info might be hard with ET)
            # Java: "Invalid tag <"+tag.getNodeName()+"> found under <"+tag.getParentNode().getNodeName()+" "+(tag.getParentNode().getAttributes().getNamedItem("name")==null?"":tag.getParentNode().getAttributes().getNamedItem("name"))+"> where one of "+validTags+" was expected"
            # Simplified version for Python ET:
            # Finding parent reliably in ET requires extra work (e.g., parent map or lxml)
            # For now, provide a simpler error message.
            raise ValueError(
                f"Invalid tag <{tag.tag}> found where one of {validTags} was expected"
                # Consider adding parent info if a parent map is maintained during parsing
            )

    # Method: validateTagAttributes (private in Java) - Renamed
    # Note: Java takes org.w3c.dom.Node, Python takes ET.Element
    def validateTagAttributes(self, tag: ET.Element, validTagAttributes: List[str], identifier: str) -> None:
        """
        Validates the attributes of a given XML tag against a list of valid attributes.
        Raises ValueError if any invalid attribute is found.
        Internal helper corresponding to Java's private void validateTagAttributes(Node tag, List<String> validTagAttributes, String identifier).
        """
        tag_id_val = tag.get(identifier, "") if identifier else "" # Get identifier value if specified
        # Java error includes identifier value if present: "<"+tag.getNodeName()+" "+(tag.getAttributes().getNamedItem(identifier)==null?"":tag.getAttributes().getNamedItem(identifier))+">"
        tag_id_str = f"{identifier}='{tag_id_val}'" if identifier and tag_id_val else ""
        tag_repr = f"<{tag.tag} {tag_id_str}>".strip()

        for attr_name in tag.attrib:
            if attr_name not in validTagAttributes:
                raise ValueError(
                    f"Invalid attribute \"{attr_name}\" found in {tag_repr} "
                    f"where one of {validTagAttributes} was expected"
                )

    # Method: loadFile (private in Java) - Renamed
    # Note: Java takes org.w3c.dom.Document, Python takes ET.ElementTree
    def loadFile(self, doc: ET.ElementTree, domainPath: str) -> None:
        """
        Loads a file and parses its contents to populate the domain data.
        Internal helper corresponding to Java's private void loadFile(Document doc, String domainPath).
        """
        folderPath = self.getFolderPath(domainPath) # Returns List[str]
        base_name = folderPath[0]
        folder_path_str = folderPath[1]
        webInf = Path(folder_path_str) # Use Path object for consistency

        root_element = doc.getroot()

        # --- Validation ---
        # Validate root tag is <domain>
        if root_element.tag != "domain":
             raise ValueError(f"Expected root tag <domain>, but found <{root_element.tag}> in {domainPath}") # Java throws Exception

        # Validate domain name attribute
        domain_name_attr = root_element.get("name")
        if domain_name_attr is None:
             # Java gets attribute and checks null later, but error message implies it checks here
             raise ValueError(f"Root tag <domain> must have a 'name' attribute in {domainPath}") # Java throws Exception

        # Set domain if not already set (matches Java logic)
        if self.domain is None:
            self.domain = domain_name_attr
        # Java doesn't explicitly check for domain mismatch here, seems to allow overwriting/merging later.
        # Let's keep the warning for clarity in Python.
        elif self.domain != domain_name_attr and domainPath not in self.importedFiles:
             print(f"Warning: Loading file with domain '{domain_name_attr}' into existing domain '{self.domain}' from {domainPath}")

        # --- Process Child Elements ---
        # Java uses index-based access and checks node names. Python uses iteration and tag checks.
        allowed_sections = ["imports", "user-types", "entities", "union_entities", "relationships", "axioms"]

        # Filter out non-element nodes (like comments)
        children = [child for child in root_element if isinstance(child.tag, str)]

        current_child_index = 0

        # --- 1. Imports (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "imports":
            self.validateTag(children[current_child_index], ["imports"]) # Java validates implicitly by checking name
            self.parseImports(webInf, children[current_child_index])
            current_child_index += 1

        # --- 2. User Types (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "user-types":
             self.validateTag(children[current_child_index], ["user-types"])
             self.parseTypes(webInf, children[current_child_index])
             current_child_index += 1

        # --- 3. Entities (Mandatory) ---
        if current_child_index >= len(children) or children[current_child_index].tag != "entities":
            # Java throws Exception
            raise ValueError(f"Missing mandatory <entities> section in domain '{self.domain or domain_name_attr}' file: {domainPath}")
        self.validateTag(children[current_child_index], ["entities"])
        self.parseEntities(children[current_child_index], self.entityTree, self.domain or domain_name_attr) # Pass current domain
        current_child_index += 1

        # --- 4. Union Entities (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "union_entities":
             self.validateTag(children[current_child_index], ["union_entities"])
             self.parseUnionEntities(children[current_child_index], self.domain or domain_name_attr)
             current_child_index += 1

        # --- 5. Relationships (Mandatory) ---
        if current_child_index >= len(children) or children[current_child_index].tag != "relationships":
             # Java throws Exception
             raise ValueError(f"Missing mandatory <relationships> section in domain '{self.domain or domain_name_attr}' file: {domainPath}")
        self.validateTag(children[current_child_index], ["relationships"])
        self.parseRelationships(children[current_child_index], self.relationshipTree, self.domain or domain_name_attr)
        current_child_index += 1

        # --- 6. Axioms (Optional) ---
        if current_child_index < len(children) and children[current_child_index].tag == "axioms":
             self.validateTag(children[current_child_index], ["axioms"])
             self.parseAxioms(children[current_child_index], self.domain or domain_name_attr)
             current_child_index += 1

        # Check for unexpected tags (Java doesn't explicitly check this, relies on index/name checks)
        if current_child_index < len(children):
            unexpected_tag = children[current_child_index].tag
            raise ValueError(f"Unexpected tag <{unexpected_tag}> found in <domain> tag in {domainPath}. Allowed order: {allowed_sections}")

        # Sort subjects and objects (matches Java)
        self.subjects.sort()
        self.objects.sort()

    # Method: parseAxioms (private in Java) - Renamed
    def parseAxioms(self, axioms_tag: ET.Element, domainName: str) -> None:
        """
        Parses the axioms from the given XML node and adds them to the set of axioms.
        Internal helper for Java's private void parseAxioms(Node axioms_tag, String domainName).
        """
        # Java valid attributes: "name","formalism","rule"
        valid_axiom_attrs = ["name", "formalism", "rule"]
        for axiom_node in axioms_tag.findall("axiom"):
            self.validateTag(axiom_node, ["axiom"])
            self.validateTagAttributes(axiom_node, valid_axiom_attrs, "name")

            name = axiom_node.get("name")
            formalism = axiom_node.get("formalism")
            # Java uses attribute "rule", not text content
            expression = axiom_node.get("rule")

            if name is None or formalism is None or expression is None:
                 # Java doesn't explicitly check for null here but relies on later NullPointerException?
                 # Adding check for clarity.
                 raise ValueError(f"Axiom tag requires 'name', 'formalism', and 'rule' attributes. Found: name={name}, formalism={formalism}, rule={expression}")

            print(f"Parsing Axiom: {name} {formalism} {expression}") # Mimic Java print
            new_axiom = Axiom(name=name, formalism=formalism, expression=expression, domain=domainName)

            # Check for duplicates before adding (Java uses HashSet.add which returns false if duplicate)
            # Python set add doesn't return value, check membership first
            if new_axiom in self.axioms:
                 # Check if the existing one has the same domain (Java error condition)
                 existing = next((a for a in self.axioms if a == new_axiom), None)
                 if existing and existing.getDomain() == domainName:
                      raise ValueError(f"Duplicate Axiom: \"{name}\" in domain \"{domainName}\"")
                 # If domains differ, Java logic seems unclear. Python set will just ignore the duplicate.
            else:
                 self.axioms.add(new_axiom)

    # Method: parseUnionEntities (private in Java) - Renamed
    def parseUnionEntities(self, union_entities_tag: ET.Element, domainName: str) -> None:
        """
        Parses the union entities from the given XML node and adds them to the domain's set of Union entities.
        Internal helper for Java's private void parseUnionEntities(Node union_entities, String domainName).
        """
        unions_to_add: List[Union] = []
        valid_union_attrs = ["name"]
        valid_uvalue_attrs = ["name"] # For <uvalue> tag

        for union_node in union_entities_tag.findall("union"):
            self.validateTag(union_node, ["union"])
            self.validateTagAttributes(union_node, valid_union_attrs, "name")

            union_name = union_node.get("name")
            if not union_name:
                raise ValueError("<union> tag requires a 'name' attribute.")

            # Check if an entity with the same name already exists (Java check)
            if self.findInTree(self.entityTree, union_name) is not None:
                raise ValueError(f"Entity \"{union_name}\" already exists, can't create union entity with the same name.")

            # Read uvalues using readValuesList helper
            # Java uses: new HashSet<>(readValuesList(pair.getValue(), "uvalue", false))
            uvalues_list = self.readValuesList(union_node, "uvalue", False)
            uvalues: Set[str] = set(uvalues_list) # Convert list to set

            new_union = Union(name=union_name, domain=domainName, values=uvalues)
            unions_to_add.append(new_union)

        self.addUnions(unions_to_add)

    # Method: addUnions (private in Java) - Renamed
    def addUnions(self, _unions: List[Union]) -> None:
        """
        Adds a list of Union objects to the domain, checking for duplicates and valid entity references.
        Internal helper for Java's private void addUnions(List<Union> _unions).
        """
        # Check that all uvalues are existing entities
        for union_obj in _unions:
            for entity_name in union_obj.getValues():
                if self.findInTree(self.entityTree, entity_name) is None:
                    raise ValueError(f"Entity \"{entity_name}\" required by union \"{union_obj.getName()}\" does not exist.")

        # Add or merge unions (Java logic)
        for new_union in _unions:
            # Check if a union with the same name already exists
            existing_union = next((u for u in self.unions if u.getName() == new_union.getName()), None)

            if existing_union:
                 # Java logic: Error if same domain, merge if different domain
                 if existing_union.getDomain() == new_union.getDomain():
                      # Java throws error, let's match Java.
                      raise ValueError(f"Duplicate Union: \"{new_union.getName()}\" in domain \"{new_union.getDomain()}\"")
                 else:
                      # Different domains, merge values and update domain (overwriting)
                      print(f"Merging union '{new_union.getName()}' from domain '{new_union.getDomain()}' into existing from '{existing_union.getDomain()}'")
                      existing_union.setDomain(new_union.getDomain()) # Overwrite domain
                      existing_union.getValues().update(new_union.getValues()) # Merge values
            else:
                 # Union is new, just add it
                 self.unions.add(new_union)

    # Method: addEntity (public in Java)
    def addEntity(self, entity: Entity) -> None:
        """Adds a top-level entity to the domain, replacing any existing top-level entity with the same name."""
        if not isinstance(entity, Entity):
            raise TypeError("Can only add Entity objects")

        # Java logic: find existing, remove if found, then add.
        existing_entity = next((e for e in self.getTopEntities() if e.getName() == entity.getName()), None)

        if existing_entity:
            print(f"Replacing existing top-level entity '{entity.getName()}'")
            # Java uses List.remove(Object), ensure Python list remove works
            try:
                 # Assuming getChildren returns a mutable list or Entity.removeChild exists
                 self.entityTree.removeChild(existing_entity) # Prefer specific method if available
                 # Or: self.entityTree.getChildren().remove(existing_entity) # If getChildren is mutable list
            except (ValueError, AttributeError) as e:
                 print(f"Warning: Could not remove existing entity '{entity.getName()}' during replacement: {e}")
            # Detach old entity? Java doesn't explicitly detach here, relies on GC?
            # existing_entity.setParent(None) # Optional cleanup

        self.entityTree.addChild(entity) # addChild should handle setting the parent internally

    # Method: addRelationship (public in Java)
    def addRelationship(self, relationship: Relationship) -> None:
        """Adds a top-level relationship to the domain, replacing any existing top-level relationship with the same name."""
        if not isinstance(relationship, Relationship):
            raise TypeError("Can only add Relationship objects")

        # Java logic: find existing, remove if found, then add.
        existing_rel = next((r for r in self.getTopRelationships() if r.getName() == relationship.getName()), None)

        if existing_rel:
            print(f"Replacing existing top-level relationship '{relationship.getName()}'")
            # Need to remove from the relationshipTree's children
            try:
                 # Assuming getChildren returns a mutable list or Entity.removeChild exists
                 self.relationshipTree.removeChild(existing_rel) # Prefer specific method
                 # Or: self.relationshipTree.getChildren().remove(existing_rel)
            except (ValueError, AttributeError) as e:
                 print(f"Warning: Could not remove existing relationship '{relationship.getName()}' during replacement: {e}")
            # Detach old relationship?
            # existing_rel.setParent(None) # Optional cleanup

        # Java uses addChild for relationships too
        self.relationshipTree.addChild(relationship) # Assuming addChild works for Relationships too and sets parent

    # Method: parseRelationships (private in Java) - Renamed
    def parseRelationships(self, parentNode: ET.Element, root: Relationship, domainName: str) -> None:
        """
        Recursively constructs the relationships tree by parsing relationships and their attributes, references, and sub-relationships.
        Internal helper for Java's private void parseRelationships(Node parentNode, Relationship root, String domainName).
        """
        # Java valid attributes: "name","inverse","description","abstract"
        # Python version also had "notes". Let's match Java for now.
        valid_rel_attrs = ["name", "inverse", "description", "abstract", "notes"] # Keep notes for now, Java might miss it in validation list
        # Determine allowed children based on whether we are at the top <relationships> or inside a <relationship>
        allowed_children = ["relationship"] if root == self.relationshipTree else ["relationship", "attribute", "reference"]

        # Filter for relationship elements first
        relationship_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == "relationship"]

        for rel_node in relationship_nodes: # Iterate through direct children that are <relationship>
             self.validateTag(rel_node, allowed_children) # Validate allowed children in this context
             self.validateTagAttributes(rel_node, valid_rel_attrs, "name") # Validate attributes of <relationship>

             rel_name = rel_node.get("name")
             rel_inverse = rel_node.get("inverse")
             description = rel_node.get("description")
             notes = rel_node.get("notes") # Get notes attribute
             is_abstract_str = rel_node.get("abstract", "false") # Default to false if missing
             is_abstract = is_abstract_str.lower() == "true"

             if not rel_name or not rel_inverse:
                  raise ValueError("<relationship> tag requires 'name' and 'inverse' attributes.") # Java doesn't check null here

             # Find existing relationship anywhere in the tree first (Java logic)
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
                       root.addChild(existing_relationship) # Add to new parent (sets parent) - Java uses addChild
                       current_relationship = existing_relationship
                  elif existing_parent == root:
                       # Already in the correct place, just update properties
                       print(f"Updating existing relationship '{rel_name}' under parent '{root.getName()}'")
                       current_relationship = existing_relationship
                  else:
                       # Inconsistency: Found elsewhere but not in a compatible import/parent situation
                       raise ValueError(f"Inconsistency: Relationship '{rel_name}' found under unexpected parent '{existing_parent.getName() if existing_parent else 'root'}'. Cannot automatically move to '{root.getName()}'.") # Java throws Exception
             else:
                  # Relationship is new, create it
                  print(f"Creating new relationship '{rel_name}' under parent '{root.getName()}'")
                  # Java constructor: new Relationship(domainName, relationName, relationInverse);
                  current_relationship = Relationship(name=rel_name, domain=domainName, inverse=rel_inverse)
                  root.addChild(current_relationship) # Adds to children and sets parent

             # Update properties of the (potentially existing or new) relationship
             if current_relationship:
                  current_relationship.setDomain(domainName) # Overwrite domain like Java
                  current_relationship.setDescription(description or "") # Use empty string if None
                  current_relationship.setAbstract(is_abstract)
                  current_relationship.setNotes(notes or "") # Use empty string if None

                  # Add attributes defined directly within this <relationship> tag
                  direct_attributes = self.readAttributes(rel_node)
                  current_relationship.addAttributes(direct_attributes) # Add new attributes

                  # Parse references defined directly within this <relationship> tag
                  self.parseReferences(rel_node, current_relationship)

                  # Recursively parse sub-relationships
                  self.parseRelationships(rel_node, current_relationship, domainName)
             else:
                  # This case should ideally not happen if logic above is correct
                  print(f"Error: Failed to get or create relationship '{rel_name}'")

    # Method: parseReferences (private in Java) - Renamed
    def parseReferences(self, parentNode: ET.Element, relation: Relationship) -> None:
        """
        Parses the references from the given parent node (<relationship>) and adds them to the specified relationship.
        Internal helper for Java's private void parseReferences(Node parentNode, Relationship relation).
        """
        relation_name = relation.getName()
        # Java valid attributes: "subject","object"
        valid_ref_attrs = ["subject", "object"]
        # Java valid attributes for attributes within reference: "name","datatype","description","mandatory","distinguishing","display","target","notes"
        valid_attr_attrs = ["name", "datatype", "description", "mandatory",
                            "distinguishing", "display", "target", "notes"]

        for ref_node in parentNode.findall("reference"):
             self.validateTagAttributes(ref_node, valid_ref_attrs, "") # Validate reference attributes

             subject = ref_node.get("subject")
             object_ref = ref_node.get("object") # Renamed variable to avoid conflict with keyword

             if not subject or not object_ref:
                  raise ValueError("<reference> tag requires 'subject' and 'object' attributes.") # Java doesn't check null

             # Add subject/object to global lists if not present (Java logic)
             if subject not in self.subjects:
                  self.subjects.append(subject)
                  # Java sorts later

             if object_ref not in self.objects:
                  self.objects.append(object_ref)
                  # Java sorts later

             # Create Reference object (Java: new Reference(subject, object))
             ref = Reference(subject=subject, object=object_ref)

             # Read attributes specific to this reference (Java: ref.setAttributes(readAttributes(node)))
             ref_attributes = self.readAttributes(ref_node) # Attributes can be children of <reference>
             if ref_attributes:
                  ref.setAttributes(ref_attributes) # Assuming setAttributes takes a list

             # Add reference to the relationship (Java: relation.addReference(ref))
             relation.addReference(ref) # Assuming addReference handles internal storage

             # Update helper dictionaries and sets (Java logic)
             self.nRelRefs += 1
             subj_rel_obj_str = f"{subject}.{relation_name}.{object_ref}"
             self.subjRelObjs.add(subj_rel_obj_str) # Python set is unordered, Java TreeSet is ordered

             self.addValue(self.subjRels, subject, relation_name)
             self.addValue(self.subjObjs, subject, object_ref)
             self.addValue(self.relSubjs, relation_name, subject)
             self.addValue(self.relObjs, relation_name, object_ref)
             self.addValue(self.objRels, object_ref, relation_name)
             self.addValue(self.objSubjs, object_ref, subject)
             self.addValue(self.subjRel_Objs, f"{subject}.{relation_name}", object_ref)
             self.addValue(self.subjObj_Rels, f"{subject}.{object_ref}", relation_name)
             self.addValue(self.relObj_Subjs, f"{relation_name}.{object_ref}", subject)

    # Method: parseEntities (private in Java) - Renamed
    def parseEntities(self, parentNode: ET.Element, root: Entity, domainName: str) -> None:
        """
        Recursively parses entities from the given parent node and adds them to the entity tree.
        Internal helper for Java's private void parseEntities(Node parentNode, Entity root, String domainName).
        """
        # Java valid attributes: "name","description","abstract","notes"
        valid_entity_attrs = ["name", "description", "abstract", "notes"]
        # Determine allowed children based on whether we are at the top <entities> or inside an <entity>
        allowed_children = ["entity"] if root == self.entityTree else ["entity", "attribute"]

        # Filter for entity elements first
        entity_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == "entity"]

        for entity_node in entity_nodes: # Iterate through direct children that are <entity>
             self.validateTag(entity_node, allowed_children) # Validate allowed children in this context
             self.validateTagAttributes(entity_node, valid_entity_attrs, "name") # Validate attributes of <entity>

             entity_name = entity_node.get("name")
             description = entity_node.get("description")
             notes = entity_node.get("notes")
             is_abstract_str = entity_node.get("abstract", "false")
             is_abstract = is_abstract_str.lower() == "true"

             if not entity_name:
                  raise ValueError("<entity> tag requires a 'name' attribute.") # Java doesn't check null

             # Find existing entity anywhere in the tree first (Java logic)
             existing_entity = self.findInTree(self.entityTree, entity_name)
             current_entity: Optional[Entity] = None

             if existing_entity:
                  # Entity already exists somewhere
                  existing_parent = existing_entity.getParent()
                  is_ancestor = existing_parent and root.hasAncestor(existing_parent.getName())
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
                       raise ValueError(f"Inconsistency: Entity '{entity_name}' found under unexpected parent '{existing_parent.getName() if existing_parent else 'root'}'. Cannot automatically move to '{root.getName()}'.") # Java throws Exception
             else:
                  # Entity is new, create it (Java: new Entity(entityName, domainName))
                  print(f"Creating new entity '{entity_name}' under parent '{root.getName()}'")
                  current_entity = Entity(name=entity_name, domain=domainName)
                  root.addChild(current_entity) # Adds to children and sets parent

             # Update properties
             if current_entity:
                  current_entity.setDomain(domainName) # Overwrite domain like Java
                  current_entity.setDescription(description or "")
                  current_entity.setAbstract(is_abstract)
                  current_entity.setNotes(notes or "")

                  # Add attributes defined directly within this <entity> tag (Java: currentEntity.addAttributes(readAttributes(en)))
                  direct_attributes = self.readAttributes(entity_node)
                  current_entity.addAttributes(direct_attributes)

                  # Recursively parse sub-entities (Java: parseEntities(en, currentEntity, domainName))
                  self.parseEntities(entity_node, current_entity, domainName)
             else:
                  print(f"Error: Failed to get or create entity '{entity_name}'")

    # Method: parseImports (private in Java) - Renamed
    def parseImports(self, folder: Path, importsNode: ET.Element) -> None:
        """
        Parses the imports from the <imports> tag, loads imported files recursively (DFS),
        and handles the <deleted> section.
        Internal helper for Java's private void parseImports(File folder, Node importsNode).
        """
        # Java valid children: "import","deleted"
        valid_import_children = ["import", "deleted"]
        # Java valid import attributes: "schema"
        valid_import_attrs = ["schema"]
        # Java valid deleted children: "entity","relationship"
        valid_deleted_children = ["entity", "relationship"]
        # Java valid deleted item attributes: "name"
        valid_deleted_item_attrs = ["name"]

        children = [child for child in importsNode if isinstance(child.tag, str)] # Filter comments/PIs
        import_nodes: List[ET.Element] = []
        deleted_node: Optional[ET.Element] = None

        # Separate import and deleted nodes, validate structure (Java logic)
        for i, child in enumerate(children):
             self.validateTag(child, valid_import_children)
             if child.tag == "import":
                  if deleted_node is not None:
                       raise ValueError("<import> tag cannot appear after <deleted> tag within <imports>.")
                  self.validateTagAttributes(child, valid_import_attrs, "schema")
                  import_nodes.append(child)
             elif child.tag == "deleted":
                  if deleted_node is not None:
                       # Java doesn't explicitly check for multiple <deleted> tags
                       print("Warning: Multiple <deleted> tags found within <imports>. Only the last one might be processed based on Java loop structure.")
                  if i != len(children) - 1:
                       # Java check: IntStream.range(0, nodes.size()-1).filter(i->nodes.get(i).getNodeName().equals("deleted"))...
                       raise ValueError("<deleted> tag must be the last child of <imports>.")
                  # No attributes expected on <deleted> itself
                  self.validateTagAttributes(child, [], "")
                  deleted_node = child # Keep track of the (last) deleted node

        # Process imports first (DFS)
        for import_node in import_nodes:
            schema_path_str = import_node.get("schema")
            if not schema_path_str:
                 raise ValueError("<import> tag requires a 'schema' attribute.") # Java doesn't check null

            # Resolve import path (Java logic: check "/", else use folder)
            import_file_path: Path
            # Use absolute path for reliable checking and loading (Java passes absolute path eventually)
            # Check if schema_path_str is already absolute or contains separators
            if Path(schema_path_str).is_absolute() or "/" in schema_path_str or os.path.sep in schema_path_str:
                 import_file_path = Path(schema_path_str)
                 # Ensure .gbs extension? Java seems to assume it's there or adds it later.
                 # Let's assume the path is correct if it contains separators.
            else:
                 # Relative path (likely just domain name), resolve against the folder of the *current* file
                 import_file_path = folder / (schema_path_str + ".gbs")

            abs_import_path_str = str(import_file_path.resolve())

            # Avoid reloading files already processed (Python version tracks importedFiles list)
            if abs_import_path_str not in self.importedFiles:
                 print(f"Importing: {abs_import_path_str}")
                 self.importedFiles.append(abs_import_path_str) # Track import
                 try:
                      imported_doc = self.parseFile(import_file_path)
                      # Recursively load the imported file (Java passes absolute path)
                      self.loadFile(imported_doc, abs_import_path_str)
                 except FileNotFoundError:
                      print(f"Error: Imported file not found: {import_file_path}")
                      raise # Re-raise to stop the loading process
                 except Exception as e:
                      print(f"Error loading imported file {import_file_path}: {e}")
                      raise # Re-raise
            else:
                 print(f"Skipping already imported file: {abs_import_path_str}")

        # Process deleted items after all imports are done (Java logic)
        if deleted_node is not None:
            for deleted_item in deleted_node:
                 if not isinstance(deleted_item.tag, str): continue # Skip comments/PIs
                 self.validateTag(deleted_item, valid_deleted_children)
                 self.validateTagAttributes(deleted_item, valid_deleted_item_attrs, "name")

                 item_type = deleted_item.tag
                 item_name = deleted_item.get("name")
                 if not item_name:
                      raise ValueError(f"<{item_type}> tag within <deleted> requires a 'name' attribute.") # Java doesn't check null

                 print(f"Processing deletion: Type='{item_type}', Name='{item_name}'")
                 if item_type == "entity":
                      self.removeEntity(item_name) # Remove from tree
                      if item_name not in self.removedEntities:
                           self.removedEntities.append(item_name) # Track removal (Java list)
                 elif item_type == "relationship":
                      self.removeRelationship(item_name) # Remove from tree
                      if item_name not in self.removedRelationships:
                           self.removedRelationships.append(item_name) # Track removal (Java list)

    # Method: parseTypes (private in Java) - Renamed
    def parseTypes(self, webInf: Path, typesNode: ET.Element) -> None:
        """
        Parses the <user-types> section.
        Internal helper for Java's private void parseTypes(File webInf, Node typesNode).
        """
        try:
            # readAttributes expects a parent node containing <attribute> children
            attributes_read = self.readAttributes(typesNode)
            self.types = self.fromAttributesToTypes(attributes_read) # Java uses Vector
            print(f"Parsed {len(self.types)} user types.")
        except Exception as e: # Catch potential CloneNotSupportedException if Attribute.clone fails
            print(f"Error parsing user types: {e}")
            traceback.print_exc() # Java prints stack trace

    # Method: fromAttributesToTypes (private in Java) - Renamed
    def fromAttributesToTypes(self, attributes: List[Attribute]) -> List[Attribute]: # Java returns Vector
        """
        Converts a list of attributes into a list of types (potentially UType instances).
        Internal helper for Java's private Vector<Attribute> fromAttributesToTypes(Vector<Attribute> attributes).
        """
        # Java code casts to UType but seems to store as Attribute in the Vector.
        # Python equivalent: return the list directly.
        return attributes # Return List[Attribute]

    # Method: substitute (private in Java) - Renamed
    # Note: This method modifies files on disk, which is less common in Python.
    # It also relies heavily on Java's DOM manipulation. Translating accurately is complex.
    def substitute(self, fileToModify: Path, entityToRemove: str, entityToAddNode: ET.Element) -> None:
        """
        Substitutes an entity in the specified XML file with a new entity definition.
        NOTE: Directly modifies the file on disk. Use with caution.
        Internal helper for Java's private void substitute(File fileToModify, String entityToRemove, Node entityToAdd).
        """
        print(f"Attempting to substitute entity '{entityToRemove}' in file: {fileToModify}")
        # This requires loading the XML, finding the node, removing it, cloning/importing the new node,
        # inserting it, and saving. Using lxml would simplify finding/removing nodes.
        # With ElementTree, it's more cumbersome.
        # Given the complexity and potential side effects, providing a robust
        # implementation matching Java's DOM manipulation is difficult without lxml.
        # Placeholder implementation:
        try:
            # 1. Parse the file to modify
            # Use lxml for easier tree manipulation if available, otherwise stick to ET
            # For ET, finding parent and index is hard.
            # tree = etree.parse(str(fileToModify)) # Example using lxml
            # root = tree.getroot()
            # entities_to_replace = root.xpath(f".//entity[@name='{entityToRemove}']") # lxml XPath

            # Using ElementTree (less robust finding/removal)
            tree = self.parseFile(fileToModify)
            root = tree.getroot()
            parent_map = {c: p for p in root.iter() for c in p} # Build parent map

            entity_to_replace_node: Optional[ET.Element] = None
            parent_of_entity_to_replace: Optional[ET.Element] = None

            # Find the entity node (iterative search)
            queue = [root]
            found_node = None
            while queue:
                current_node = queue.pop(0)
                if current_node.tag == 'entity' and current_node.get('name', '').lower() == entityToRemove.lower(): # Case-insensitive match like Java
                    found_node = current_node
                    break
                queue.extend(list(current_node))

            if found_node is None:
                 print(f"Entity '{entityToRemove}' not found in {fileToModify} for substitution.")
                 return

            entity_to_replace_node = found_node
            parent_of_entity_to_replace = parent_map.get(entity_to_replace_node)

            if parent_of_entity_to_replace is None:
                 print(f"Error: Could not find parent for entity '{entityToRemove}' during substitution.")
                 return

            # 2. Clone the node to add (Java uses doc.importNode or manual clone)
            # Deep copy is the Pythonic way
            try:
                 new_entity_node = self.clone(tree, entityToAddNode) # Use clone helper
            except TypeError as e:
                 print(f"Error: Could not deep copy the entity node to add: {e}. Substitution failed.")
                 return

            # 3. Remove old node and insert new node
            try:
                 # Find index for insertion (ET specific)
                 index = list(parent_of_entity_to_replace).index(entity_to_replace_node)
                 parent_of_entity_to_replace.remove(entity_to_replace_node)
                 parent_of_entity_to_replace.insert(index, new_entity_node)
                 print(f"Successfully substituted '{entityToRemove}' in {fileToModify}")
            except ValueError:
                 print(f"Error: Node '{entityToRemove}' not found in its supposed parent during substitution. Appending instead.")
                 # Fallback: just append if index fails? Java might error out.
                 parent_of_entity_to_replace.remove(entity_to_replace_node) # Ensure removal first
                 parent_of_entity_to_replace.append(new_entity_node)

            # 4. Save the modified XML
            self.saveXML(tree, fileToModify)

        except Exception as e:
            print(f"Error during entity substitution in {fileToModify}: {e}")
            traceback.print_exc()

    # Method: saveXML (private in Java) - Renamed
    def saveXML(self, doc: ET.ElementTree, fileToSave: Path) -> None:
        """
        Saves the ElementTree document to the specified file path with indentation.
        Internal helper for Java's private void saveXML(Document docToModify, File fileToModify).
        """
        try:
            # Use ET.indent for pretty printing (Python 3.9+)
            if hasattr(ET, 'indent'):
                ET.indent(doc.getroot())
            # Java uses Transformer with INDENT=yes
            doc.write(fileToSave, encoding='utf-8', xml_declaration=True)
            print(f"Saved XML changes to: {fileToSave}")
        except Exception as e:
            print(f"Error saving XML to {fileToSave}: {e}")
            traceback.print_exc()
            # Java catches TransformerException, IOException

    # Method: clone (private in Java) - Renamed
    # Note: Java clones DOM nodes. Python uses copy.deepcopy for ET elements.
    def clone(self, docToModify: ET.ElementTree, nodeToClone: ET.Element) -> ET.Element:
         """
         Clones an XML element using deepcopy.
         Internal helper roughly corresponding to Java's private Node clone(Document docToModify, Node entityToAdd).
         Note: Java's clone is more complex, handling document context.
         """
         try:
              # Using copy.deepcopy is generally the most Pythonic way for element cloning
              cloned_node = copy.deepcopy(nodeToClone)
              return cloned_node
         except Exception as e:
              print(f"Error cloning node <{nodeToClone.tag}>: {e}")
              raise # Re-raise the error

    # Method: cloneAttributes (private in Java) - Renamed
    def cloneAttributes(self, docToModify: ET.ElementTree, attributesNode: ET.Element) -> ET.Element:
        """
        Clones an <attributes> element and its children using deepcopy.
        Internal helper for Java's private Element cloneAttributes(Document docToModify, Node attributesToAdd).
        """
        return self.clone(docToModify, attributesNode)

    # Method: cloneValues (private in Java) - Renamed
    def cloneValues(self, docToModify: ET.ElementTree, valuesNode: ET.Element) -> ET.Element:
        """
        Clones a <values> or <taxonomy> element and its children recursively using deepcopy.
        Internal helper for Java's private Element cloneValues(Document docToModify, Node valuesToAdd).
        """
        return self.clone(docToModify, valuesNode)

    # Method: getTopEntities (public in Java)
    def getTopEntities(self) -> List[Entity]:
        """Returns a list of the top-level entities (direct children of the root Entity)."""
        if self.entityTree:
             return self.entityTree.getChildren() # Assuming returns List[Entity]
        return []

    # Method: getTopRelationships (public in Java)
    def getTopRelationships(self) -> List[Relationship]:
        """Returns a list of top-level relationships (direct children of the root Relationship)."""
        if self.relationshipTree:
             # Java uses toRelationships(getRelationshipTree().getChildren())
             # Assuming getChildren returns List[Entity], filter and cast
             children = self.relationshipTree.getChildren()
             return self.toRelationships(children) # Use static helper like Java
        return []

    # Method: getTopRelationshipsToString (public in Java)
    def getTopRelationshipsToString(self) -> List[str]:
        """Returns a list of names of the top-level relationships."""
        # Java uses stream().map().collect()
        return [r.getName() for r in self.getTopRelationships()]

    # Method: toRelationships (public static in Java)
    @staticmethod
    def toRelationships(entities: List[Entity]) -> List[Relationship]:
        """Converts a list of Entity objects to a list of Relationship objects by casting."""
        # Java uses stream().map(er -> (Relationship) er).collect()
        # Python equivalent with type checking:
        rels = []
        for e in entities:
            if isinstance(e, Relationship):
                rels.append(e)
            else:
                # Java would throw ClassCastException here. Python can warn or raise.
                print(f"Warning: Entity '{e.getName()}' is not a Relationship in toRelationships.")
                # Or raise TypeError(f"Entity '{e.getName()}' is not a Relationship")
        return rels

    # Method: getEntityTree (public in Java)
    def getEntityTree(self) -> Entity:
        """Returns the root of the entity tree."""
        return self.entityTree

    # Method: getRelationshipTree (public in Java)
    def getRelationshipTree(self) -> Relationship:
        """Returns the root of the relationship tree."""
        return self.relationshipTree

    # Method: getRemovedEntities (public in Java)
    def getRemovedEntities(self) -> List[str]: # Java returns ArrayList
        """Returns the list of entity names marked for removal via <deleted> tag."""
        return self.removedEntities

    # Method: getRemovedRelationships (public in Java)
    def getRemovedRelationships(self) -> List[str]: # Java returns ArrayList
        """Returns the list of relationship names marked for removal via <deleted> tag."""
        return self.removedRelationships

    # Method: properties (public in Java)
    def properties(self, entity_name: str) -> List[Attribute]: # Java returns List
        """Retrieves all attributes (including inherited) for a given entity name."""
        entity = self.getEntity(entity_name)
        # Java uses propertiesCommon(e)
        # Python version assumes Entity class handles inheritance in getAttributes or similar
        if entity:
             # Assuming Entity class has a method like getAllAttributes() that handles inheritance
             try:
                  return entity.getAllAttributes()
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllAttributes'. Returning only direct attributes for '{entity_name}'.")
                  return entity.getAttributes() # Fallback to direct attributes
        return []

    # Method: propertiesRelation (public in Java)
    def propertiesRelation(self, relation_name: str) -> List[Attribute]: # Java returns List
        """Retrieves all attributes (including inherited) for a given relationship name."""
        relationship = self.getRelationship(relation_name)
        # Java uses propertiesCommon(r)
        if relationship:
             # Assuming Relationship (as an Entity) has getAllAttributes()
             try:
                  return relationship.getAllAttributes()
             except AttributeError:
                  print(f"Warning: Relationship class missing 'getAllAttributes'. Returning only direct attributes for '{relation_name}'.")
                  return relationship.getAttributes() # Fallback
        return []

    # Method: propertiesCommon (private in Java) - Renamed
    # This logic is likely better placed within the Entity/Relationship classes themselves
    # def propertiesCommon(self, e: Optional[Entity]) -> List[Attribute]: ...

    # Method: relationName (public static in Java)
    @staticmethod
    def relationName(subject: str, relationship: str, object_ref: str) -> str:
        """Generates a standard relationship name string."""
        return f"{subject}.{relationship}.{object_ref}"

    # Method: removeEntity (public in Java)
    def removeEntity(self, name: str) -> None:
        """Removes an entity by name from the entity tree."""
        # Java finds entity then calls detach()
        entity_to_remove = self.findInTree(self.entityTree, name)
        if entity_to_remove:
            print(f"Removing entity: {name}")
            entity_to_remove.detach() # Detach from parent
            # Java code comments "// REMOVE REFERENCES AND RELATIONSHIPS" but doesn't implement it here.
            # Python version added removeReferencesInvolving. Keep it for correctness.
            self.removeReferencesInvolving(name) # Call helper to clean up refs
        else:
            print(f"Entity '{name}' not found for removal.")

    # Method: removeRelationship (public in Java)
    def removeRelationship(self, name: str) -> None:
        """Removes a relationship by name from the relationship tree."""
        # Java finds relationship then calls detach()
        rel_to_remove = self.findInTree(self.relationshipTree, name)
        if rel_to_remove and isinstance(rel_to_remove, Relationship):
            print(f"Removing relationship: {name}")
            rel_to_remove.detach() # Detach from parent
            # Java code doesn't explicitly clean up helper dicts here.
            # Python version added cleanupRelationshipData. Keep it?
            self.cleanupRelationshipData(name) # Call helper to clean up dicts/sets
        else:
            print(f"Relationship '{name}' not found for removal.")

    # Method: removeReferencesInvolving (internal helper, not in Java) - Renamed
    def removeReferencesInvolving(self, entity_name: str) -> None:
        """Internal helper to remove relationship references involving a deleted entity."""
        print(f"Removing references involving entity: {entity_name}")
        all_rels = self.getAllRelationships()
        refs_to_remove_map: Dict[Relationship, List[Reference]] = defaultdict(list)

        for rel in all_rels:
            refs_in_rel = list(rel.getReferences()) # Get a copy to iterate over while potentially modifying
            for ref in refs_in_rel:
                if ref.getSubject() == entity_name or ref.getObject() == entity_name:
                    refs_to_remove_map[rel].append(ref)
                    # Clean up helper dicts immediately for this specific reference
                    self.cleanupReferenceData(ref.getSubject(), rel.getName(), ref.getObject())

            # Remove the collected references from the relationship
            if rel in refs_to_remove_map:
                 current_refs = rel.getReferences()
                 # Create a new list excluding the ones to remove
                 updated_refs = [r for r in current_refs if r not in refs_to_remove_map[rel]]
                 try:
                      rel.setReferences(updated_refs) # Assuming setReferences exists
                 except AttributeError:
                      print(f"Warning: Relationship class missing 'setReferences'. Cannot remove references involving '{entity_name}' from '{rel.getName()}'.")


    # Method: cleanupRelationshipData (internal helper, not in Java) - Renamed
    def cleanupRelationshipData(self, rel_name: str) -> None:
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
        # Iterate over copies of keys/items to avoid modification issues
        for key, values in list(self.subjRels.items()):
            if rel_name in values: self.removeValue(self.subjRels, key, rel_name)
        for key, values in list(self.objRels.items()):
            if rel_name in values: self.removeValue(self.objRels, key, rel_name)
        for key in list(self.subjRel_Objs.keys()):
            if key.endswith(f".{rel_name}"): self.subjRel_Objs.pop(key, None)
        for key, values in list(self.subjObj_Rels.items()):
            if rel_name in values: self.removeValue(self.subjObj_Rels, key, rel_name)
        for key in list(self.relObj_Subjs.keys()):
            if key.startswith(f"{rel_name}."): self.relObj_Subjs.pop(key, None)

        # Remove from subjRelObjs set
        self.subjRelObjs = {sro for sro in self.subjRelObjs if f".{rel_name}." not in sro}

    # Method: cleanupReferenceData (internal helper, not in Java) - Renamed
    def cleanupReferenceData(self, subject: str, rel_name: str, object_ref: str) -> None:
        """Internal helper to remove data for a specific deleted reference."""
        subj_rel_obj_str = f"{subject}.{rel_name}.{object_ref}"
        subj_rel_key = f"{subject}.{rel_name}"
        subj_obj_key = f"{subject}.{object_ref}"
        rel_obj_key = f"{rel_name}.{object_ref}"

        if subj_rel_obj_str in self.subjRelObjs:
             self.subjRelObjs.remove(subj_rel_obj_str)
             if self.nRelRefs > 0: self.nRelRefs -= 1 # Decrement count only if successfully removed

        self.removeValue(self.subjRels, subject, rel_name)
        self.removeValue(self.subjObjs, subject, object_ref)
        self.removeValue(self.relSubjs, rel_name, subject)
        self.removeValue(self.relObjs, rel_name, object_ref)
        self.removeValue(self.objRels, object_ref, rel_name)
        self.removeValue(self.objSubjs, object_ref, subject)
        self.removeValue(self.subjRel_Objs, subj_rel_key, object_ref)
        self.removeValue(self.subjObj_Rels, subj_obj_key, rel_name)
        self.removeValue(self.relObj_Subjs, rel_obj_key, subject)

    # Method: removeValue (internal helper, not in Java) - Renamed
    def removeValue(self, map_dict: Dict[str, List[str]], key: str, value: str) -> None:
        """ Safely removes a value from a list within a dictionary. Cleans up empty lists/keys."""
        if key in map_dict:
            try:
                map_dict[key].remove(value)
                if not map_dict[key]: # If list becomes empty
                    del map_dict[key]
            except ValueError:
                pass # Value wasn't in the list

    # Method: readAttributes (private in Java) - Renamed
    def readAttributes(self, parentNode: ET.Element) -> List[Attribute]: # Java returns Vector
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
            self.validateTagAttributes(attr_node, valid_attr_attrs, "name")

            attr_name = attr_node.get("name")
            # Java defaults datatype to "" if not present, let's default to "string" for clarity
            data_type = attr_node.get("datatype", "string")
            description = attr_node.get("description", "") # Default to empty string like Java
            notes = attr_node.get("notes") # Get notes (new in Python version?)

            if not attr_name:
                 raise ValueError("<attribute> tag requires a 'name' attribute.") # Java doesn't check null

            # Initialize attribute (Java: new Attribute(attribute,datatype))
            currentAttr = Attribute(name=attr_name, data_type=data_type)
            currentAttr.setDescription(description)
            if notes is not None: currentAttr.setNotes(notes) # Set notes if present

            # Set optional boolean flags (Java uses setOptionalAttributes helper)
            self.setOptionalAttributes(attr_node.attrib, currentAttr)

            # Handle datatype specific logic (Java switch statement)
            if data_type == "select":
                 # Java: currentAttr.setValuesString(readValuesList(an,"value",true));
                 values = self.readValuesList(attr_node, "value", True) # Read <value> children, add "Other"
                 currentAttr.setValues(values) # Assuming setValues takes List[str]
            elif data_type == "tree":
                 # Java: currentAttr.setSubClasses(readValuesTree(an,null));
                 # readValuesTree expects the root of the tree structure (<attribute> or <value>)
                 # It returns a DefaultTreeNode
                 sub_classes_tree = self.readValuesTree(attr_node, None) # Pass None as parent for the root call
                 currentAttr.setSubClasses(sub_classes_tree) # Assuming setSubClasses takes TreeNode
            elif data_type == "entity":
                 # Java: currentAttr.setTarget(n.getNamedItem("target").getNodeValue());
                 target = attr_node.get("target")
                 if target is None: # Java would throw NullPointerException here
                      raise ValueError("<attribute> with datatype='entity' requires a 'target' attribute.")
                 currentAttr.setTarget(target)
            elif data_type == "user-types":
                 # Java: String target = n.getNamedItem("target").getNodeValue();
                 target_type_name = attr_node.get("target")
                 if target_type_name is None:
                      raise ValueError("<attribute> with datatype='user-types' requires a 'target' attribute.")

                 # Find the predefined type from self.types (Java: fromAttributesToString(types).contains(target))
                 found_type = next((t for t in self.types if t.getName() == target_type_name), None)
                 if found_type:
                      try:
                           # Java: currentAttr = (Attribute) type.clone();
                           cloned_type = found_type.clone() # Assumes Attribute.clone() exists and works
                           # Java overrides name, description, and optional flags after cloning
                           cloned_type.setName(attr_name)
                           cloned_type.setDescription(description)
                           if notes is not None: cloned_type.setNotes(notes)
                           self.setOptionalAttributes(attr_node.attrib, cloned_type)
                           currentAttr = cloned_type # Replace the initially created attribute
                      except Exception as e: # Catch potential clone errors (Java catches CloneNotSupportedException)
                           print(f"Error cloning user type '{target_type_name}' for attribute '{attr_name}': {e}")
                           raise ValueError(f"Failed to clone user type '{target_type_name}'") from e
                 else:
                      # Java doesn't explicitly raise error here, but clone would fail.
                      raise ValueError(f"Target user type '{target_type_name}' not found for attribute '{attr_name}'. Ensure it's defined in <user-types>.")
            # Add other datatypes (string, int, etc.) if needed - handled by default Attribute init

            fullAttrs.append(currentAttr)

        return fullAttrs

    # Method: fromAttributesToString (private in Java) - Renamed
    def fromAttributesToString(self, attributes: List[Attribute]) -> List[str]: # Java returns Vector
        """Converts a list of Attribute objects to a list of their names."""
        # Java uses stream().map().collect(Collectors.toCollection(Vector::new))
        return [a.getName() for a in attributes if a.getName() is not None]

    # Method: fromTypesToString (private in Java) - Renamed
    # This might not be needed if UType isn't used explicitly
    # def fromTypesToString(self, types: List[UType]) -> List[str]: # Java returns Vector
    #     """Converts a list of UType objects to a list of their names."""
    #     return [t.getName() for t in types if t.getName() is not None]

    # Method: readValuesList (private in Java) - Renamed
    def readValuesList(self, parentNode: ET.Element, tag_name: str, add_other: bool) -> List[str]: # Java returns List
        """
        Reads child elements with tag_name under parentNode and returns their 'name' attributes as a list.
        Internal helper for Java's private List<String> readValuesList(Node parentNode, String tag_name, boolean add_other).
        """
        values: List[str] = []
        valid_value_attrs = ["name"] # Java validates name attribute

        value_nodes = [child for child in parentNode if isinstance(child.tag, str) and child.tag == tag_name]

        for value_node in value_nodes:
             self.validateTag(value_node, [tag_name]) # Java validates tag
             self.validateTagAttributes(value_node, valid_value_attrs, "name") # Java validates attributes
             value_name = value_node.get("name")
             if value_name is not None: # Java gets value, might throw NPE later if null
                  values.append(value_name)
             else:
                  raise ValueError(f"<{tag_name}> tag requires a 'name' attribute.")

        if add_other: # Java adds "Other" conditionally
             values.append("Other")
        return values

    # Method: readValuesTree (private in Java) - Renamed
    # Note: Java returns org.primefaces.model.DefaultTreeNode, Python uses local DefaultTreeNode
    def readValuesTree(self, parentXmlNode: ET.Element, parentTreeNode: Optional[DefaultTreeNode]) -> DefaultTreeNode:
        """
        Recursively parses <value> tags under parentXmlNode to build a DefaultTreeNode structure.
        Internal helper for Java's private DefaultTreeNode readValuesTree(Node parentNode, DefaultTreeNode parent).
        """
        # Determine the data for the current TreeNode based on Java logic
        node_data: str
        if parentXmlNode.tag == "attribute":
             # Root of the tree definition (within <attribute datatype="tree">)
             node_data = "- Select one -" # Special root node label from Java
        elif parentXmlNode.tag == "value":
             node_data = parentXmlNode.get("name")
             if node_data is None: # Java gets attribute, might throw NPE later
                  raise ValueError("<value> tag within a tree structure requires a 'name' attribute.")
        else:
             raise ValueError(f"Unexpected tag '{parentXmlNode.tag}' encountered in readValuesTree.")

        # Create the TreeNode for the current XML node
        # Java: DefaultTreeNode treeNode = new DefaultTreeNode(name, parent); (adds to parent implicitly)
        # Ensure Python DefaultTreeNode constructor handles parent linking or do it manually.
        currentTreeNode = DefaultTreeNode(data=node_data, parent=parentTreeNode)
        # Assuming constructor handles linking. If not:
        # if parentTreeNode: parentTreeNode.add_child(currentTreeNode)

        valid_value_attrs = ["name"] # Java validates name attribute

        value_nodes = [child for child in parentXmlNode if isinstance(child.tag, str) and child.tag == "value"]

        for childXmlNode in value_nodes:
             self.validateTag(childXmlNode, ["value"]) # Java validates tag
             self.validateTagAttributes(childXmlNode, valid_value_attrs, "name") # Java validates attributes

             # Recursive call to build the subtree
             childTreeNode = self.readValuesTree(childXmlNode, currentTreeNode)
             # If constructor doesn't add child, do it here:
             # currentTreeNode.add_child(childTreeNode) # If needed

             # Java code adds an "Other <name>" node if the child has further children (is not a leaf)
             if not childTreeNode.isLeaf(): # Assuming isLeaf() method exists
                  other_node_data = f"Other {childXmlNode.get('name')}"
                  # Java: new DefaultTreeNode("Other " + child.getAttributes().getNamedItem("name").getNodeValue(), subtree);
                  # Creates the "Other" node as a child of the *childTreeNode*
                  DefaultTreeNode(data=other_node_data, parent=childTreeNode) # Assuming constructor links to parent

        return currentTreeNode

    # Method: addValue (private in Java) - Renamed
    def addValue(self, map_dict: Dict[str, List[str]], key: str, value: str) -> None: # Java map value is Vector
        """
        Adds a value to a list within a dictionary, ensuring no duplicates in the list. Sorts the list.
        Internal helper for Java's private void addValue(Map<String,Vector<String>> map, String key, String value).
        """
        # Java uses map.get(key), checks null, creates new Vector if needed. defaultdict simplifies this.
        if value not in map_dict[key]: # Check for duplicates before adding
            map_dict[key].append(value)
            map_dict[key].sort() # Java sorts after adding

    # Method: setOptionalAttributes (private in Java) - Renamed
    def setOptionalAttributes(self, attrib_map: Dict[str, str], attr_obj: Attribute) -> None:
        """
        Sets optional boolean attributes (mandatory, distinguishing, display) on an Attribute object based on string values ("true"/"false").
        Internal helper for Java's private void setOptionalAttributes(NamedNodeMap n, Attribute a).
        """
        # Java checks attribute presence and compares value to "true"
        # Mandatory
        mandatory_str = attrib_map.get("mandatory") # Get value or None
        attr_obj.setMandatory(mandatory_str == "true") # Compare to "true"

        # Distinguishing
        distinguishing_str = attrib_map.get("distinguishing")
        attr_obj.setDistinguishing(distinguishing_str == "true")

        # Display
        display_str = attrib_map.get("display")
        attr_obj.setDisplay(display_str == "true")

    # Method: getInverseRel (public in Java)
    def getInverseRel(self, relationship_name: str) -> Optional[str]: # Java returns String
        """Gets the inverse relationship name for the given relationship name."""
        # Java: return getRelationship(relationship).getInverse(); (Might throw NPE if relationship not found)
        relationship = self.getRelationship(relationship_name)
        if relationship:
            return relationship.getInverse()
        return None # Return None if relationship not found

    # Method: getDomain (public in Java)
    def getDomain(self) -> Optional[str]: # Java returns String
        """Returns the primary domain name associated with this DomainData instance."""
        return self.domain

    # Method: getEntitiesNotRemoved (public in Java)
    def getEntitiesNotRemoved(self, toRemove: Optional[List[str]] = None) -> List[Entity]: # Java returns List, takes ArrayList
        """Returns a list of top-level entities, filtering out those in the optional toRemove list."""
        # Java logic: get top entities, create removal list, removeAll, return result.
        top_entities = list(self.getTopEntities()) # Get a mutable copy
        entities_to_remove_names = toRemove if toRemove is not None else self.removedEntities

        if not entities_to_remove_names:
            return top_entities # No filtering needed

        # Filter based on names
        result = [e for e in top_entities if e.getName() not in entities_to_remove_names]
        return result

    # Method: getAllEntities (public in Java)
    def getAllEntities(self) -> List[Entity]: # Java returns Vector
        """Returns a flat list of all entities in the tree (including sub-entities)."""
        # Java uses recursion via getAllChildren. Python iterative approach:
        all_entities: List[Entity] = []
        if not self.entityTree:
            return all_entities

        queue = list(self.entityTree.getChildren()) # Start with top-level entities
        # Use id() for visited set as Entity objects are not hashable by default
        visited: Set[int] = {id(self.entityTree)} # Store object IDs

        while queue:
            current_entity = queue.pop(0)
            current_entity_id = id(current_entity)

            if current_entity_id in visited: continue
            visited.add(current_entity_id)

            all_entities.append(current_entity)
            # Add children to the queue for processing
            try:
                 children = current_entity.getChildren()
                 queue.extend(children)
            except AttributeError:
                 print(f"Warning: Entity '{current_entity.getName()}' lacks 'getChildren' method in getAllEntities.")
            except Exception as e:
                 print(f"Error getting children for entity '{current_entity.getName()}' in getAllEntities: {e}")


        return all_entities

    # Method: getAllEntitiesToString (public in Java)
    def getAllEntitiesToString(self) -> List[str]: # Java returns Vector
        """Returns a flat list of names of all entities in the tree."""
        # Java uses recursion via getAllChildrenToString. Python using getAllEntities:
        return [e.getName() for e in self.getAllEntities()]

    # Method: getRelationship (public in Java - overloaded)
    # Version 1: getRelationship(String relName)
    def getRelationship(self, relName: str) -> Optional[Relationship]: # Java returns Relationship
        """Retrieves a relationship by its name by searching the relationship tree."""
        # Java searches top level, then recursively calls helper.
        # Python findInTree already searches recursively.
        found_entity = self.findInTree(self.relationshipTree, relName)
        if found_entity and isinstance(found_entity, Relationship):
            return found_entity
        return None

    # Version 2: getRelationship(String relName, ArrayList<Relationship> topRels) - Not directly needed if findInTree works

    # Method: getAllRelationships (public in Java)
    def getAllRelationships(self) -> List[Relationship]: # Java returns List
        """Returns a flat list of all relationships in the tree (including sub-relationships)."""
        # Java uses Stack based iteration.
        all_rels: List[Relationship] = []
        if not self.relationshipTree:
            return all_rels

        stack: List[Relationship] = list(self.getTopRelationships()) # Start with top-level relationships
        visited = {self.relationshipTree} # Avoid cycles/reprocessing

        while stack:
            current_rel = stack.pop()
            if current_rel in visited: continue
            visited.add(current_rel)

            all_rels.append(current_rel)
            # Add children relationships to stack
            # Assuming getChildren returns List[Entity], filter for Relationships
            children_rels = [child for child in current_rel.getChildren() if isinstance(child, Relationship)]
            stack.extend(reversed(children_rels)) # Add in reverse to mimic stack push order

        return all_rels

    # Method: getAllRelationshipsToString (public in Java)
    def getAllRelationshipsToString(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of names of all relationships in the tree."""
        # Java uses stream().map().collect(Collectors.toCollection(TreeSet::new))
        names = {r.getName() for r in self.getAllRelationships()}
        return sorted(list(names)) # Return sorted list to mimic TreeSet ordering

    # Method: getAllChildren (private in Java) - Renamed
    # Note: Used internally by Java's getAllEntities. Python version uses iteration.
    def getAllChildren(self, e: Entity) -> List[Entity]: # Java returns Vector
        """Recursively gets all children (entities) of a given entity."""
        children_list: List[Entity] = []
        for child in e.getChildren():
            children_list.append(child)
            children_list.extend(self.getAllChildren(child)) # Recursive call
        return children_list

    # Method: getAllChildrenToString (private in Java) - Renamed
    # Note: Used internally by Java's getAllEntitiesToString. Python version uses iteration.
    def getAllChildrenToString(self, e: Entity) -> List[str]: # Java returns Vector
        """Recursively gets names of all children (entities) of a given entity."""
        names_list: List[str] = []
        for child in e.getChildren():
            names_list.append(child.getName())
            names_list.extend(self.getAllChildrenToString(child)) # Recursive call
        return names_list

    # Method: getTopEntitiesToString (public in Java)
    def getTopEntitiesToString(self) -> List[str]: # Java returns Vector
        """Returns a list of names of the top-level entities."""
        # Java iterates and adds name.
        return [e.getName() for e in self.getTopEntities()]

    # Method: getSubjsFromRel (public in Java - overloaded)
    # Version 1: getSubjsFromRel(String relationship)
    def getSubjsFromRel(self, relationship_name: str) -> Set[str]: # Java returns TreeSet
        """Gets all unique subjects associated with a given relationship name (including inheritance)."""
        # Java iterates all relationships, finds match, calls r.getSubjects()
        relationship = self.getRelationship(relationship_name)
        if relationship:
            # Assuming Relationship class has getSubjects() that handles inheritance/all references
            # and returns a Set or compatible type.
            try:
                 subjects = relationship.getSubjects()
                 return set(subjects) # Ensure it's a set
            except AttributeError:
                 print(f"Warning: Relationship class missing 'getSubjects'. Cannot get subjects for '{relationship_name}'.")
                 return set()
        return set() # Return empty set if relationship not found

    # Method: getObjsFromRel (public in Java - overloaded)
    # Version 1: getObjsFromRel(String relationship)
    def getObjsFromRel(self, relationship_name: str) -> Set[str]: # Java returns TreeSet
        """Gets all unique objects associated with a given relationship name (including inheritance)."""
        # Java iterates all relationships, finds match, calls r.getObjects()
        relationship = self.getRelationship(relationship_name)
        if relationship:
            # Assuming Relationship class has getObjects() that handles inheritance/all references
            try:
                 objects = relationship.getObjects()
                 return set(objects) # Ensure it's a set
            except AttributeError:
                 print(f"Warning: Relationship class missing 'getObjects'. Cannot get objects for '{relationship_name}'.")
                 return set()
        return set()

    # Method: getSubjects (public in Java)
    def getSubjects(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of all unique subjects found in references."""
        # Java returns new TreeSet<String>(subjects)
        return sorted(list(set(self.subjects))) # Ensure uniqueness and sort

    # Method: getObjects (public in Java)
    def getObjects(self) -> List[str]: # Java returns TreeSet (sorted set)
        """Returns a sorted list of all unique objects found in references."""
        # Java returns new TreeSet<String>(objects)
        return sorted(list(set(self.objects))) # Ensure uniqueness and sort

    # Method: getSubjObj_Rels (public in Java)
    def getSubjObj_Rels(self, subject: str, object_ref: str) -> Set[str]: # Java returns Set
        """Gets the set of relationship names connecting a specific subject to a specific object."""
        # Java: return new HashSet<String>(subjObj_Rels.get(subject + "." + object));
        key = f"{subject}.{object_ref}"
        # Return a copy to prevent external modification
        return set(self.subjObj_Rels.get(key, []))

    # --- Scaraggi Getters/Setters ---
    # Note: These match the public fields/getters/setters added at the end of the Java class

    # Method: getInverseRels (public in Java)
    def getInverseRels(self) -> Dict[str, str]: # Java returns Map
        return self.inverseRels
    # Method: setInverseRels (public in Java)
    def setInverseRels(self, inverseRels: Dict[str, str]) -> None:
        self.inverseRels = inverseRels

    # Method: getRelSubjs (public in Java)
    def getRelSubjs(self) -> Dict[str, List[str]]: # Java returns Map<String, Vector<String>>
        return self.relSubjs
    # Method: setRelSubjs (public in Java)
    def setRelSubjs(self, relSubjs: Dict[str, List[str]]) -> None: # Java takes Map<String, Vector<String>>
        self.relSubjs = relSubjs

    # Method: getRelObjs (public in Java)
    def getRelObjs(self) -> Dict[str, List[str]]: # Java returns Map<String, Vector<String>>
        return self.relObjs
    # Method: setRelObjs (public in Java)
    def setRelObjs(self, relObjs: Dict[str, List[str]]) -> None: # Java takes Map<String, Vector<String>>
        self.relObjs = relObjs

    # Method: getAttrsRel (public in Java)
    def getAttrsRel(self) -> Dict[str, List[Attribute]]: # Java returns Map<String, Vector<Attribute>>
        return self.attrsRel
    # Method: setAttrsRel (public in Java)
    def setAttrsRel(self, attrsRel: Dict[str, List[Attribute]]) -> None: # Java takes Map<String, Vector<Attribute>>
        self.attrsRel = attrsRel

    # Method: getInverse (public in Java)
    def getInverse(self) -> Optional[str]: # Java returns String
        return self.inverse
    # Method: setInverse (public in Java)
    def setInverse(self, inverse: str) -> None:
        self.inverse = inverse

    # Method: getDomainList (public in Java)
    def getDomainList(self) -> Optional[List[str]]: # Java returns ArrayList
        return self.domainList
    # Method: setDomainList (public in Java)
    def setDomainList(self, domainList: List[str]) -> None: # Java takes ArrayList
        self.domainList = domainList
    # --- End Scaraggi Getters/Setters ---

    # Method: getRelationshipsToString (public in Java, name mismatch with return type)
    # Java name is getRelationshipsToString but returns Vector<Relationship>
    def getRelationshipsToString(self, entity_name: str) -> List[Relationship]: # Java returns Vector<Relationship>
        """Retrieves relationships where the given entity name is either subject or object."""
        # Java iterates all relationships, checks subjects/objects sets.
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            # Check direct references (Java uses r.getSubjects().contains(entity) || r.getObjects().contains(entity))
            # Assuming getSubjects/getObjects on Relationship return sets of names for that relationship and its children
            try:
                 if entity_name in rel.getSubjects() or entity_name in rel.getObjects():
                      includes.append(rel)
            except AttributeError:
                 print(f"Warning: Relationship class missing 'getSubjects' or 'getObjects'. Cannot check involvement for '{entity_name}' in '{rel.getName()}'.")
        return includes

    # Method: getRelationshipsForSubj (public in Java)
    def getRelationshipsForSubj(self, entity_name: str) -> List[Relationship]: # Java returns List
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the subject."""
        # Java iterates all relationships, checks r.getSubjects().contains(entity)
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            try:
                 if entity_name in rel.getSubjects(): # Assumes getSubjects checks inheritance if needed
                     includes.append(rel)
            except AttributeError:
                 print(f"Warning: Relationship class missing 'getSubjects'. Cannot check subject involvement for '{entity_name}' in '{rel.getName()}'.")
        return includes

    # Method: getRelationshipsForObj (public in Java)
    def getRelationshipsForObj(self, entity_name: str) -> List[Relationship]: # Java returns List
        """Retrieves relationships where the given entity name (or potentially its subclasses) is the object."""
        # Java iterates all relationships, checks r.getObjects().contains(entity)
        includes: List[Relationship] = []
        for rel in self.getAllRelationships():
            try:
                 if entity_name in rel.getObjects(): # Assumes getObjects checks inheritance if needed
                     includes.append(rel)
            except AttributeError:
                 print(f"Warning: Relationship class missing 'getObjects'. Cannot check object involvement for '{entity_name}' in '{rel.getName()}'.")
        return includes

    # Method: getImportedFiles (public in Java)
    def getImportedFiles(self) -> List[str]: # Java returns List
        """Returns the list of absolute paths of imported .gbs files."""
        return self.importedFiles

    # Method: getEntity (public in Java)
    def getEntity(self, entityName: str) -> Optional[Entity]: # Java returns Entity
        """Retrieves an entity by its name by searching the entity tree."""
        # Java iterates top entities, then calls getSubEntity recursively.
        # Python findInTree already searches recursively.
        return self.findInTree(self.entityTree, entityName)

    # Method: getSubEntity (public in Java) - Seems redundant if findInTree works
    # def getSubEntity(self, entities: List[Entity], entityName: str) -> Optional[Entity]: ...

    # Method: removeEntities (public in Java)
    def removeEntities(self, entities_to_remove: List[Entity]) -> None: # Java takes List
        """Removes a list of entity objects from the tree if their domain differs from the main domain."""
        # Java iterates and removes from getTopEntities() if domain is different.
        top_entities = self.getTopEntities() # Get the list
        removed_count = 0
        # Iterate backwards to avoid index issues when removing
        for i in range(len(top_entities) - 1, -1, -1):
            e = top_entities[i]
            if e in entities_to_remove: # Check if the specific object is in the list to remove
                 if e.getDomain() != self.domain:
                      print(f"Removing entity '{e.getName()}' due to domain mismatch ('{e.getDomain()}' != '{self.domain}')")
                      try:
                           # Use detach or removeChild if available
                           e.detach()
                           removed_count += 1
                      except Exception as ex:
                           print(f"Error removing entity {e.getName()}: {ex}")

        print(f"Removed {removed_count} entities based on domain mismatch.")


    # Method: removeRelationships (public in Java)
    def removeRelationships(self, domainToRemove: str) -> None:
        """Removes all relationships belonging to a specific domain."""
        # Java finds all relationships, filters by domain, then calls removeRelationship for each.
        rels_to_remove = [r for r in self.getAllRelationships() if r.getDomain() == domainToRemove]
        print(f"Removing {len(rels_to_remove)} relationships belonging to domain: {domainToRemove}")
        for r in rels_to_remove:
            self.removeRelationship(r.getName()) # Call the existing remove method

    # Method: findInTree (public in Java)
    def findInTree(self, parent: Entity, nodeName: str) -> Optional[Entity]: # Java returns Entity
        """
        Finds the entity/relationship with the given name in the tree starting from parent (DFS).
        Case-insensitive search matching Java behavior.
        Includes checks for None names and visited nodes.
        """
        if not parent:
            return None

        # Use a set to keep track of visited nodes to prevent infinite loops
        visited: Set[Entity] = set()
        # Initialize stack with children of the parent node
        try:
            # Ensure getChildren exists and handle potential errors
            if not hasattr(parent, 'getChildren'):
                 print(f"Warning: Parent node {type(parent)} lacks getChildren method in findInTree.")
                 return None
            initial_children = parent.getChildren()
            stack: List[Entity] = list(initial_children)
            visited.update(initial_children) # Mark initial children as visited
        except Exception as e:
            print(f"Error getting initial children from parent {parent.getName() if hasattr(parent, 'getName') else type(parent)}: {e}")
            return None


        while stack:
            current_node = stack.pop()

            # --- Safely get the name ---
            current_node_name: Optional[str] = None
            try:
                if hasattr(current_node, 'getName'):
                    current_node_name = current_node.getName()
                else:
                    print(f"Warning: Node encountered in findInTree does not have getName method: {type(current_node)}")
                    continue # Skip this node
            except Exception as e:
                print(f"Warning: Error calling getName() on node {type(current_node)}: {e}")
                continue # Skip this node

            # --- Perform comparison only if name is not None ---
            if current_node_name is not None and current_node_name.lower() == nodeName.lower():
                return current_node

            # --- Add children to stack for further exploration ---
            if hasattr(current_node, 'getChildren'):
                try:
                    children = current_node.getChildren()
                    # Add children that haven't been visited yet
                    for child in reversed(children):
                         # Ensure child is not None and hasn't been visited
                         if child is not None and child not in visited:
                              visited.add(child)
                              stack.append(child)
                         elif child is None:
                              print(f"Warning: Encountered a None child for node '{current_node_name or type(current_node)}' in findInTree.")
                except Exception as e:
                    print(f"Warning: Error calling getChildren() on node '{current_node_name or type(current_node)}': {e}")
            # else: Node might be a leaf or not have children concept

        return None # Node not found

    # Method: getnTopEntities (public in Java)
    def getnTopEntities(self) -> int:
        """Returns the number of top-level entities."""
        return len(self.getTopEntities())

    # Method: getnSubEntities (public in Java)
    def getnSubEntities(self) -> int:
        """Returns the number of non-top-level entities."""
        # Java: getAllEntitiesToString().size()-getnTopEntities();
        # Note: getAllEntitiesToString includes top-level entities.
        return len(self.getAllEntitiesToString()) - self.getnTopEntities()

    # Method: getnTopRels (public in Java)
    def getnTopRels(self) -> int:
        """Returns the number of top-level relationships."""
        # Java: relationshipTree.getChildren().size();
        return len(self.getTopRelationships())

    # Method: getnRelRefs (public in Java)
    def getnRelRefs(self) -> int:
        """Returns the total number of relationship references parsed."""
        return self.nRelRefs

    # Method: readFile (static in Java)
 # Method: readFile (static in Java)
    @staticmethod
    def readFile(path: str, encoding: str = 'utf-8') -> str: # Java takes Charset
        """Reads a file and returns its content as a string."""
        # Java uses Files.readAllBytes and new String(bytes, encoding)
        try:
            # Use Path object for better path handling
            file_path = Path(path)
            with file_path.open('r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found at path {path}")
            raise # Re-raise FileNotFoundError
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            raise # Java throws IOException, Python raises general Exception or specific ones like UnicodeDecodeError

    # Method: getRelationshipsWithSubj (public in Java)
    def getRelationshipsWithSubj(self, subject: str) -> Set[str]: # Java returns TreeSet
        """Retrieves the names of top-level relationships involving the subject (or its subclasses)."""
        relationships: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject) # Find entity for inheritance check

        # Get all types this subject could represent (itself + subclasses)
        subj_types: Set[str] = {subject.lower()} # Use lower case for comparison
        if subj_entity:
             try:
                  # Assuming getAllSubclassNames includes the entity itself and returns lowercase names
                  # Java's findInTree(subjEntity, ref.getSubject()) checks if ref.getSubject() is a descendant of subjEntity
                  # Python equivalent: check if ref.getSubject() is in the set of subclass names
                  subclass_names = {sub.lower() for sub in subj_entity.getAllSubclassNames(subclassRestriction=False)}
                  subj_types.update(subclass_names)
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getRelationshipsWithSubj might be incomplete.")

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                # Check if the reference's subject is the target subject or one of its subclasses
                if ref.getSubject().lower() in subj_types:
                    # Add the top-level ancestor relationship name
                    try:
                         # Java uses r.getTop() - assuming Relationship has getTop() returning name
                         top_rel_name = rel.getTop()
                         relationships.add(top_rel_name)
                    except AttributeError:
                         print(f"Warning: Relationship class missing 'getTop'. Cannot determine top relationship for '{rel.getName()}'. Using direct name.")
                         relationships.add(rel.getName()) # Fallback
                    break # Found one match for this relationship, move to next rel
        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(relationships))
        return relationships

    # Method: getRelationshipsWithObj (public in Java)
    def getRelationshipsWithObj(self, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves the names of top-level relationships involving the object (or its subclasses)."""
        relationships: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref) # Find entity for inheritance check

        obj_types: Set[str] = {object_ref.lower()} # Use lower case
        if obj_entity:
             try:
                  # Java's findInTree(objEntity, ref.getObject()) checks for descendants
                  subclass_names = {sub.lower() for sub in obj_entity.getAllSubclassNames(subclassRestriction=False)}
                  obj_types.update(subclass_names)
             except AttributeError:
                  print(f"Warning: Entity class missing 'getAllSubclassNames'. Inheritance check in getRelationshipsWithObj might be incomplete.")

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                # Check if the reference's object is the target object or one of its subclasses
                if ref.getObject().lower() in obj_types:
                    try:
                         top_rel_name = rel.getTop()
                         relationships.add(top_rel_name)
                    except AttributeError:
                         print(f"Warning: Relationship class missing 'getTop'. Cannot determine top relationship for '{rel.getName()}'.")
                         relationships.add(rel.getName())
                    break # Found one match for this relationship, move to next rel
        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(relationships))
        return relationships

    # Method: getObjsFromRel (public in Java - overloaded)
    # Version 2: getObjsFromRel(List<String> relationships)
    def getObjsFromRel(self, relationships: List[str]) -> List[str]: # Java returns Vector
        """Retrieves unique objects from a list of relationship names."""
        # Java uses TreeSet to collect unique objects, then returns Vector
        objects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                # Java iterates only direct references in this version
                for ref in rel.getReferences():
                    objects_set.add(ref.getObject())
                # If inheritance is needed here (like in getObjsFromRel(String)), the logic would be different.
                # Based on Java code, it seems only direct references are considered in this overload.

        return sorted(list(objects_set)) # Return sorted list to mimic TreeSet -> Vector

    # Method: getSubjsFromRel (public in Java - overloaded)
    # Version 2: getSubjsFromRel(List<String> relationships)
    def getSubjsFromRel(self, relationships: List[str]) -> List[str]: # Java returns Vector
        """Retrieves unique subjects from a list of relationship names."""
        # Java uses HashSet to collect unique subjects, then returns Vector
        subjects_set: Set[str] = set()
        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                # Java iterates only direct references in this version
                for ref in rel.getReferences():
                    subjects_set.add(ref.getSubject())
                # If inheritance is needed, logic would differ. Java code suggests direct refs only.

        return sorted(list(subjects_set)) # Return sorted list

    # Method: getObjsFromSubjRel (public in Java)
    def getObjsFromSubjRel(self, subject: str, relName: str) -> Set[str]: # Java returns TreeSet
        """Retrieves objects related to a subject via a specific relationship (considering inheritance)."""
        objects_set: Set[str] = set()
        rel = self.getRelationship(relName)
        if not rel: return set()

        subj_entity = self.findInTree(self.entityTree, subject) # Find entity for inheritance check

        try:
            direct_references = rel.getReferences()
        except AttributeError:
            print(f"Warning: Relationship class missing 'getReferences' for '{relName}'.")
            return set()
        # --- End Correction ---

        for ref in direct_references: # Use direct_references now
            # Java check: ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null
            # This means: is the ref subject the exact subject OR a descendant of the subject?
            is_match = False
            ref_subject_name = ref.getSubject() # Avoid multiple calls
            if ref_subject_name: # Check if subject name is not None
                is_match = ref_subject_name.lower() == subject.lower()
                if not is_match and subj_entity:
                    # Check if ref.getSubject() is a descendant of subj_entity
                    # Ensure findInTree handles None gracefully if subj_entity is None
                    descendant_check = self.findInTree(subj_entity, ref_subject_name)
                    is_match = descendant_check is not None

            if is_match:
                objects_set.add(ref.getObject())

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed for consistency.
        # return sorted(list(objects_set))
        return objects_set

    # Method: getSubjsFromObjRel (public in Java)
    def getSubjsFromObjRel(self, object_ref: str, relName: str) -> Set[str]: # Java returns TreeSet
        """Retrieves subjects related to an object via a specific relationship (considering inheritance)."""
        subjects_set: Set[str] = set()
        rel = self.getRelationship(relName)
        if not rel: return set()

        obj_entity = self.findInTree(self.entityTree, object_ref) # Find entity for inheritance check

        try:
            direct_references = rel.getReferences()
        except AttributeError:
            print(f"Warning: Relationship class missing 'getReferences' for '{relName}'.")
            return set()
        # --- End Correction ---

        for ref in direct_references: # Use direct_references now
            # Java check: ref.getObject().equals(object) || findInTree(parent, ref.getObject())!=null
            is_match = False
            ref_object_name = ref.getObject() # Avoid multiple calls
            if ref_object_name: # Check if object name is not None
                is_match = ref_object_name.lower() == object_ref.lower()
                if not is_match and obj_entity:
                    # Ensure findInTree handles None gracefully if obj_entity is None
                    descendant_check = self.findInTree(obj_entity, ref_object_name)
                    is_match = descendant_check is not None

            if is_match:
                subjects_set.add(ref.getSubject())

        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(subjects_set))
        return subjects_set

    # Method: getRelFromSubjObj (public in Java)
    def getRelFromSubjObj(self, subject: str, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves top-level relationship names connecting a subject and object (considering inheritance)."""
        rels_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)
        obj_entity = self.findInTree(self.entityTree, object_ref)

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                # Check subject inheritance: ref.getSubject().equals(subject) || findInTree(parentSubject, ref.getSubject())!=null
                subj_match = ref.getSubject().lower() == subject.lower()
                if not subj_match and subj_entity:
                     subj_match = self.findInTree(subj_entity, ref.getSubject()) is not None

                # Check object inheritance: ref.getObject().equals(object) || findInTree(parentObject, ref.getObject())!=null
                obj_match = ref.getObject().lower() == object_ref.lower()
                if not obj_match and obj_entity:
                     obj_match = self.findInTree(obj_entity, ref.getObject()) is not None

                if subj_match and obj_match:
                    try:
                         top_rel_name = rel.getTop()
                         rels_set.add(top_rel_name)
                    except AttributeError:
                         print(f"Warning: Relationship class missing 'getTop'. Cannot determine top relationship for '{rel.getName()}'.")
                         rels_set.add(rel.getName()) # Fallback
                    break # Found a match for this relationship, move to next rel
        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(rels_set))
        return rels_set

    # Method: getObjsFromSubRels (public in Java)
    def getObjsFromSubRels(self, subject: str, relationships: List[str]) -> List[str]: # Java returns List (Vector)
        """Retrieves unique objects related to a subject via a list of relationship names (considering inheritance)."""
        # Java logic: find subject entity, use HashSet for uniqueness, iterate relationships, iterate refs, check subject inheritance, add object. Return Vector.
        objects_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)

        for rel_name in relationships:
            rel = self.getRelationship(rel_name)
            if rel:
                # --- Correction: Only iterate direct references of 'rel' ---
                try:
                    direct_references = rel.getReferences()
                except AttributeError:
                    print(f"Warning: Relationship class missing 'getReferences' for '{rel_name}'.")
                    continue # Skip this relationship if it has no getReferences
                # --- End Correction ---

                for ref in direct_references: # Use direct_references now
                    # Java check: ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null
                    is_match = False
                    ref_subject_name = ref.getSubject()
                    if ref_subject_name:
                        is_match = ref_subject_name.lower() == subject.lower()
                        if not is_match and subj_entity:
                            is_match = self.findInTree(subj_entity, ref_subject_name) is not None

                    if is_match:
                        objects_set.add(ref.getObject())

        return sorted(list(objects_set)) # Return sorted list to mimic HashSet -> Vector

    # Method: getObjsFromSubj (public in Java)
    def getObjsFromSubj(self, subject: str) -> Set[str]: # Java returns TreeSet
        """Retrieves all unique objects related to a subject across all relationships (considering inheritance)."""
        objects_set: Set[str] = set()
        subj_entity = self.findInTree(self.entityTree, subject)

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                # Java check: ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null
                is_match = ref.getSubject().lower() == subject.lower()
                if not is_match and subj_entity:
                     is_match = self.findInTree(subj_entity, ref.getSubject()) is not None

                if is_match:
                    objects_set.add(ref.getObject())
        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(objects_set))
        return objects_set

    # Method: getSubjsFromObj (public in Java)
    def getSubjsFromObj(self, object_ref: str) -> Set[str]: # Java returns TreeSet
        """Retrieves all unique subjects related to an object across all relationships (considering inheritance)."""
        subjects_set: Set[str] = set()
        obj_entity = self.findInTree(self.entityTree, object_ref)

        for rel in self.getAllRelationships():
            for ref in rel.getReferences():
                # Java check: ref.getObject().equals(object) || findInTree(parent, ref.getObject())!=null
                is_match = ref.getObject().lower() == object_ref.lower()
                if not is_match and obj_entity:
                     is_match = self.findInTree(obj_entity, ref.getObject()) is not None

                if is_match:
                    subjects_set.add(ref.getSubject())
        # Return set (unordered), Java returns TreeSet (ordered). Sort if needed.
        # return sorted(list(subjects_set))
        return subjects_set

    # Method: getAxioms (public in Java)
    def getAxioms(self) -> Set[Axiom]: # Java returns HashSet
        """Returns the set of axioms."""
        return self.axioms

    # Method: setAxioms (public in Java)
    def setAxioms(self, axioms: Set[Axiom]) -> None: # Java takes HashSet
        """Sets the set of axioms."""
        self.axioms = axioms