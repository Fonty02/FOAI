package domain;
import java.util.List;
//funziona
import java.util.Map;

/**
 * Represents an instance of a specific type with a set of attribute values.
 * Each instance has a unique identifier and a short description generated from its descriptive attributes.
 */
public class Instance {
    /** The type of this instance */
    private String type; 
    /** The unique identifier for this instance */
    private String selectedInstanceId; //ste non puo' essere int?
    /** Map containing the attribute values, where keys are attribute names and values are attribute values */
    private Map<String,String> attributeValues;
    /** A short human-readable description of this instance */
    private String shortDescription;

    /**
     * Constructs a new Instance with the specified properties.
     *
     * @param type The type of the instance
     * @param selectedInstanceId The unique identifier for this instance
     * @param attrVals Map of attribute values where keys are attribute names
     * @param fields List of attributes that define the structure of this instance type
     */
    public Instance(String type, String selectedInstanceId, Map<String,String> attrVals, List<Attribute> fields) {
        this.type = type;
        this.selectedInstanceId = selectedInstanceId;
        this.shortDescription = buildShortDescription(selectedInstanceId, type, attrVals, fields);
        this.attributeValues = attrVals;
    }

    /**
     * Builds a short description for this instance based on its descriptive attributes.
     *
     * @param id The instance identifier
     * @param type The instance type
     * @param myAttributeValues Map of attribute values
     * @param fields List of attributes that define the structure
     * @return A string containing the short description
     */
    private String buildShortDescription(String id, String type, Map<String,String> myAttributeValues, List<Attribute> fields) {
        String shortDescription = "";
        for(Attribute a : fields)
            if(a.isDescriptive() && myAttributeValues.get(a.getName()) != null)
                shortDescription += myAttributeValues.get(a.getName()) + " ";
        return shortDescription += "  <" + id + ":" + type + ">";
    }

    /**
     * Sets the type of this instance.
     *
     * @param type The new type
     */
    public void setType(String type) {
        this.type = type;
    }
    
    /**
     * Gets the type of this instance.
     *
     * @return The instance type
     */
    public String getType() {
        return type;
    }
    
    /**
     * Sets the unique identifier for this instance.
     *
     * @param selectedInstanceId The new identifier
     */
    public void setSelectedInstanceId(String selectedInstanceId) {
        this.selectedInstanceId = selectedInstanceId;
    }
    
    /**
     * Gets the unique identifier of this instance.
     *
     * @return The instance identifier
     */
    public String getSelectedInstanceId() {
        return selectedInstanceId;
    }
    
//	public void setAttributeValues(Map<String, String> attributeValues) {
//		this.attributeValues = attributeValues;
//	}

    /**
     * Gets the short description of this instance.
     *
     * @return The short description
     */
    public String getShortDescription() {
        return shortDescription;
    }
    
    /**
     * Sets the short description of this instance.
     *
     * @param shortDescription The new short description
     */
    public void setShortDescription(String shortDescription) {
        this.shortDescription = shortDescription;
    }
    
    /**
     * Gets the attribute values of this instance.
     *
     * @return Map of attribute values where keys are attribute names
     */
    public Map<String, String> getAttributeValues() {
        return attributeValues;
    }
    
    /**
     * Sets the attribute values for this instance.
     *
     * @param attributeValues Map of new attribute values
     */
    public void setAttributeValues(Map<String, String> attributeValues) {
        this.attributeValues = attributeValues;
    }

//	public void setShortDescription(String shortDescription) {
//		this.shortDescription = shortDescription;
//	}

    /**
     * Returns a string representation of this instance.
     *
     * @return A string containing the instance ID
     */
    @Override
    public String toString() {
        return "Instance [selectedInstanceId=" + selectedInstanceId + "]";
    }
    
    /**
     * Compares this instance with another object for equality.
     * Instances are considered equal if they have the same ID.
     *
     * @param obj The object to compare with
     * @return true if this instance equals the specified object, false otherwise
     */
    @Override
    public boolean equals(Object obj) {
        // TODO Auto-generated method stub
        Instance objInstance = (Instance) obj;
        return this.selectedInstanceId.equals(objInstance.selectedInstanceId);
    }
}