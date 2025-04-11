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

/**
 * A class that translates domain model data into Prolog facts.
 * This class is responsible for converting domain entities, relationships, and attributes
 * into Prolog syntax for knowledge representation.
 */
public class TranslatorAPIProlog implements Serializable {

    /** Serial version UID for serialization. */
    private static final long serialVersionUID = 1L;
    
    /** HashMap containing attributes for entities, indexed by entity name. */
    private HashMap<String, ArrayList<Attribute>> attributes;
    
    /** HashMap containing attributes for relationships, indexed by relationship name. */
    private HashMap<String, ArrayList<Attribute>> attributesRel;
    
    /** The name of the domain being translated. */
    private String domainName;
    
    /** Temporary string buffer used for accumulating recursive tree representation. */
    private String recur = "";

    /**
     * Constructor that creates a Prolog representation of a domain model.
     * 
     * @param domain The domain data model to be translated into Prolog facts
     * @throws IOException If an I/O error occurs during the process
     */
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
    
    /**
     * Converts Prolog facts to facts with unique IDs.
     * Transforms each fact into the format fact(id_X, fact_content, 1).
     * 
     * @param content The string containing Prolog facts to be processed
     * @param id_prefix The prefix to use for the fact IDs
     * @return A string of Prolog facts with unique IDs
     */
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

    /**
     * Creates Prolog facts for a list of entities and their attributes.
     * 
     * @param entities List of top-level entities to process
     * @return A string representation of entities and their attributes in Prolog syntax
     */
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

    /**
     * Recursively processes an entity and its children, generating Prolog facts.
     * 
     * @param entity The entity to process
     * @return A string representation of the entity, its attributes, and children in Prolog syntax
     */
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

    /**
     * Creates Prolog facts for a list of relationships and their attributes.
     * 
     * @param relationships List of top-level relationships to process
     * @return A string representation of relationships and their attributes in Prolog syntax
     */
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

    /**
     * Extracts class names from a tree node's children.
     * 
     * @param classi The tree node containing class information
     * @return An ArrayList of class names from the tree node's children
     */
    public ArrayList<String> getClassi(TreeNode classi) {
        ArrayList<String> s = new ArrayList<String>();
        List<TreeNode> children = classi.getChildren();
        for (TreeNode t : children) {
            s.add(t.toString());
        }
        return s;
    }

    /**
     * Gets the attributes map for entities.
     * 
     * @return HashMap mapping entity names to their attributes
     */
    public HashMap<String, ArrayList<Attribute>> getAttributes() {
        return attributes;
    }
    
    /**
     * Sets the attributes map for entities.
     * 
     * @param attributes HashMap mapping entity names to their attributes
     */
    public void setAttributes(HashMap<String, ArrayList<Attribute>> attributes) {
        this.attributes = attributes;
    }

    /**
     * Gets the attributes map for relationships.
     * 
     * @return HashMap mapping relationship names to their attributes
     */
    public HashMap<String, ArrayList<Attribute>> getAttributesRel() {
        return attributesRel;
    }
    
    /**
     * Sets the attributes map for relationships.
     * 
     * @param attributesRel HashMap mapping relationship names to their attributes
     */
    public void setAttributesRel(HashMap<String, ArrayList<Attribute>> attributesRel) {
        this.attributesRel = attributesRel;
    }

    /**
     * Gets the serial version UID.
     * 
     * @return The serial version UID value
     */
    public static long getSerialversionuid() {
        return serialVersionUID;
    }

    /**
     * Gets the domain name.
     * 
     * @return The name of the domain
     */
    public String getDomainName() {
        return domainName;
    }
    
    /**
     * Sets the domain name.
     * 
     * @param domainName The name to set for the domain
     */
    public void setDomainName(String domainName) {
        this.domainName = domainName;
    }

    /**
     * Recursively traverses a tree node and collects class names.
     * 
     * @param node The tree node to traverse
     * @return An ArrayList of class names found in the tree
     */
    public ArrayList<String> recursiveTree(TreeNode node) {
        ArrayList<String> classi = new ArrayList<String>();
        List<TreeNode> children = node.getChildren();
        for (int j = 0; j < node.getChildCount(); j++) {
            classi.add(children.get(j).toString());
            recursiveTree(children.get(j));
        }
        return classi;
    }

    /**
     * Recursively builds a taxonomy representation in Prolog format.
     * Results are accumulated in the 'recur' instance variable.
     * 
     * @param s The predicate name to use in the Prolog facts
     * @param node The current node in the tree
     * @param superV The parent/super class name
     */
    public void recursiveTreeTax(String s, TreeNode node, String superV) {
        List<TreeNode> children = node.getChildren();
        for (int j = 0; j < node.getChildCount(); j++) {
            recur += s + superV + ", " + children.get(j).toString() + ").\n";
            recursiveTreeTax(s, children.get(j), children.get(j).toString());
        }
    }

    /**
     * Gets the accumulated recursive representation.
     * 
     * @return The string containing the accumulated tree representation
     */
    public String getRecur() {
        return recur;
    }
    
    /**
     * Sets the accumulated recursive representation.
     * 
     * @param recur The string to set as the recursive representation
     */
    public void setRecur(String recur) {
        this.recur = recur;
    }

    /**
     * Converts an ArrayList of strings into a Prolog list representation.
     * 
     * @param lista The ArrayList of strings to convert
     * @return A string representing the ArrayList in Prolog list syntax
     */
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
