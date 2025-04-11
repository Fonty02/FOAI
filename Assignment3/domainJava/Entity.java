package domain;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Vector;
import java.util.stream.Collectors;

import org.primefaces.model.DefaultTreeNode;
import org.primefaces.model.TreeNode;

/**
 * Represents an entity in the domain model with hierarchical relationships
 * and attributes.
 */
public class Entity extends DomainTag{
    private static final String universalClassName = "Entity";
    private List<String> values = new ArrayList<String>();
    private String graphBrainID;
    protected List<Attribute> attributes = new ArrayList<Attribute>();
    protected List<Entity> children = new ArrayList<Entity>();
    protected Entity parent;
    protected boolean _abstract=false;

    /**
     * Creates a new Entity with the specified name.
     *
     * @param name The name of the entity
     */
    public Entity(String name) {
        this.name = name;
    }
    
    /**
     * Creates a new Entity with the specified name and domain.
     *
     * @param name The name of the entity
     * @param domain The domain this entity belongs to
     */
    public Entity(String name, String domain) {
        this(name);
        this.domain = domain;
    }
    
    /**
     * Checks if this entity is abstract.
     *
     * @return true if the entity is abstract, false otherwise
     */
    public boolean isAbstract() {
        return _abstract;
    }

    /**
     * Sets the abstract property of this entity.
     *
     * @param _abstract true to make this entity abstract, false otherwise
     */
    public void setAbstract(boolean _abstract) {
        this._abstract = _abstract;
    }

    /**
     * Gets the list of attributes defined directly on this entity.
     *
     * @return List of attributes for this entity
     */
    public List<Attribute> getAttributes() {
        return attributes;
    }
    
    /**
     * Gets the top-most entity in the inheritance hierarchy.
     *
     * @return The name of the top-most entity
     */
    public String getTop() {
        if(parent.getName().equals("Entity") || parent.getName().equals("Relationship"))
            return this.getName();
        return parent.getTop();
    }
    
    /**
     * Gets all attributes, including inherited ones from parent entities.
     *
     * @return List of all attributes including inherited ones
     */
    public List<Attribute> getAllAttributes() {
        List<Attribute> pathAttributes = new ArrayList<Attribute>();
        if (parent != null)
            pathAttributes = parent.getAllAttributes();
        pathAttributes.addAll(this.getAttributes());
        return pathAttributes;
    }

    /**
     * Gets the names of all attributes, including inherited ones.
     *
     * @return List of all attribute names
     */
    public List<String> getAllAttributesToString() {
        ArrayList<String> allAttributesToString = new ArrayList<>();
        for (Attribute attr : getAllAttributes())
            allAttributesToString.add(attr.getName());
        return allAttributesToString;
    }
    
    /**
     * Gets all mandatory attributes, including inherited ones.
     *
     * @return List of all mandatory attributes
     */
    public List<Attribute> getMandatoryAttributes(){
        List<Attribute> mandatoryAttributes = new ArrayList<>();
        List<Attribute> allAttributes = getAllAttributes();
        for (Attribute attr : allAttributes)
            if (attr.isMandatory())
                mandatoryAttributes.add(attr);
        return mandatoryAttributes;
    }

    /**
     * Adds a child entity to this entity.
     *
     * @param child The entity to be added as a child
     */
    public void addChild(Entity child) {
        children.add(child);
        child.setParent(this);
    }
    
    /**
     * Removes all attributes from this entity that are also in the specified entity.
     *
     * @param entity The entity whose attributes should be removed
     */
    public void removeAllAttributes(Entity entity) {
        attributes.removeAll(entity.getAttributes());
    }
    
    /**
     * Finds a child entity by name.
     *
     * @param name The name of the child entity to find
     * @return The child entity if found, null otherwise
     */
    public Entity getChild(String name) {
        for(Entity e : getChildren())
            if(e.getName().equalsIgnoreCase(name))
                return e;
        return null;
    }
    
    /**
     * Method to be implemented by subclasses.
     */
    public void run() {}
    
    /**
     * Gets the list of child entities.
     *
     * @return List of child entities
     */
    public List<Entity> getChildren() {
        return children;
    }

    /**
     * Gets the names of all child entities.
     *
     * @return List of child entity names
     */
    public ArrayList<String> getChildrenToString() {
        ArrayList<String> childrenToString = new ArrayList<>();
        for(Entity e : getChildren())
            childrenToString.add(e.getName());
        return childrenToString;
    }

    /**
     * Sets the list of child entities.
     *
     * @param children The list of child entities to set
     */
    public void setChildren(List<Entity> children) {
        this.children = children;
    }

    /**
     * Gets the parent entity.
     *
     * @return The parent entity
     */
    public Entity getParent() {
        return parent;
    }

    /**
     * Sets the parent entity.
     *
     * @param parent The parent entity to set
     */
    public void setParent(Entity parent) {
        this.parent = parent;
    }
    
    /**
     * Gets attributes that are unique to this entity (not inherited from parent).
     *
     * @return List of attributes unique to this entity
     */
    public ArrayList<Attribute> getNewAttributes() {
        ArrayList<Attribute> s = new ArrayList<>();
        for(Attribute a : attributes) {
            if(!parent.getAttributesToString().contains(a.getName())) {
                s.add(a);
            }
        }
        return s;
    }
    
    /**
     * Gets the names of all attributes directly defined on this entity.
     *
     * @return List of attribute names
     */
    public ArrayList<String> getAttributesToString() {
        return new ArrayList<String>(attributes.stream()
                                         	   .map(Attribute::getName)
                                         	   .collect(Collectors.toList())
                              		);
    }
    
    /**
     * Finds an attribute by name.
     *
     * @param attribute The name of the attribute to find
     * @return The attribute if found, null otherwise
     */
    public Attribute getAttribute(String attribute) {
        for(Attribute a : attributes) {
            if(a.getName().equals(attribute)) {
                return a;
            }
        }
        return null;
    }
    
    /**
     * Checks if this entity equals another entity.
     * Two entities are equal if they have the same name and domain.
     *
     * @param obj The object to compare with
     * @return true if the entities are equal, false otherwise
     */
    @Override
    public boolean equals(Object obj) {
        Entity other = (Entity) obj;
        return name.equals(other.name) && (domain == null ? other.domain == null : domain.equals(other.domain));
    }

    /**
     * Returns the string representation of this entity.
     *
     * @return The name of the entity
     */
    @Override
    public String toString() {
        return name;
    }

    /**
     * Adds an attribute to this entity.
     *
     * @param attr The attribute to add
     */
    public void addAttribute(Attribute attr) {
        attributes.add(attr);
    }

    /**
     * Adds multiple attributes to this entity, overwriting any attributes with the same name.
     *
     * @param attrs The attributes to add
     */
    public void addAttributes(Vector<Attribute> attrs) {
        for (Attribute a : attrs) { // se esiste lo sovrascrive
            for (Attribute old : attributes)
                if (old.getName().equals(a.getName())) {
                    attributes.remove(old);
                    break; // trovato, esce dal ciclo anticipatamente
                }
            attributes.add(a);
        }
    }

    /**
     * Removes an attribute by name.
     *
     * @param attribute The name of the attribute to remove
     */
    public void removeAttribute(String attribute) {
        attributes.remove(getAttribute(attribute));
    }

    /**
     * Sets the list of attributes for this entity.
     *
     * @param attributes The list of attributes to set
     */
    public void setAttributes(List<Attribute> attributes) {
        this.attributes = attributes;
    }

    /**
     * Recursively searches for a subclass with the specified name.
     *
     * @param nameSubClass The name of the subclass to find
     * @return The subclass entity if found, null otherwise
     */
    public Entity findSubClass(String nameSubClass) {
        if (name.equals(nameSubClass))
            return this;
        else {
            Entity subClass = null;
            boolean found = false;
            for (Entity e : children)
                if (!found) {
                    subClass = e.findSubClass(nameSubClass);
                    if (subClass != null)
                        found = true;
                }
            return subClass;
        }
    }

    /**
     * Gets the path of entities from the root to this entity.
     *
     * @return List of entities representing the class path
     */
    public List<Entity> getClassPath() {
        List<Entity> path = new LinkedList<Entity>();
        Entity parent = this.getParent();
        if (parent != null) {
            path = parent.getClassPath();
        }
        path.add(this);
        return path;
    }

    /**
     * Gets the names of all subclasses, with an option to restrict to just this class.
     *
     * @param subclassRestriction If true, returns only this class name; if false, returns all subclass names
     * @return List of subclass names
     */
    public List<String> getAllSubclassNames(boolean subclassRestriction) {
        if (subclassRestriction) {
            List<String> subClassNames = new LinkedList<String>();
            subClassNames.add(this.getName());
            return subClassNames;
        } else
            return getAllSubclassesToString();
    }
    
    /**
     * Gets all subclasses of this entity, including this entity itself.
     *
     * @return List of all subclass entities
     */
    public List<Entity> getAllSubclasses() {
        List<Entity> subclasses = new LinkedList<Entity>();
        subclasses.add(this);
        if(this.children != null) {
            for(Entity e : this.children) {
                subclasses.addAll(e.getAllSubclasses());
            }
        }
        return subclasses;
    }
    
    /**
     * Gets the names of all subclasses of this entity, including this entity itself.
     *
     * @return List of all subclass names
     */
    public List<String> getAllSubclassesToString() {
        List<String> subclasses = new LinkedList<String>();
        subclasses.add(this.name);
        for(Entity e : this.children) {
            subclasses.addAll(e.getAllSubclassesToString());
        }
        return subclasses;
    }
    
    /**
     * Creates a tree representation of this entity and its subclasses.
     *
     * @return TreeNode representing the hierarchy of subclasses
     */
    public TreeNode getSubclassesTree() {
        TreeNode rootClass = new DefaultTreeNode(this);
        if(this.children != null)
            for(Entity e : this.children)
                rootClass.getChildren().add(e.getSubclassesTree());
        return rootClass;
    }
    
    /**
     * Checks if a subclass with the specified name exists.
     *
     * @param subclassName The name of the subclass to check
     * @return The subclass entity if found, null otherwise
     */
    public Entity existsSubclass(String subclassName) {
        if (this.getName().equals(subclassName))
            return this;
        else if (this.children != null) {
            Entity found;
            for(Entity e : this.children) {
                found = e.existsSubclass(subclassName);
                if (found != null)
                    return found;
            }
        }
        return null;
    }
    
    /**
     * Checks if this entity is a top-level class (direct child of the universal class).
     *
     * @return true if this is a top-level class, false otherwise
     */
    public boolean isTopClass() {
        return this.parent.getName().equals(universalClassName);
    }

    /**
     * Checks if this entity has a direct child with the specified name.
     *
     * @param entityName The name of the child entity to look for
     * @return true if a child with the specified name exists, false otherwise
     */
    public boolean hasChild(String entityName) {
        for(Entity e : this.getChildren()) {
            if(e.getName().equalsIgnoreCase(entityName)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Checks if this entity has an ancestor with the specified name.
     * Traverses up the hierarchy until reaching the "Entity" root class.
     *
     * @param entityName The name of the ancestor entity to look for
     * @return true if an ancestor with the specified name exists, false otherwise
     */
    public boolean hasAncestor(String entityName) {
        Entity e = this;
        while(!e.getParent().getName().equals("Entity")) {
            e = e.getParent();
            if(e.getName().equals(entityName)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Removes a child entity by name.
     *
     * @param childName The name of the child entity to remove
     */
    private void removeChild(String childName) {
        int pos = -1;
        for(int i=0; i<getChildren().size() && pos==-1; i++) {
            if(getChildren().get(i).getName().equalsIgnoreCase(childName)) {
                pos = i;
            }
        }
        getChildren().remove(pos);
    }
    
    /**
     * Detaches this entity from its parent.
     */
    public void detach() {
        getParent().removeChild(name);
    }

    /**
     * Gets the list of values associated with this entity.
     *
     * @return List of values
     */
    public List<String> getValues() {
        return values;
    }

    /**
     * Sets the list of values associated with this entity.
     *
     * @param values The list of values to set
     */
    public void setValues(List<String> values) {
        this.values = values;
    }

    /**
     * Gets the GraphBrain ID associated with this entity.
     *
     * @return The GraphBrain ID
     */
    public String getGraphBrainID() {
        return graphBrainID;
    }

    /**
     * Sets the GraphBrain ID associated with this entity.
     *
     * @param graphBrainID The GraphBrain ID to set
     */
    public void setGraphBrainID(String graphBrainID) {
        this.graphBrainID = graphBrainID;
    }
}
