package domain;

import java.util.Set;
import java.util.Objects;

/**
 * Represents a Union domain tag.
 * A Union is a type of DomainTag that contains a set of values.
 */
public class Union extends DomainTag{
    private Set<String> values;

    /**
     * Constructs a Union object with the specified name, domain, and values.
     * 
     * @param name   the name of the Union
     * @param domain the domain of the Union
     * @param values the set of values in the Union
     */
    public Union(String name, String domain, Set<String> values) {
        this.name = name;
        this.domain = domain;
        this.values = values;
    }

    /**
     * Returns the set of values in the Union.
     * 
     * @return the set of values
     */
    public Set<String> getValues() {
        return values;
    }

    /**
     * Sets the set of values in the Union.
     * 
     * @param values the set of values to set
     */
    public void setValues(Set<String> values) {
        this.values = values;
    }
    
    
    /**
        * Indicates whether some other object is "equal to" this one.
        * 
        * @param obj the reference object with which to compare
        * @return true if the two Unions have the same name; false otherwise
        */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }
        Union union = (Union) obj;
        return name.equals(union.name);
    }

    /**
     * Returns the hash code value for this Union object.
     * 
     * @return the hash code value for this Union object as the hash of the name attribute.
     */
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}
