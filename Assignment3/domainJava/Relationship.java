package domain;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import java.util.Vector;

public class Relationship extends Entity {
	private static final String universalRelationshipName = "Relationship";
	private String inverse;
	private Vector<Reference> references = new Vector<>();
	private ArrayList<Relationship> children = new ArrayList<>();
	private Relationship parent;
//ste ereditati da Entity
//	private String domain;
//	private String name;
//	private List<Attribute> attributes = new LinkedList<>();
	
	private boolean symmetric;
	
	public Relationship(String domain, String name, String inverse) {
		super(name, domain);
//		this.domain = domain;
//		this.name = name;
		this.inverse = inverse;
	}
	
	public Relationship(String domain, String name, String inverse, Relationship parent) {
		super(name, domain);
		this.inverse = inverse;
		this.setParentRelationship(parent);
	}
	
	public Relationship(String domain, String name, String inverse, Boolean symmetric, List<Attribute> attributes) {
		this(domain, name, inverse);
		this.symmetric = symmetric;
		this.attributes = attributes;
	}
	
	/*
	public TreeNode getSubrelationshipsTree() {
		TreeNode rootRelationship = new DefaultTreeNode(this);
		if(this.children != null) {
			for(Relationship r : this.children) {
				rootRelationship.getChildren().add(r.getSubrelationshipsTree()); // e.getSubclassesTree().setParent(rootClass); non funziona
			}
		}	
		return rootRelationship;
	}
	*/
	
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		return name /*+ " (" + inverse + ")"*/;
	}
	
	public void setReferences(Vector<Reference> references) {
		this.references = references;
	}

	public void removeRef(Reference ref) {
		references.remove(ref);
	}
	public Vector<Reference> getReferences() {
		return references;
	}
	public TreeSet<String> getSubjects() {
		TreeSet<String> subjects = new TreeSet<String>();
		for (Reference r : references) {
			subjects.add(r.getSubject());
		}
		//Collections.sort(subjects);
		return subjects;
	}
	public Reference getReference(String subject, String object) {
		for(Reference r : references) {
			if(r.getSubject().equalsIgnoreCase(subject) && r.getObject().equalsIgnoreCase(object)) {
				return r;
			}
		}
		return null;
	}

	public TreeSet<String> getObjects() {
		TreeSet<String> objects = new TreeSet<String>();
		for (Reference r : references) {
			objects.add(r.getObject());
		}
		//Collections.sort(objects);
		return objects;
	}

	public Vector<String> getSubj_Objs(String subject) {
		Vector<String> objects = new Vector<String>();
		for (Reference r : references) {
			if (r.getSubject().equals(subject))
				objects.add(r.getObject());
		}
		return objects;
	}
	
	public void removeAll(Vector<Reference> refs) {
		references.removeAll(refs);
	}
	
	public Vector<String> getObj_Subjs(String object) {
		Vector<String> subjects = new Vector<String>();
		for (Reference r : references) {
			if (r.getObject().equals(object))
				subjects.add(r.getSubject());
		}
		return subjects;
	}
	
	public List<Attribute> getAllAttributes() { //ste sovrascrive quella di Entity fino a quando non ci saranno le sottorelazioni
		ArrayList<Attribute> allAttributes = new ArrayList<Attribute>(attributes);
		allAttributes.add(new Attribute("notes","text"));
		return allAttributes;
	}
	
	public String getName() {
		return name;
	}
	public void set(String name, String inverse) {
		setName(name);
		setInverse(inverse);
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

	public void addReference(Reference ref) {
		for (Reference r : references)
			if (ref.getSubject().equals(r.getSubject()) && ref.getObject().equals(r.getObject())) {
				references.remove(r);
				break; // trovato, esce dal ciclo anticipatamente
			}
		references.add(ref);
	}

	public ArrayList<Relationship> getChildrenRelationships() {
		return children;
	}

	public void setChildrenRelationship(ArrayList<Relationship> children) {
		this.children = children;
	}
	
	public void addChildrenRelationship(Relationship relationship) {
		this.children.add(relationship);
	}

	public void addReferences(Vector<Reference> references) {
		for(Reference ref : references) {
			addReference(ref);
		}
	}

	public void setParentRelationship(Relationship parent) {
		this.parent = parent;
		parent.addChild(this);
	}
	
	public boolean isTopRelationship() {
		return this.parent.getName().equals(universalRelationshipName);
	}

}
