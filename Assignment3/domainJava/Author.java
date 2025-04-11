package domain;

import java.sql.Timestamp;

/**
 * Represents an Author entity in the system.
 * This class stores information about an author including identification,
 * associated graph, type, attributes, description, creation date, username
 * and active status.
 */
public class Author {

    /** The unique identifier for the author */
    private Integer id;
    /** The associated graph identifier */
    private Integer graph_id;
    /** The type of the author */
    private String type;
    /** The key of the author's attribute */
    private String attributeKey;
    /** The value of the author's attribute */
    private String attributeValue;
    /** The description of the author */
    private String description;
    /** The date when the author was created */
    private Timestamp creationDate;
    /** The username of the author */
    private String username;
    /** Flag indicating if the author is active */
    private Boolean isActive;
    
    /**
     * Gets the unique identifier of the author.
     * 
     * @return the author's ID
     */
    public Integer getId() {
        return id;
    }
    
    /**
     * Sets the unique identifier of the author.
     * 
     * @param id the ID to set
     */
    public void setId(Integer id) {
        this.id = id;
    }
    
    /**
     * Gets the graph identifier associated with the author.
     * 
     * @return the graph ID
     */
    public Integer getGraph_id() {
        return graph_id;
    }
    
    /**
     * Sets the graph identifier associated with the author.
     * 
     * @param graph_id the graph ID to set
     */
    public void setGraph_id(Integer graph_id) {
        this.graph_id = graph_id;
    }
    
    /**
     * Gets the type of the author.
     * 
     * @return the author type
     */
    public String getType() {
        return type;
    }
    
    /**
     * Sets the type of the author.
     * 
     * @param type the author type to set
     */
    public void setType(String type) {
        this.type = type;
    }
    
    /**
     * Gets the attribute key of the author.
     * 
     * @return the attribute key
     */
    public String getAttributeKey() {
        return attributeKey;
    }
    
    /**
     * Sets the attribute key of the author.
     * 
     * @param attributeKey the attribute key to set
     */
    public void setAttributeKey(String attributeKey) {
        this.attributeKey = attributeKey;
    }
    
    /**
     * Gets the attribute value of the author.
     * 
     * @return the attribute value
     */
    public String getAttributeValue() {
        return attributeValue;
    }
    
    /**
     * Sets the attribute value of the author.
     * 
     * @param attributeValue the attribute value to set
     */
    public void setAttributeValue(String attributeValue) {
        this.attributeValue = attributeValue;
    }
    
    /**
     * Gets the description of the author.
     * 
     * @return the description
     */
    public String getDescription() {
        return description;
    }
    
    /**
     * Sets the description of the author.
     * 
     * @param description the description to set
     */
    public void setDescription(String description) {
        this.description = description;
    }
    
    /**
     * Gets the creation date of the author.
     * 
     * @return the creation date
     */
    public Timestamp getCreationDate() {
        return creationDate;
    }
    
    /**
     * Sets the creation date of the author.
     * 
     * @param creationDate the creation date to set
     */
    public void setCreationDate(Timestamp creationDate) {
        this.creationDate = creationDate;
    }
    
    /**
     * Gets the username of the author.
     * 
     * @return the username
     */
    public String getUsername() {
        return username;
    }
    
    /**
     * Sets the username of the author.
     * 
     * @param username the username to set
     */
    public void setUsername(String username) {
        this.username = username;
    }
    
    /**
     * Checks if the author is active.
     * 
     * @return true if the author is active, false otherwise
     */
    public Boolean getIsActive() {
        return isActive;
    }
    
    /**
     * Sets the active status of the author.
     * 
     * @param isActive the active status to set
     */
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
}
