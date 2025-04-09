 package domain;


public class RelationTriple {

	private Instance subject;
	private Instance relation;
	private Instance object;
	
	
	public RelationTriple() {}
	
	public RelationTriple(Instance subject, Instance relation, Instance object) {
		this.subject = subject;
		this.relation = relation;
		this.object = object;
	}
	
	public Instance getSubject() {
		return subject;
	}
	public void setSubject(Instance subject) {
		this.subject = subject;
	}
	public Instance getRelation() {
		return relation;
	}
	public void setRelation(Instance relation) {
		this.relation = relation;
	}
	public Instance getObject() {
		return object;
	}
	public void setObject(Instance object) {
		this.object = object;
	}

}
