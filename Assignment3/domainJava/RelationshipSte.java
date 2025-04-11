package domain;

import java.util.Collections;
import java.util.Vector;

/**
 * Represents a relationship stereotype that defines connections between subjects and objects.
 * The relationship can have attributes and may be symmetric.
 */
public class RelationshipSte {
    private String name;
    private String inverse;
    private boolean symmetric;
    private Vector<Attribute> attributes;
    private Vector<Reference> relationships;
    
    /**
     * Creates a new relationship stereotype.
     *
     * @param name The name of the relationship
     * @param inverse The name of the inverse relationship
     * @param symmetric Whether the relationship is symmetric (if A relates to B, then B relates to A)
     * @param attributes The attributes associated with this relationship
     */
    public RelationshipSte(String name, String inverse, Boolean symmetric, Vector<Attribute> attributes) {
        this.name = name;
        this.inverse = inverse;
        this.symmetric = symmetric;
        this.attributes = attributes;
    }
    
    /**
     * Retrieves all unique subjects in this relationship.
     *
     * @return A sorted vector of all subjects
     */
    public Vector<String> getSubjects() {
        Vector<String> subjects = new Vector<String>();
        for (Reference r : relationships) {
            subjects.add(r.getSubject());
        }
        Collections.sort(subjects);
        return subjects;
    }

    /**
     * Retrieves all unique objects in this relationship.
     *
     * @return A sorted vector of all objects
     */
    public Vector<String> getObjects() {
        Vector<String> objects = new Vector<String>();
        for (Reference r : relationships) {
            objects.add(r.getObject());
        }
        Collections.sort(objects);
        return objects;
    }

    /**
     * Finds all objects that are related to a specific subject.
     *
     * @param subject The subject to find related objects for
     * @return A vector of objects related to the specified subject
     */
    public Vector<String> getSubj_Objs(String subject) {
        Vector<String> objects = new Vector<String>();
        for (Reference r : relationships) {
            if (r.getSubject().equals(subject))
                objects.add(r.getObject());
        }
        return objects;
    }
    
    /**
     * Finds all subjects that relate to a specific object.
     *
     * @param object The object to find related subjects for
     * @return A vector of subjects related to the specified object
     */
    public Vector<String> getObj_Subjs(String object) {
        Vector<String> subjects = new Vector<String>();
        for (Reference r : relationships) {
            if (r.getObject().equals(object))
                subjects.add(r.getSubject());
        }
        return subjects;
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
     * Sets the name of this relationship.
     *
     * @param name The new relationship name
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * Gets the inverse relationship name.
     *
     * @return The inverse relationship name
     */
    public String getInverse() {
        return inverse;
    }
    
    /**
     * Sets the inverse relationship name.
     *
     * @param inverse The new inverse relationship name
     */
    public void setInverse(String inverse) {
        this.inverse = inverse;
    }
    
    /**
     * Checks if this relationship is symmetric.
     *
     * @return True if the relationship is symmetric, false otherwise
     */
    public Boolean getSymmetric() {
        return symmetric;
    }
    
    /**
     * Sets whether this relationship is symmetric.
     *
     * @param symmetric True to make the relationship symmetric, false otherwise
     */
    public void setSymmetric(Boolean symmetric) {
        this.symmetric = symmetric;
    }
    
    /**
     * Gets the attributes associated with this relationship.
     *
     * @return A vector of attributes
     */
    public Vector<Attribute> getAttributes() {
        return attributes;
    }
    
    /**
     * Sets the attributes for this relationship.
     *
     * @param attributes The new vector of attributes
     */
    public void setAttributes(Vector<Attribute> attributes) {
        this.attributes = attributes;
    }
}
