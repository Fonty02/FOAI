package domain;

/**
 * Represents a triple consisting of subject, relation, and object instances.
 * This class models a relationship between entities in the form of (subject, relation, object).
 */
public class RelationTriple {

    private Instance subject;
    private Instance relation;
    private Instance object;
    
    /**
     * Default constructor that creates an empty relation triple.
     */
    public RelationTriple() {}
    
    /**
     * Creates a relation triple with specified subject, relation, and object.
     * 
     * @param subject The instance representing the subject of the triple
     * @param relation The instance representing the relation of the triple
     * @param object The instance representing the object of the triple
     */
    public RelationTriple(Instance subject, Instance relation, Instance object) {
        this.subject = subject;
        this.relation = relation;
        this.object = object;
    }
    
    /**
     * Returns the subject of this relation triple.
     * 
     * @return The subject instance
     */
    public Instance getSubject() {
        return subject;
    }
    
    /**
     * Sets the subject of this relation triple.
     * 
     * @param subject The instance to set as the subject
     */
    public void setSubject(Instance subject) {
        this.subject = subject;
    }
    
    /**
     * Returns the relation of this relation triple.
     * 
     * @return The relation instance
     */
    public Instance getRelation() {
        return relation;
    }
    
    /**
     * Sets the relation of this relation triple.
     * 
     * @param relation The instance to set as the relation
     */
    public void setRelation(Instance relation) {
        this.relation = relation;
    }
    
    /**
     * Returns the object of this relation triple.
     * 
     * @return The object instance
     */
    public Instance getObject() {
        return object;
    }
    
    /**
     * Sets the object of this relation triple.
     * 
     * @param object The instance to set as the object
     */
    public void setObject(Instance object) {
        this.object = object;
    }
}
