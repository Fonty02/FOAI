package domain;

/**
 * The abstract base class for all tags.
 */
public abstract class Tag {

	protected String name;
	protected String description;
	protected String notes;

	/**
	 * Gets the name of the tag.
	 *
	 * @return The name of the tag.
	 */
	public String getName() {
		return name;
	}

	/**
	 * Sets the name of the tag.
	 *
	 * @param name The name of the tag.
	 */
	public void setName(String name) {
		this.name = name;
	}A

	/**
	 * Gets the description of the tag.
	 *
	 * @return The description of the tag.
	 */
	public String getDescription() {
		return description;
	}

	/**
	 * Sets the description of the tag.
	 *
	 * @param description The description of the tag.
	 */
	public void setDescription(String description) {
		this.description = description;
	}

	/**
	 * Gets the notes of the tag.
	 *
	 * @return The notes of the tag.
	 */
	public String getNotes() {
		return notes;
	}

	/**
	 * Sets the notes of the tag.
	 *
	 * @param notes The notes of the tag.
	 */
	public void setNotes(String notes) {
		this.notes = notes;
	}

}
