import io
from typing import List, Dict, Optional, TYPE_CHECKING

# Assuming domain classes are in the same directory or package
from .Attribute import Attribute
from .DomainData import DomainData
from .Entity import Entity
from .Reference import Reference
from .Relationship import Relationship
if TYPE_CHECKING:
    from .TreeNode import TreeNode # Or from appropriate library

class TranslatorAPIProlog:

    serialVersionUID: int = 1  # Placeholder for Java's serialVersionUID
    attributes: Optional[Dict[str, List[Attribute]]] = None
    attributesRel: Optional[Dict[str, List[Attribute]]] = None
    domainName: Optional[str] = None
    recur: str = ""

    def __init__(self, domain: DomainData):
        """
        Initializes the TranslatorAPIProlog instance and generates Prolog facts.
        Mirrors the Java constructor.
        """
        if domain.getDomain() is None:
            raise ValueError("Domain name cannot be None")

        content = f"domain({domain.getDomain().lower()}).\n"
        content += TranslatorAPIProlog.createEntities(domain.getTopEntities())
        content += TranslatorAPIProlog.createRelationships(domain.getTopRelationships())

        # output originale
        content = TranslatorAPIProlog.writeFactsWithId(content, "id")
        print(content)


    @staticmethod
    def writeFactsWithId(content: str, id_prefix: str) -> str:
        """
        Adds a unique ID to each fact string.
        Mirrors the Java static method.
        """
        id_counter = 0
        contentWithId = ""
        # Split carefully, handling potential empty lines
        facts = [line for line in content.splitlines() if line.strip()]
        for fact in facts:
            fact = fact[:-1]
            # Format with ID
            fact_with_id = f"fact({id_prefix}_{id_counter}, {fact}, 1).\n"
            id_counter += 1
            contentWithId += fact_with_id
        return contentWithId

    @staticmethod
    def createEntities(entities: List[Entity]) -> str:
        """
        Generates Prolog facts for top-level entities and their attributes recursively.
        Mirrors the Java static method.
        """
        values = ""
        att = ""
        for entity in entities:
            domain_lower = entity.getDomain().lower() if entity.getDomain() else "unknown_domain"
            name_lower = entity.getName().lower() if entity.getName() else "unknown_entity"

            values += f"entity({domain_lower}, {name_lower}).\n"
            # Use getAttributes() for top-level entities as in Java
            for attr in entity.getAttributes():
                attr_name_lower = attr.getName().lower() if attr.getName() else "unknown_attr"
                attr_dtype_lower = attr.getDataType().lower() if attr.getDataType() else "unknown_type"

                att += f"attribute({domain_lower}, {name_lower}, {attr_name_lower}, {attr_dtype_lower}).\n"
                if attr.getValues(): # Check if list is not empty
                    # Ensure getValuesToStringToLower exists and returns a Prolog-compatible list string
                    values_str = attr.getValuesToStringToLower() # Assuming this method exists and formats correctly
                    if values_str: # Check if the result is not empty
                         att += f"values({domain_lower}, {name_lower}, {attr_name_lower}, {values_str}).\n"

                if attr.getMandatory():
                    att += f"mandatory({domain_lower}, {name_lower}, {attr_name_lower}).\n"
                if attr.isDisplay():
                    att += f"display({domain_lower}, {name_lower}, {attr_name_lower}).\n"
                if attr.isDistinguishing():
                    att += f"distinguishing({domain_lower}, {name_lower}, {attr_name_lower}).\n"
                if attr.getTarget():
                    target_lower = attr.getTarget().lower() # type: ignore
                    att += f"target({domain_lower}, {name_lower}, {attr_name_lower}, {target_lower}).\n"

            # Process children recursively
            children = entity.getChildren()
            if children:
                 for e in children:
                      child_name_lower = e.getName().lower() if e.getName() else "unknown_child"
                      att += f"parent({domain_lower}, {name_lower}, {child_name_lower}).\n"
                      # Call writeEntity for children as in Java
                      att += TranslatorAPIProlog.writeEntity(e)
        values += att
        return values

    @staticmethod
    def writeEntity(entity: Entity) -> str:
        """
        Generates Prolog facts for a specific entity and its *new* attributes recursively.
        Mirrors the Java static method.
        """
        att = ""
        domain_lower = entity.getDomain().lower() if entity.getDomain() else "unknown_domain"
        name_lower = entity.getName().lower() if entity.getName() else "unknown_entity"

        att += f"entity({domain_lower}, {name_lower}).\n"
        # Use getNewAttributes() for child entities as in Java
        for attr in entity.getNewAttributes():
            attr_name_lower = attr.getName().lower() if attr.getName() else "unknown_attr"
            attr_dtype_lower = attr.getDataType().lower() if attr.getDataType() else "unknown_type"

            att += f"attribute({domain_lower}, {name_lower}, {attr_name_lower}, {attr_dtype_lower}).\n"
            if attr.getValues():
                values_str = attr.getValuesToStringToLower() # Assuming this method exists
                if values_str:
                    att += f"values({domain_lower}, {name_lower}, {attr_name_lower}, {values_str}).\n"
            if attr.getMandatory():
                att += f"mandatory({domain_lower}, {name_lower}, {attr_name_lower}).\n"
            if attr.isDisplay():
                att += f"display({domain_lower}, {name_lower}, {attr_name_lower}).\n"
            if attr.isDistinguishing():
                att += f"distinguishing({domain_lower}, {name_lower}, {attr_name_lower}).\n"
            if attr.getTarget():
                target_lower = attr.getTarget().lower() # type: ignore
                att += f"target({domain_lower}, {name_lower}, {attr_name_lower}, {target_lower}).\n"

        # Process children recursively
        children = entity.getChildren()
        if children:
            for e in children:
                child_name_lower = e.getName().lower() if e.getName() else "unknown_child"
                att += f"parent({domain_lower}, {name_lower}, {child_name_lower}).\n"
                att += TranslatorAPIProlog.writeEntity(e)
        return att

    @staticmethod
    def createRelationships(relationships: List[Relationship]) -> str:
        """
        Generates Prolog facts for relationships, inverses, and attributes.
        Mirrors the Java static method.
        """
        att = ""
        for relation in relationships:
            domain_lower = relation.getDomain().lower() if relation.getDomain() else "unknown_domain"
            rel_name_lower = relation.getName().lower() if relation.getName() else "unknown_relation"

            # Relationship facts from references
            refs = relation.getReferences()
            if refs:
                for ref in refs:
                    subj_lower = ref.getSubject().lower() if ref.getSubject() else "unknown_subject"
                    obj_lower = ref.getObject().lower() if ref.getObject() else "unknown_object"
                    att += f"relationship({domain_lower}, {rel_name_lower}, {subj_lower}, {obj_lower}).\n"

            # Inverse relationship fact
            inv_lower = relation.getInverse().lower() if relation.getInverse() else "unknown_inverse"
            att += f"inverse({domain_lower}, {rel_name_lower}, {inv_lower}).\n"

            # Attributes of the relationship
            rel_attrs = relation.getAttributes()
            if rel_attrs:
                for attr in rel_attrs:
                    attr_name_lower = attr.getName().lower() if attr.getName() else "unknown_attr"
                    attr_dtype_lower = attr.getDataType().lower() if attr.getDataType() else "unknown_type"

                    att += f"attribute({domain_lower}, {rel_name_lower}, {attr_name_lower}, {attr_dtype_lower}).\n"
                    if attr.getValues():
                        values_str = attr.getValuesToStringToLower() # Assuming this method exists
                        if values_str:
                             att += f"values({domain_lower}, {rel_name_lower}, {attr_name_lower}, {values_str}).\n"
                    if attr.getMandatory():
                        att += f"mandatory({domain_lower}, {rel_name_lower}, {attr_name_lower}).\n"
                    if attr.isDisplay():
                        att += f"display({domain_lower}, {rel_name_lower}, {attr_name_lower}).\n"
                    if attr.isDistinguishing():
                        att += f"distinguishing({domain_lower}, {rel_name_lower}, {attr_name_lower}).\n"
                    if attr.getTarget():
                        target_lower = attr.getTarget().lower() # type: ignore
                        att += f"target({domain_lower}, {rel_name_lower}, {attr_name_lower}, {target_lower}).\n"
        return att

    # --- Instance Methods ---

    def getClassi(self, classi: TreeNode) -> List[str]:
        """
        Gets the string representation of the direct children of a TreeNode.
        Requires a TreeNode implementation with getChildren() and __str__.
        """
        s: List[str] = []
        children = classi.getChildren() # Assuming getChildren exists
        if children:
            for t in children:
                s.append(str(t)) # Assuming __str__ gives the desired representation
        return s

    def getAttributes(self) -> Optional[Dict[str, List[Attribute]]]:
        return self.attributes

    def setAttributes(self, attributes: Dict[str, List[Attribute]]) -> None:
        self.attributes = attributes

    def getAttributesRel(self) -> Optional[Dict[str, List[Attribute]]]:
        return self.attributesRel

    def setAttributesRel(self, attributesRel: Dict[str, List[Attribute]]) -> None:
        self.attributesRel = attributesRel

    # getSerialversionuid is Java specific, omitted.

    def getDomainName(self) -> Optional[str]:
        return self.domainName

    def setDomainName(self, domainName: str) -> None:
        self.domainName = domainName

    def recursiveTree(self, node: 'TreeNode') -> List[str]:
        """
        Recursively collects the string representation of all nodes in a subtree.
        Requires a TreeNode implementation.
        """
        classi: List[str] = []
        children = node.getChildren() # Assuming getChildren exists
        if children:
            # Java code iterates using getChildCount, Python can iterate directly
            for child_node in children:
                classi.append(str(child_node)) # Add current child
                classi.extend(self.recursiveTree(child_node)) # Recurse and add results
        return classi

    def recursiveTreeTax(self, s: str, node: 'TreeNode', superV: str) -> None:
        """
        Recursively builds a string representation of a taxonomy.
        Modifies the instance variable `recur`. Requires a TreeNode implementation.
        """
        children = node.getChildren() # Assuming getChildren exists
        if children:
            # Java code iterates using getChildCount, Python can iterate directly
            for child_node in children:
                child_str = str(child_node)
                self.recur += f"{s}{superV}, {child_str}).\n"
                self.recursiveTreeTax(s, child_node, child_str)

    def getRecur(self) -> str:
        return self.recur

    def setRecur(self, recur: str) -> None:
        self.recur = recur

    # Private helper method in Java, made internal (_ prefix) in Python
    def _createList(self, lista: List[str]) -> str:
        """
        Creates a Prolog-style list string from a Python list of strings.
        Mirrors the Java private method createList.
        """
        if not lista:
            return "[]"
        list_content = ", ".join(lista)
        return f"[{list_content}]"
