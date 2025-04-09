package domain;

import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import org.primefaces.model.TreeNode;

/**
 * Represents an attribute in a domain.
 * An attribute can have various properties such as mandatory, distinguishing, display, data type, and values.
 */
public class Attribute extends Tag implements Cloneable {
	public boolean mandatory = false;
	public boolean distinguishing = false;
	public boolean display = false;
	private List<String> values = new ArrayList<>();
	public String dataType;
	private String target;

	private TreeNode subClasses;
	private TreeNode subClassesSelect;

	/**
	 * Constructs a new Attribute object with the given name.
	 * @param name The name of the attribute.
	 */
	public Attribute(String name) {
		this.name = name;
	}

	/**
	 * Constructs a new Attribute object with the given name and data type.
	 * @param name The name of the attribute.
	 * @param dataType The data type of the attribute.
	 */
	public Attribute(String name, String dataType) {
		this(name);
		this.dataType = dataType;
	}

	/**
	 * Constructs a new Attribute object with the given name, mandatory flag, and values.
	 * @param name The name of the attribute.
	 * @param mandatory Indicates if the attribute is mandatory.
	 * @param values The list of values of the attribute (data type is therefore set to "select").
	 */
	public Attribute(String name, boolean mandatory, List<String> values) {
		this.name = name;
		this.dataType = "select";
		this.mandatory = mandatory;
		this.values = values;
	}

	/**
	 * Constructs a new Attribute object with the given name, data type, and mandatory flag.
	 * @param name The name of the attribute.
	 * @param dataType The data type of the attribute.
	 * @param mandatory Indicates if the attribute is mandatory.
	 */
	public Attribute(String name, String dataType, boolean mandatory) {
		this(name, dataType);
		this.mandatory = mandatory;
	}

	/**
	 * Constructs a new Attribute object with the given name, data type, and mandatory flag.
	 * @param name The name of the attribute.
	 * @param dataType The data type of the attribute.
	 * @param mandatory Indicates if the attribute is mandatory. (String that is checked if it is "true", otherwise it is set as false)
	 */
	public Attribute(String name, String dataType, String mandatory) {
		this(name, dataType);
		this.mandatory = mandatory.equals("true");
	}

	/**
	 * Constructs a new Attribute object with the given name, data type, mandatory flag, distinguishing flag, and display flag.
	 * @param name The name of the attribute.
	 * @param dataType The data type of the attribute.
	 * @param mandatory Indicates if the attribute is mandatory.
	 * @param distinguishing Indicates if the attribute is distinguishing.
	 * @param display Indicates if the attribute is displayable.
	 */
	public Attribute(String name, String dataType, boolean mandatory, boolean distinguishing, boolean display) {
		this(name, dataType, mandatory);
		this.distinguishing = distinguishing;
		this.display = display;
	}

	/**
	 * Constructs a new Attribute object with the given name and values.
	 * @param name The name of the attribute.
	 * @param values The list of values of the attribute (data type is therefore set to "select").
	 */
	public Attribute(String name, List<String> values) {
		this.name = name;
		this.dataType = "select";
		this.values = values;
	}

	/**
	 * Constructs a new Attribute object with the given name and sub-classes.
	 * @param name The name of the attribute.
	 * @param values The sub-classes of the attribute.
	 */
	public Attribute(String name, TreeNode values) {
		this.name = name;
		this.dataType = "taxonomy";
		this.subClasses = values;
	}

	/**
	 * Checks if the attribute is descriptive.
	 * An attribute is descriptive if it is mandatory or distinguishing.
	 * @return true if the attribute is descriptive, false otherwise.
	 */
	public boolean isDescriptive() {
		return mandatory || distinguishing;
	}

	/**
	 * Gets the mandatory flag of the attribute.
	 * @return true if the attribute is mandatory, false otherwise.
	 */
	public boolean getMandatory() {
		return mandatory;
	}

	/**
	 * Checks if the attribute is mandatory.
	 * @return true if the attribute is mandatory, false otherwise.
	 */
	public boolean isMandatory() {
		return mandatory;
	}

	/**
	 * Sets the mandatory flag of the attribute.
	 * @param mandatory true if the attribute is mandatory, false otherwise.
	 */
	public void setMandatory(boolean mandatory) {
		this.mandatory = mandatory;
	}

	/**
	 * Checks if the attribute is distinguishing.
	 * @return true if the attribute is distinguishing, false otherwise.
	 */
	public boolean isDistinguishing() {
		return distinguishing;
	}

	/**
	 * Sets the distinguishing flag of the attribute.
	 * @param distinguishing true if the attribute is distinguishing, false otherwise.
	 */
	public void setDistinguishing(boolean distinguishing) {
		this.distinguishing = distinguishing;
	}

	/**
	 * Gets the data type of the attribute.
	 * @return The data type of the attribute.
	 */
	public String getDataType() {
		return dataType;
	}

	/**
	 * Sets the data type of the attribute.
	 * @param dataType The data type of the attribute.
	 */
	public void setDataType(String dataType) {
		this.dataType = dataType;
	}

	/**
	 * Sets the target of the attribute.
	 * @param target The target of the attribute.
	 */
	public void setTarget(String target) {
		this.target = target;
	}

	/**
	 * Gets the values of the attribute.
	 * @return The values of the attribute.
	 */
	public List<String> getValues() {
		return values;
	}

	/**
	 * Gets the values of the attribute as a vector of lowercase strings.
	 * @return The values of the attribute as a vector of lowercase strings.
	 */
	public Vector<String> getValuesToStringToLower() {
		Vector<String> s = new Vector<>();
		for (int i=0; i<values.size(); i++) {
			s.add(values.get(i).toLowerCase());
		}
		return s;
	}

	/**
	 * Sets the values of the attribute.
	 * @param values The values of the attribute.
	 */
	public void setValues(List<String> values) {
		this.values = values;
	}

	/**
	 * Removes all the values of the attribute.
	 */
	public void removeValues() {
		this.values.removeAll(this.values);
	}

	/**
	 * Sets the values of the attribute as strings.
	 * @param values The values of the attribute as strings.
	 */
	public void setValuesString(List<String> values) {
		List<String> s = new ArrayList<>(values);
		setValues(s);
	}

	/**
	 * Adds a value to the attribute.
	 * @param value The value to be added.
	 */
	public void addValue(String value) {
		values.add(value);
	}

	/**
	 * Removes a value from the attribute.
	 * @param value The value to be removed.
	 */
	public void removeValue(String value) {
		values.remove(value);
	}

	/**
	 * Gets the sub-classes of the attribute 
	 * @return The sub-classes of the attribute. 
	 */
	public TreeNode getSubClasses() {
		return subClasses;
	}

	/**
	 * Sets the sub-classes of the attribute (data type should therefore be set to "tree").
	 * @param values The sub-classes of the attribute.
	 */
	public void setSubClasses(TreeNode values) {
		this.subClasses = values;
	}

	/**
	 * Checks if the attribute is displayable.
	 * @return true if the attribute is displayable, false otherwise.
	 */
	public boolean isDisplay() {
		return display;
	}

	/**
	 * Sets the display flag of the attribute.
	 * @param display true if the attribute is displayable, false otherwise.
	 */
	public void setDisplay(boolean display) {
		this.display = display;
	}

	/**
	 * Gets the display flag of the attribute.
	 * @return true if the attribute is displayable, false otherwise.
	 */
	public boolean getDisplay() {
		return display;
	}

	/**
	 * Gets the target of the attribute.
	 * @return The target of the attribute.
	 */
	public String getTarget() {
		return target;
	}

	public TreeNode getSubClassesSelect() {
		return subClassesSelect;
	}

	public void setSubClassesSelect(TreeNode subClassesSelect) {
		this.subClassesSelect = subClassesSelect;
	}

	/**
	 * Constructs a new empty Attribute object.
	 */
	public Attribute() {
	}

	/**
	 * Gets the values of the attribute as a vector of strings.
	 * @return The values of the attribute as a vector of strings.
	 */
	public Vector<String> getValuesToString() {
		Vector<String> s = new Vector<>();
		for (int i=0; i<values.size(); i++) {
			s.add(values.get(i));
		}
		return s;
	}

	/**
	 * Returns the name of the attribute.
	 * @return The name of the attribute.
	 */
	@Override
	public String toString() {
		return name;
	}

	/**
	 * Creates and returns a copy of this attribute.
	 * @return A copy of this attribute.
	 * @throws CloneNotSupportedException if cloning is not supported for this attribute.
	 */
	public Object clone() throws CloneNotSupportedException {
		return super.clone();
	}
}
