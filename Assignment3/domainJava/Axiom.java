package domain;

import java.util.Objects;

/**
 * Represents an axiom in a domain.
 */
public class Axiom extends DomainTag{
    private String formalism;
    private String expression;

    /**
     * Constructs a new Axiom object with the specified name, formalism, expression, and domain.
     *
     * @param name the name of the axiom
     * @param formalism the formalism of the axiom
     * @param expression the expression of the axiom
     * @param domain the domain of the axiom
     */
    public Axiom(String name, String formalism, String expression, String domain) {
        this.name = name;
        this.formalism = formalism;
        this.expression = expression;
        this.domain = domain;
    }

    /**
     * Returns the formalism of the axiom.
     *
     * @return the formalism of the axiom
     */
    public String getFormalism() {
        return formalism;
    }

    /**
     * Sets the formalism of the axiom.
     *
     * @param formalism the formalism to set
     */
    public void setFormalism(String formalism) {
        this.formalism = formalism;
    }

    /**
     * Returns the expression of the axiom.
     *
     * @return the expression of the axiom
     */
    public String getExpression() {
        return expression;
    }

    /**
     * Sets the expression of the axiom.
     *
     * @param expression the expression to set
     */
    public void setExpression(String expression) {
        this.expression = expression;
    }

    // Add getters and setters for name, domain, and values

    /**
        * Indicates whether some other object is "equal to" this one.
        * 
        * @param obj the reference object with which to compare
        * @return true if the two Axioms have the same name; false otherwise
        */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }
        Axiom axiom = (Axiom) obj;
        return name.equals(axiom.name);
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
