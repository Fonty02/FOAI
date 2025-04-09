package domain;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Vector;
import java.util.stream.Collectors;

import org.primefaces.model.DefaultTreeNode;
import org.primefaces.model.TreeNode;

public class Entity extends DomainTag{
	private static final String universalClassName = "Entity";
	private List<String> values = new ArrayList<String>();
	private String graphBrainID;
	protected List<Attribute> attributes = new ArrayList<Attribute>();
	protected List<Entity> children = new ArrayList<Entity>();
	protected Entity parent;
	protected boolean _abstract=false;

	public Entity(String name) {
		this.name = name;
	}
	
	public Entity(String name, String domain) {
		this(name);
		this.domain = domain;
	}
	
	public boolean isAbstract() {
		return _abstract;
	}

	public void setAbstract(boolean _abstract) {
		this._abstract = _abstract;
	}

	public List<Attribute> getAttributes() {
		return attributes;
	}
	
	public String getTop() {
		if(parent.getName().equals("Entity") || parent.getName().equals("Relationship"))
			return this.getName();
		return parent.getTop();
	}
	
	public List<Attribute> getAllAttributes() {
		List<Attribute> pathAttributes = new ArrayList<Attribute>();
		if (parent != null)
			pathAttributes = parent.getAllAttributes();
		pathAttributes.addAll(this.getAttributes());
		return pathAttributes;
	}

	public List<String> getAllAttributesToString() {
		ArrayList<String> allAttributesToString = new ArrayList<>();
		for (Attribute attr : getAllAttributes())
			allAttributesToString.add(attr.getName());
		return allAttributesToString;
	}
	
	public List<Attribute> getMandatoryAttributes(){
		List<Attribute> mandatoryAttributes = new ArrayList<>();
		List<Attribute> allAttributes = getAllAttributes();
		for (Attribute attr : allAttributes)
			if (attr.isMandatory())
				mandatoryAttributes.add(attr);
		return mandatoryAttributes;
	}

	public void addChild(Entity child) {
		children.add(child); //ste mettere in ordine alfabetico?
		child.setParent(this);
	}
	
	public void removeAllAttributes(Entity entity) {
		attributes.removeAll(entity.getAttributes());
	}
	
	public Entity getChild(String name) {
		for(Entity e : getChildren())
			if(e.getName().equalsIgnoreCase(name))
				return e;
		return null;
	}
	
	public void run() {}
	
	public List<Entity> getChildren() {
		return children;
	}
	public ArrayList<String> getChildrenToString() {
		ArrayList<String> childrenToString = new ArrayList<>();
		for(Entity e : getChildren())
			childrenToString.add(e.getName());
		return childrenToString;
	}
	public void setChildren(List<Entity> children) {
		this.children = children;
	}
	public Entity getParent() {
		return parent;
	}
	public void setParent(Entity parent) {
		this.parent = parent;
//		this.attributes.addAll(parent.getAttributes());
	}
	
	public ArrayList<Attribute> getNewAttributes() {
		ArrayList<Attribute> s = new ArrayList<>();
		for(Attribute a : attributes) {
			if(!parent.getAttributesToString().contains(a.getName())) {
				s.add(a);
			}
		}
		return s;
	}
	
	public ArrayList<String> getAttributesToString() {
		return new ArrayList<String>(attributes.stream()
										 	   .map(Attribute::getName)
										 	   .collect(Collectors.toList())
							  		);
	}
	
	public Attribute getAttribute(String attribute) {
		for(Attribute a : attributes) {
			if(a.getName().equals(attribute)) {
				return a;
			}
		}
		return null;
	}
	
	@Override
	public boolean equals(Object obj) {
		// TODO Auto-generated method stub
		Entity other = (Entity) obj;
		return name.equals(other.name) && (domain == null ? other.domain == null : domain.equals(other.domain));
	}
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		return name;
	}
	public void addAttribute(Attribute attr) {
		attributes.add(attr);
	}
	public void addAttributes(Vector<Attribute> attrs) {
//		attributes.addAll(attrs);
		for (Attribute a : attrs) { // se esiste lo sovrascrive
			for (Attribute old : attributes)
				if (old.getName().equals(a.getName())) {
					attributes.remove(old);
					break; // trovato, esce dal ciclo anticipatamente
				}
			attributes.add(a);
		}
	}
	public void removeAttribute(String attribute) {
		attributes.remove(getAttribute(attribute));
	}
	public void setAttributes(List<Attribute> attributes) {
		this.attributes = attributes;
	}

	public Entity findSubClass(String nameSubClass) {
		if (name.equals(nameSubClass))
			return this;
		else {
			Entity subClass = null;
			boolean found = false;
			for (Entity e : children)
				if (!found) {
					subClass = e.findSubClass(nameSubClass);
					if (subClass != null)
						found = true;
				}
			return subClass;
		}
	}

	public List<Entity> getClassPath() {
		List<Entity> path = new LinkedList<Entity>();
		Entity parent = this.getParent();
		if (parent != null) {
			path = parent.getClassPath();
		}
		path.add(this);
		return path;
	}

	public List<String> getAllSubclassNames(boolean subclassRestriction) {
		if (subclassRestriction) {
			List<String> subClassNames = new LinkedList<String>();
			subClassNames.add(this.getName());
			return subClassNames;
		} else
			return getAllSubclassesToString();
	}
	
	public List<Entity> getAllSubclasses() {
		List<Entity> subclasses = new LinkedList<Entity>();
		subclasses.add(this);
		if(this.children != null) {
			for(Entity e : this.children) {
				subclasses.addAll(e.getAllSubclasses());
			}
		}
		return subclasses;
	}
	
//	public List<String> findSubClasses() { //ste sostituito da getAllSubclassesToString()

	public List<String> getAllSubclassesToString() {
		List<String> subclasses = new LinkedList<String>();
//		if (this.parent != null)
			subclasses.add(this.name);
//		if(this.children != null) {
			for(Entity e : this.children) {
				subclasses.addAll(e.getAllSubclassesToString());
			}
//		}
		return subclasses;
	}
	
	public TreeNode getSubclassesTree() {
		TreeNode rootClass = new DefaultTreeNode(this);
		if(this.children != null)
			for(Entity e : this.children)
				rootClass.getChildren().add(e.getSubclassesTree()); // e.getSubclassesTree().setParent(rootClass); non funziona
		return rootClass;
	}
	
	public Entity existsSubclass(String subclassName) {
		if (this.getName().equals(subclassName))
			return this;
		else if (this.children != null) {
			Entity found;
			for(Entity e : this.children) {
				found = e.existsSubclass(subclassName);
				if (found != null)
					return found;
			}
		}
		return null;
	}
	
	public boolean isTopClass() {
		return this.parent.getName().equals(universalClassName);
	}
	public boolean hasChild(String entityName) {
		for(Entity e : this.getChildren()) {
			if(e.getName().equalsIgnoreCase(entityName)) {
				return true;
			}
		}
		return false;
	}
	
	public boolean hasAncestor(String entityName) {
		Entity e = this;
		while(!e.getParent().getName().equals("Entity")) {
			e = e.getParent();
			if(e.getName().equals(entityName)) {
				return true;
			}
		}
		return false;
	}
	
	private void removeChild(String childName) {
		int pos = -1;
		for(int i=0; i<getChildren().size() && pos==-1; i++) {
			if(getChildren().get(i).getName().equalsIgnoreCase(childName)) {
				pos = i;
			}
		}
		getChildren().remove(pos);
	}
	
	public void detach() {
		getParent().removeChild(name);
	}

	public List<String> getValues() {
		return values;
	}
	public void setValues(List<String> values) {
		this.values = values;
	}

	public String getGraphBrainID() {
		return graphBrainID;
	}
	public void setGraphBrainID(String graphBrainID) {
		this.graphBrainID = graphBrainID;
	}

}
