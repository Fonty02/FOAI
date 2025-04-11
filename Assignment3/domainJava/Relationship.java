package domain;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import java.util.Vector;

/**
 * Represents a relationship within a domain model.
 * This class extends Entity and models connections between domain entities.
 * Relationships can form hierarchies with parent-child relationships and can 
 * contain references between subjects and objects.
 * 
 * <p>A relationship has an inverse name which represents the relationship 
 * when viewed from the opposite direction. Relationships can also be symmetric,
 * meaning they are the same in both directions.</p>
 * 
 * <p>This class provides functionality to manage references between entities,
 * handle the hierarchical structure of relationships, and maintain relationship
 * attributes.</p>
 */
public class Relationship extends Entity {
    /**
     * The universal relationship name, used as the name for the top-level relationship.
     */
    private static final String universalRelationshipName = "Relationship";
    
    /**
     * The inverse name of this relationship.
     */
    private String inverse;
    
    /**
     * The collection of references between subjects and objects for this relationship.
     */
    private Vector<Reference> references = new Vector<>();
    
    /**
     * The child relationships of this relationship in the hierarchy.
     */
    private ArrayList<Relationship> children = new ArrayList<>();
    
    /**
     * The parent relationship of this relationship in the hierarchy.
     */
    private Relationship parent;
    
    /**
     * Flag indicating whether this relationship is symmetric.
     * A symmetric relationship is the same in both directions.
     */
    private boolean symmetric;
    
    /**
     * Constructs a new Relationship with the specified domain, name, and inverse.
     *
     * @param domain The domain to which this relationship belongs
     * @param name The name of the relationship
     * @param inverse The inverse name of the relationship
     */
    public Relationship(String domain, String name, String inverse) {
        super(name, domain);
        this.inverse = inverse;
    }
    
    /**
     * Constructs a new Relationship with the specified domain, name, inverse, and parent.
     *
     * @param domain The domain to which this relationship belongs
     * @param name The name of the relationship
     * @param inverse The inverse name of the relationship
     * @param parent The parent relationship
     */
    public Relationship(String domain, String name, String inverse, Relationship parent) {
        super(name, domain);
        this.inverse = inverse;
        this.setParentRelationship(parent);
    }
    
    /**
     * Constructs a new Relationship with the specified domain, name, inverse, symmetric flag, and attributes.
     *
     * @param domain The domain to which this relationship belongs
     * @param name The name of the relationship
     * @param inverse The inverse name of the relationship
     * @param symmetric Whether the relationship is symmetric
     * @param attributes The list of attributes for this relationship
     */
    public Relationship(String domain, String name, String inverse, Boolean symmetric, List<Attribute> attributes) {
        this(domain, name, inverse);
        this.symmetric = symmetric;
        this.attributes = attributes;
    }
    
    /**
     * Returns a string representation of this relationship.
     * 
     * @return The name of this relationship
     */
    @Override
    public String toString() {
        return name;
    }
    
    /**
     * Sets the references of this relationship.
     * 
     * @param references The new collection of references
     */
    public void setReferences(Vector<Reference> references) {
        this.references = references;
    }

    /**
     * Removes a specific reference from this relationship.
     * 
     * @param ref The reference to remove
     */
    public void removeRef(Reference ref) {
        references.remove(ref);
    }
    
    /**
     * Gets all references in this relationship.
     * 
     * @return The collection of references
     */
    public Vector<Reference> getReferences() {
        return references;
    }
    
    /**
     * Gets all unique subjects from the references in this relationship.
     * 
     * @return A sorted set of all subjects
     */
    public TreeSet<String> getSubjects() {
        TreeSet<String> subjects = new TreeSet<String>();
        for (Reference r : references) {
            subjects.add(r.getSubject());
        }
        return subjects;
    }
    
    /**
     * Finds a specific reference by subject and object.
     * 
     * @param subject The subject to search for
     * @param object The object to search for
     * @return The matching reference, or null if not found
     */
    public Reference getReference(String subject, String object) {
        for(Reference r : references) {
            if(r.getSubject().equalsIgnoreCase(subject) && r.getObject().equalsIgnoreCase(object)) {
                return r;
            }
        }
        return null;
    }

    /**
     * Gets all unique objects from the references in this relationship.
     * 
     * @return A sorted set of all objects
     */
    public TreeSet<String> getObjects() {
        TreeSet<String> objects = new TreeSet<String>();
        for (Reference r : references) {
            objects.add(r.getObject());
        }
        return objects;
    }

    /**
     * Gets all objects related to a specific subject in this relationship.
     * 
     * @param subject The subject to find related objects for
     * @return A vector of objects related to the subject
     */
    public Vector<String> getSubj_Objs(String subject) {
        Vector<String> objects = new Vector<String>();
        for (Reference r : references) {
            if (r.getSubject().equals(subject))
                objects.add(r.getObject());
        }
        return objects;
    }
    
    /**
     * Removes multiple references from this relationship.
     * 
     * @param refs The references to remove
     */
    public void removeAll(Vector<Reference> refs) {
        references.removeAll(refs);
    }
    
    /**
     * Gets all subjects related to a specific object in this relationship.
     * 
     * @param object The object to find related subjects for
     * @return A vector of subjects related to the object
     */
    public Vector<String> getObj_Subjs(String object) {
        Vector<String> subjects = new Vector<String>();
        for (Reference r : references) {
            if (r.getObject().equals(object))
                subjects.add(r.getSubject());
        }
        return subjects;
    }
    
    /**
     * Gets all attributes for this relationship, including a default "notes" attribute.
     * This method overrides the one in Entity.
     * 
     * @return A list of all attributes
     */
    public List<Attribute> getAllAttributes() {
        ArrayList<Attribute> allAttributes = new ArrayList<Attribute>(attributes);
        allAttributes.add(new Attribute("notes","text"));
        return allAttributes;
    }
    
    /**
     * Gets the name of this relationship.
     * 
     * @return The relationship name
     */
    public String getName() {
        return name;
    }
    
    /**
     * Sets both the name and inverse of this relationship.
     * 
     * @param name The new name
     * @param inverse The new inverse name
     */
    public void set(String name, String inverse) {
        setName(name);
        setInverse(inverse);
    }
    
    /**
     * Gets the inverse name of this relationship.
     * 
     * @return The inverse name
     */
    public String getInverse() {
        return inverse;
    }
    
    /**
     * Sets the inverse name of this relationship.
     * 
     * @param inverse The new inverse name
     */
    public void setInverse(String inverse) {
        this.inverse = inverse;
    }
    
    /**
     * Gets whether this relationship is symmetric.
     * 
     * @return true if the relationship is symmetric, false otherwise
     */
    public Boolean getSymmetric() {
        return symmetric;
    }
    
    /**
     * Sets whether this relationship is symmetric.
     * 
     * @param symmetric The new symmetric flag value
     */
    public void setSymmetric(Boolean symmetric) {
        this.symmetric = symmetric;
    }

    /**
     * Adds a reference to this relationship. If a reference with the same subject and object
     * already exists, it is replaced with the new reference.
     * 
     * @param ref The reference to add
     */
    public void addReference(Reference ref) {
        for (Reference r : references)
            if (ref.getSubject().equals(r.getSubject()) && ref.getObject().equals(r.getObject())) {
                references.remove(r);
                break;
            }
        references.add(ref);
    }

    /**
     * Gets the children relationships of this relationship.
     * 
     * @return The list of child relationships
     */
    public ArrayList<Relationship> getChildrenRelationships() {
        return children;
    }

    /**
     * Sets the children relationships of this relationship.
     * 
     * @param children The new list of child relationships
     */
    public void setChildrenRelationship(ArrayList<Relationship> children) {
        this.children = children;
    }
    
    /**
     * Adds a child relationship to this relationship.
     * 
     * @param relationship The child relationship to add
     */
    public void addChildrenRelationship(Relationship relationship) {
        this.children.add(relationship);
    }

    /**
     * Adds multiple references to this relationship.
     * 
     * @param references The collection of references to add
     */
    public void addReferences(Vector<Reference> references) {
        for(Reference ref : references) {
            addReference(ref);
        }
    }

    /**
     * Sets the parent relationship of this relationship and adds this relationship
     * as a child to the parent.
     * 
     * @param parent The parent relationship
     */
    public void setParentRelationship(Relationship parent) {
        this.parent = parent;
        parent.addChild(this);
    }
    
    /**
     * Checks if this relationship is a top-level relationship.
     * 
     * @return true if this is a top-level relationship, false otherwise
     */
    public boolean isTopRelationship() {
        return this.parent.getName().equals(universalRelationshipName);
    }

}
