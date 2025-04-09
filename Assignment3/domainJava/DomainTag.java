package domain;

/**
 * The abstract class DomainTag represents a tag associated with a specific domain.
 * It extends the Tag class and provides methods to get and set the domain.
 * @see Tag
 */
public abstract class DomainTag extends Tag {

	protected String domain;

	/**
	 * Returns the domain associated with this tag.
	 *
	 * @return the domain associated with this tag
	 */
	public String getDomain() {
		return domain;
	}

	/**
	 * Sets the domain associated with this tag.
	 *
	 * @param domain the domain to be set
	 */
	public void setDomain(String domain) {
		this.domain = domain;
	}

}
