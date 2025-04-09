package domain;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.primefaces.model.TreeNode;

import domain.Attribute;
import domain.DomainData;
import domain.Entity;
import domain.Reference;
import domain.Relationship;

public class TranslatorAPIProlog implements Serializable {

	private static final long serialVersionUID = 1L;
	private HashMap<String, ArrayList<Attribute>> attributes;
	private HashMap<String, ArrayList<Attribute>> attributesRel;
	private String domainName;
	private String recur = "";

	/* TODO tartarello
	 * 
	 * parametro String output_path e' provvisorio per testare la classe in maniera stand-alone al progetto
	 * togliere il parametro e ripristinare il vecchio metodo di esportazione della classe owl quando verra' inserita la classe all'interno del progetto 
	 * 
	 */
//	public TranslatorProlog(DomainData domain, String output_path) throws IOException {
	public TranslatorAPIProlog(DomainData domain) throws IOException {
		String content = "domain(" + domain.getDomain().toLowerCase() + ").\n";
		content += createEntities(domain.getTopEntities());
		content += createRelationships(domain.getTopRelationships());
		
		// output originale
		
		content = writeFactsWithId(content, "id"); // Tartarello
		System.out.println(content);
		
		//TODO tartarello
		//OutputStream output = new FileOutputStream(output_path, false);
		//content = writeFactsWithId(content, "id");
		//output.write(content.getBytes());
		//output.close();
	}
	
	// TODO tartarello - fact(Id,F,1).
	private static String writeFactsWithId(String content, String id_prefix) {
		int id = 0;
		String contentWithId = "";
		String[] facts = content.split("\n");
		for(String fact: facts) {
			fact = fact.substring(0, fact.length()-1);
			fact = "fact(" + id_prefix + "_" + id + ", " + fact + ", 1).\n";
			id++;
			contentWithId += fact;
		}
		return contentWithId;
	}

	private static String createEntities(List<Entity> entities) {
		String values = "";
		String att = "";
		for (Entity entity : entities) {
			values += "entity(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ").\n";
			for (Attribute attr : entity.getAttributes()) {
				att += "attribute(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
						+ attr.getName().toLowerCase() + ", " + attr.getDataType().toLowerCase() + ").\n";
				if(!attr.getValues().isEmpty()) {
					att += "values(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ", " + attr.getValuesToStringToLower() + ").\n";
				}
				if (attr.getMandatory() == true) {
					att += "mandatory(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ").\n";
				}
				if (attr.isDisplay() == true) {
					att += "display(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ").\n";
				}
				if (attr.isDistinguishing() == true) {
					att += "distinguishing(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ").\n";
				}
				if (attr.getTarget() != null) {
					att += "target(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", "
							+ attr.getName().toLowerCase() + ", " + attr.getTarget().toLowerCase() +").\n";
				}
			}
			for(Entity e : entity.getChildren()) {
				att += "parent(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
						+ e.getName().toLowerCase() + ").\n";
				att += writeEntity(e);
			}
		}
		values += att;
		return values;
	}

	private static String writeEntity(Entity entity) {
		String att = "";
		att += "entity(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ").\n";
		for (Attribute attr : entity.getNewAttributes()) {
			att += "attribute(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
					+ attr.getName().toLowerCase() + ", " + attr.getDataType().toLowerCase() + ").\n";
			if(!attr.getValues().isEmpty()) {
				att += "values(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", "
						+ attr.getName().toLowerCase() + ", " + attr.getValuesToStringToLower() + ").\n";
			}		
			if (attr.getMandatory() == true) {
				att += "mandatory(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
						+ attr.getName().toLowerCase() + ").\n";
			}
			if (attr.isDisplay() == true) {
				att += "display(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
						+ attr.getName().toLowerCase() + ").\n";
			}
			if (attr.isDistinguishing() == true) {
				att += "distinguishing(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
						+ attr.getName().toLowerCase() + ").\n";
			}
			if (attr.getTarget() != null) {
				att += "target(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", "
						+ attr.getName().toLowerCase() + ", " + attr.getTarget().toLowerCase() +").\n";
			}
		}
		for(Entity e : entity.getChildren()) {
			att += "parent(" + entity.getDomain().toLowerCase() + ", " + entity.getName().toLowerCase() + ", " 
					+ e.getName().toLowerCase() + ").\n";
			att += writeEntity(e);
		}
		return att;
	}

	private static String createRelationships(List<Relationship> relationships) {
		String att = "";
		for (Relationship relation : relationships) {
			for(Reference ref : relation.getReferences()) {
				att += "relationship(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
						+ ref.getSubject().toLowerCase() + ", " + ref.getObject().toLowerCase() + ").\n";
			}
			att += "inverse(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
					+ relation.getInverse().toLowerCase() + ").\n";
			for (Attribute attr : relation.getAttributes()) {
				att += "attribute(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
						+ attr.getName().toLowerCase() + ", " + attr.getDataType().toLowerCase() + ").\n";
				if(!attr.getValues().isEmpty()) {
					att += "values(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ", " + attr.getValuesToStringToLower() + ").\n";
				}
				if (attr.getMandatory() == true) {
					att += "mandatory(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ").\n";
				}
				if (attr.isDisplay() == true) {
					att += "display(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ").\n";
				}
				if (attr.isDistinguishing() == true) {
					att += "distinguishing(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() 
								+ ", " + attr.getName().toLowerCase() + ").\n";
				}
				if (attr.getTarget() != null) {
					att += "target(" + relation.getDomain().toLowerCase() + ", " + relation.getName().toLowerCase() + ", " 
							+ attr.getName().toLowerCase() + ", " + attr.getTarget().toLowerCase() +").\n";
				}
			}
		}
		return att;
	}

	public ArrayList<String> getClassi(TreeNode classi) {
		ArrayList<String> s = new ArrayList<String>();
		List<TreeNode> children = classi.getChildren();
		for (TreeNode t : children) {
			s.add(t.toString());
		}
		return s;
	}

	public HashMap<String, ArrayList<Attribute>> getAttributes() {
		return attributes;
	}
	public void setAttributes(HashMap<String, ArrayList<Attribute>> attributes) {
		this.attributes = attributes;
	}

	public HashMap<String, ArrayList<Attribute>> getAttributesRel() {
		return attributesRel;
	}
	public void setAttributesRel(HashMap<String, ArrayList<Attribute>> attributesRel) {
		this.attributesRel = attributesRel;
	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}

	public String getDomainName() {
		return domainName;
	}
	public void setDomainName(String domainName) {
		this.domainName = domainName;
	}

	public ArrayList<String> recursiveTree(TreeNode node) {
		ArrayList<String> classi = new ArrayList<String>();
		List<TreeNode> children = node.getChildren();
		for (int j = 0; j < node.getChildCount(); j++) {
			classi.add(children.get(j).toString());
			recursiveTree(children.get(j));
		}
		return classi;
	}

	public void recursiveTreeTax(String s, TreeNode node, String superV) {
		List<TreeNode> children = node.getChildren();
		for (int j = 0; j < node.getChildCount(); j++) {
			recur += s + superV + ", " + children.get(j).toString() + ").\n";
			recursiveTreeTax(s, children.get(j), children.get(j).toString());
		}
	}

	public String getRecur() {
		return recur;
	}
	public void setRecur(String recur) {
		this.recur = recur;
	}

	private String createList(ArrayList<String> lista) {
		String list = "";
		int i;
		list += "[";
		for (i =0; i < lista.size()-1; i++) {
			list += (lista.get(i)+", ");
		}
		list += lista.get(i);
		list += "]";
		return list;
	}

}
