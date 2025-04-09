package domain;

import java.util.Collections;
import java.util.Vector;

public class RelationshipSte {
	private String name;
	private String inverse;
	private boolean symmetric;
	private Vector<Attribute> attributes;
	private Vector<Reference> relationships;
	
	public RelationshipSte(String name, String inverse, Boolean symmetric, Vector<Attribute> attributes) {
		this.name = name;
		this.inverse = inverse;
		this.symmetric = symmetric;
		this.attributes = attributes;
	}
	
	
	public Vector<String> getSubjects() {
		Vector<String> subjects = new Vector<String>();
		for (Reference r : relationships) {
			subjects.add(r.getSubject());
		}
		Collections.sort(subjects);
		return subjects;
	}

	public Vector<String> getObjects() {
		Vector<String> objects = new Vector<String>();
		for (Reference r : relationships) {
			objects.add(r.getObject());
		}
		Collections.sort(objects);
		return objects;
	}

	public Vector<String> getSubj_Objs(String subject) {
		Vector<String> objects = new Vector<String>();
		for (Reference r : relationships) {
			if (r.getSubject().equals(subject))
				objects.add(r.getObject());
		}
		return objects;
	}
	
	public Vector<String> getObj_Subjs(String object) {
		Vector<String> subjects = new Vector<String>();
		for (Reference r : relationships) {
			if (r.getObject().equals(object))
				subjects.add(r.getSubject());
		}
		return subjects;
	}
	
	
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getInverse() {
		return inverse;
	}
	public void setInverse(String inverse) {
		this.inverse = inverse;
	}
	public Boolean getSymmetric() {
		return symmetric;
	}
	public void setSymmetric(Boolean symmetric) {
		this.symmetric = symmetric;
	}
	public Vector<Attribute> getAttributes() {
		return attributes;
	}
	public void setAttributes(Vector<Attribute> attributes) {
		this.attributes = attributes;
	}

}
