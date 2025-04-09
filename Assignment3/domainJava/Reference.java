package domain;

import java.util.Vector;

/**
 * The Reference class represents an instance of a relationship, a link between two entities.
 * It contains information about the subject, object, and attributes of the reference.
 */
public class Reference {
	
	private String subject;
	private String object;
	private Vector<Attribute> attributes;

	/**
	 * Constructs a Reference object with the given subject and object.
	 * @param subject the subject of the reference
	 * @param object the object of the reference
	 */
	public Reference(String subject, String object) {
		this.subject = subject;
		this.object = object;
	}
	
	/**
	 * Constructs a Reference object with the given subject, object, and attributes.
	 * @param subject the subject of the reference
	 * @param object the object of the reference
	 * @param attributes the attributes of the reference
	 */
	public Reference(String subject, String object, Vector<Attribute> attributes) {
		this(subject, object);
		this.attributes = attributes;
	}
	
	/**
	 * Returns the subject of the reference.
	 * @return the subject of the reference
	 */
	public String getSubject() {
		return subject;
	}
	
	/**
	 * Sets the subject of the reference.
	 * @param subject the subject of the reference
	 */
	public void setSubject(String subject) {
		this.subject = subject;
	}
	
	/**
	 * Returns the object of the reference.
	 * @return the object of the reference
	 */
	public String getObject() {
		return object;
	}
	
	/**
	 * Sets the object of the reference.
	 * @param object the object of the reference
	 */
	public void setObject(String object) {
		this.object = object;
	}
	
	/**
	 * Returns the attributes of the reference.
	 * @return the attributes of the reference
	 */
	public Vector<Attribute> getAttributes() {
		return attributes;
	}
	
	/**
	 * Sets the attributes of the reference.
	 * @param attributes the attributes of the reference
	 */
	public void setAttributes(Vector<Attribute> attributes) {
		this.attributes = attributes;
	}
	
	/**
	 * Returns a string representation of the Reference object.
	 * @return a string representation of the Reference object as "Reference [subject=..., object=...]"
	 */
	@Override
	public String toString() {
		return "Reference [subject=" + subject + ", object=" + object + "]";
	}
	
}
