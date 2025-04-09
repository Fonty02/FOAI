package domain;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.Stack;
import java.util.TreeSet;
import java.util.Vector;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.primefaces.model.DefaultTreeNode;
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/**
 * This class represents the domain data for a specific domain.
 * It contains methods for loading and parsing .gbs files, as well as storing and manipulating domain information.
 * The domain data includes entities, relationships, attributes, union_entities axioms, etc.
 */
public class DomainData {
	//private String author;
	//private int version;
	private Vector<Attribute> types = new Vector<>();
	private ArrayList<String> importedFiles = new ArrayList<>();
	private ArrayList<String> removedEntities = new ArrayList<>();
	private ArrayList<String> removedRelationships = new ArrayList<>();
	private String domain = null;
	private Entity entityTree;
	private HashSet<Union> unions = new HashSet<>();
	private HashSet<Axiom> axioms = new HashSet<>();
	private Relationship relationshipTree;
	private Vector<String> subjects = new Vector<String>();
//	private Map<String,Relationship> relationshipsNew = new HashMap<String,Relationship>();
	private Vector<String> objects = new Vector<String>();
	public Set<String> subjRelObjs = new TreeSet<String>(); // insieme di stringhe [soggetto.relazione.oggetto|...] // METODO getSubjRelObjs
	private Map<String,Vector<String>> subjRels = new HashMap<String,Vector<String>>(); // relazioni per un soggetto dato // METODO getSubjRels
	private Map<String,Vector<String>> subjObjs = new HashMap<String,Vector<String>>(); // oggetti per un soggetto dato // METODO getSubjObjs
	private Map<String,Vector<String>> relSubjs = new HashMap<String,Vector<String>>(); // soggetti per una relazione data // METODO getRelSubjs
	private Map<String,Vector<String>> relObjs = new HashMap<String,Vector<String>>(); // oggetti per una relazione data // METODO getRelObjs
	private Map<String,Vector<String>> objSubjs = new HashMap<String,Vector<String>>(); // soggetti per un oggetto dato // METODO getObjSubjs
	private Map<String,Vector<String>> objRels = new HashMap<String,Vector<String>>(); // relazioni per un oggetto dato // METODO getObjRels
	private Map<String,Vector<String>> subjRel_Objs = new HashMap<String,Vector<String>>(); // oggetti per una data coppia soggetto-relazione // METODO getSubjRel_Objs
	private Map<String,Vector<String>> subjObj_Rels = new HashMap<String,Vector<String>>(); // relazioni per una data coppia soggetto-oggetto // METODO getSubjObj_Rels
	private Map<String,Vector<String>> relObj_Subjs = new HashMap<String,Vector<String>>(); // soggetti per una data coppia relazione-oggetto //  METODO getRelObj_Subjs

	public Map<String,String> inverseRels = new HashMap<String,String>(); // relazioni inverse // METODO getInverse() di Relationship.java
	
	private int nRelRefs;
//	private String webInfFolder = "/home/progettoai/eclipse-workspace/.metadata/.plugins/org.eclipse.wst.server.core/tmp0/wtpwebapps/GraphBRAIN-detached/WEB-INF";
//	private String webInfFolder = "/var/lib/tomcat8/webapps/GraphBRAIN-detached/WEB-INF/";
//	private String webInfFolder = "/home/progettoai/eclipse-workspace/GraphBRAIN/GraphBRAINfiles/GraphBRAINtmp";
	private String webInfFolder = "";

	public DomainData() {
		entityTree = new Entity("Entity",null);
//		entityTree.addAttributes(new Vector<Attribute>(List.of(new Attribute("name","string","true"),new Attribute("description","string","false"),new Attribute("notes","string","false"))));
		List<Attribute> attributes = new ArrayList<>(Arrays.asList(
                new Attribute("name", "string", "true"),
                new Attribute("description", "string", "false"),
                new Attribute("notes", "string", "false")
        ));
		Vector<Attribute> attributeVector = new Vector<>(attributes);
		entityTree.addAttributes(attributeVector);

		//unions.add(new Union("Prova","test",new HashSet<String>(new ArrayList<String>(List.of("a","b","c")))));
		entityTree.setChildren(new ArrayList<>());
		relationshipTree = new Relationship(null, "Relationship", "Relationship");
		relationshipTree.setChildren(new ArrayList<>());
		subjects = new Vector<String>();
		objects = new Vector<String>();
		subjRels = new HashMap<String,Vector<String>>();
		subjObjs = new HashMap<String,Vector<String>>();
		relSubjs = new HashMap<String,Vector<String>>();
		relObjs = new HashMap<String,Vector<String>>();
		objSubjs = new HashMap<String,Vector<String>>();
		objRels = new HashMap<String,Vector<String>>();

		subjRel_Objs = new HashMap<String,Vector<String>>();
		subjObj_Rels = new HashMap<String,Vector<String>>();
		relObj_Subjs = new HashMap<String,Vector<String>>();

		subjRelObjs = new TreeSet<String>(); // insieme di stringhe soggetto.relazione.oggetto
		nRelRefs = 0;
	}
	
	/**
	 * Constructs a new instance of the DomainData class with the specified path.
	 * 
	 * @param path the path to the domain data file, which must either be a .gbs file or if path has no .gbs extension, the file is assumed to be in the WEB-INF folder, with the .gbs extension added automatically
	 * @throws ParserConfigurationException if a DocumentBuilder cannot be created
	 * @throws SAXException if any parse errors occur
	 * @throws IOException if an I/O error occurs
	 * @throws Exception if any other exception occurs
	 */
	public DomainData(String path) throws ParserConfigurationException, SAXException, IOException, Exception {
		this();

		if (path.endsWith(".gbs")) {
			loadFile(parseFile(new File(path)), path);
		} else {
			File webInf = new File(webInfFolder);
			loadFile(parseFile(new File(webInf, path + ".gbs")), path);
		}
	}
	
	public DomainData(byte[] byteArray, String webInfFolder) throws ParserConfigurationException, SAXException, IOException, Exception {
		this();
		this.webInfFolder = webInfFolder;
		InputStream is = new ByteArrayInputStream(byteArray);
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder db = factory.newDocumentBuilder();
		Document doc = db.parse(is);
		domain = doc.getDocumentElement().getAttributes().getNamedItem("name").getNodeValue();
		loadFile(doc, domain);
	}

	// permetti di fare il parsing di un file arbitrario
	public DomainData(String domainName, File file) throws ParserConfigurationException, SAXException, IOException, Exception {
		this();
		/// DA RIMUOVERE
		domain = domainName;
		loadFile(parseFile(file), file.getAbsolutePath());
	}
	//Davide: forse da rimuovere
	/*
	public void loadFile(File file, String domainPath) throws ParserConfigurationException, SAXException, IOException, Exception { //ste era private
		DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		DocumentBuilder db = dbf.newDocumentBuilder();
		Document doc = db.parse(file);
		loadFile(doc, domainPath);
	}
	*/
	/**
	 * Parses the given file and returns a Document object representing the parsed XML.
	 *
	 * @param file the file to be parsed
	 * @return a Document object representing the parsed XML
	 */
	// Parses the given file into a Document object and handles any parsing exceptions.
	private Document parseFile(File file) {
		Document doc = null;
		try {
			doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(file);
		} catch (ParserConfigurationException|SAXException|IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return doc;
	}
	
	// folderPath[0] -> domain
	// folderPath[1] -> path
	/**
	 * Retrieves the folder path for the given domain path.
	 * 
	 * @param domainPath the domain path
	 * @return a vector containing as first element the base filename without the extension and as second element the folder path
	 */
	// Retrieves the folder path for the given domain path and returns it as a Vector containing the base filename and folder path.
	private Vector<String> getFolderPath(String domainPath) {
		System.out.println(domainPath);
		Vector<String> folderPath = new Vector<>(2);
		folderPath.add(0, domainPath);
		if(domainPath.contains("/")) {
			 folderPath.add(1, domainPath.substring(0, domainPath.lastIndexOf("/") + 1));
			 folderPath.set(0, domainPath.substring(domainPath.lastIndexOf("/")+1).replace(".gbs", ""));
		} else {
			folderPath.add(1, webInfFolder);
		}
		return folderPath;
	}

	/**
	 * Validates a tag against a list of valid tags.
	 * Throws an IllegalArgumentException if the tag is not found in the list of valid tags.
	 * Otherwise, does nothing.
	 * 
	 * @param tag The tag to be validated.
	 * @param validTags The list of valid tags.
	 * @throws IllegalArgumentException If the tag is not found in the list of valid tags.
	 */
	// Validates if the provided tag is found in the list of valid tags, throwing an IllegalArgumentException if not.
	private void validateTag(Node tag,List<String> validTags) 
	{if(!validTags.contains(tag.getNodeName()))	
		{
		 throw new IllegalArgumentException("Invalid tag <"+tag.getNodeName()+"> found under <"+tag.getParentNode().getNodeName()+" "+(tag.getParentNode().getAttributes().getNamedItem("name")==null?"":tag.getParentNode().getAttributes().getNamedItem("name"))+"> where one of "+validTags+" was expected");
		}
    }
	/**
	 * Validates the attributes of a given XML tag against a list of valid attributes.
	 * Throws an IllegalArgumentException if any invalid attribute is found.
	 * Otherwise, does nothing.
	 *
	 * @param tag The XML tag to validate.
	 * @param validTagAttributes The list of valid attributes for the tag.
	 * @param identifier The identifier used to identify the tag. (e.g. "name" for entities, used to provide a more informative error message)
	 * @throws IllegalArgumentException If an invalid attribute is found.
	 */
	// Validates the attributes of a given XML tag against a list of valid attributes, throwing an IllegalArgumentException if any invalid attribute is found.
	private void validateTagAttributes(Node tag,List<String> validTagAttributes, String identifier) 
	{
		IntStream.range(0,tag.getAttributes().getLength())
			.mapToObj(tag.getAttributes()::item)
			.map(e->e.getNodeName())
			.forEach(e->{
				if(!validTagAttributes.contains(e))	
				{
				 throw new IllegalArgumentException("Invalid attribute \""+e+"\" found in <"+tag.getNodeName()+" "+(tag.getAttributes().getNamedItem(identifier)==null?"":tag.getAttributes().getNamedItem(identifier))+"> where one of "+validTagAttributes+" was expected");
				}
			
			});
    }
	
	/**
	 * Loads a file and parses its contents to populate the domain data.
	 * 
	 * @param doc The document object representing the file to be loaded.
	 * @param domainPath The path of the .gbs file.
	 * @throws ParserConfigurationException If a parser cannot be created.
	 * @throws SAXException If any parse errors occur.
	 * @throws IOException If any I/O errors occur.
	 * @throws Exception If any other errors occur during the loading process.
	 * @throws IllegalArgumentException If the domain tag is missing or if there is more than one domain tag in the file.
	 */
	// Loads and parses a file to populate the domain data, handling various XML sections such as entities, relationships, and axioms.
	private void loadFile(Document doc, String domainPath) throws ParserConfigurationException, SAXException, IOException, Exception { //ste era private
		Vector<String> folderPath = new Vector<>(2);
		folderPath = getFolderPath(domainPath);
		File webInf = new File(folderPath.get(1));
		System.out.println(doc.getDocumentURI());
//		domain = folderPath.get(0);
//		System.out.println(domain);
		//Davide: forse da rimuovere
		/*
		try {
			author = doc.getDocumentElement().getAttributes().getNamedItem("author").getNodeValue();
		} catch (Exception e) {
			author = "";
		}
		try {
			version = Integer.parseInt(doc.getDocumentElement().getAttributes().getNamedItem("version").getNodeValue());
		} catch (Exception e) {
			version = 0;
		}
		*/
		int section = 0; //[imports], [user-types], entities, [union_entities], relationships, [axioms] (se in [] la sezione è opzionale)
		NodeList nodelist = doc.getChildNodes();
//		List<Node> nodes = IntStream.range(0, nodelist.getLength())
//		.mapToObj(nodelist::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.peek(tag->validateTag(tag,List.of("domain")))	
//		.collect(Collectors.toList());
		
		List<Node> nodes = IntStream.range(0, nodelist.getLength())
		        .mapToObj(nodelist::item)
		        .filter(node -> node.getNodeType() == Node.ELEMENT_NODE)
		        .peek(tag -> validateTag(tag, Arrays.asList("domain")))  // Use Arrays.asList() instead of List.of()
		        .collect(Collectors.toList());
		if(nodes.size()!=1) {
			throw new Exception("There must be exactly one domain tag in \""+doc.getDocumentURI()+"\" file");
		}
		String domain = nodes.get(0).getAttributes().getNamedItem("name").getNodeValue();
		if(this.domain==null) {
			this.domain = domain;
		}
		nodelist = nodes.get(0).getChildNodes();
//		nodes = IntStream.range(0, nodelist.getLength())
//		.mapToObj(nodelist::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.peek(tag->validateTag(tag,List.of("imports", "user-types", "entities","union_entities","relationships","axioms")))
//		.collect(Collectors.toList());
		
		nodes = IntStream.range(0, nodelist.getLength())
		        .mapToObj(nodelist::item)
		        .filter(node -> node.getNodeType() == Node.ELEMENT_NODE)
		        .peek(tag -> validateTag(tag, Arrays.asList("imports", "user-types", "entities", "union_entities", "relationships", "axioms")))
		        .collect(Collectors.toList());

		if(nodes.get(section).getNodeName().equals("imports")) {
			parseImports(webInf, nodes.get(section++));
		}
		if(nodes.get(section).getNodeName().equals("user-types")) {
			parseTypes(webInf, nodes.get(section++));
		}

		if (!nodes.get(section).getNodeName().equals("entities")) {
			throw new Exception("Missing entities section in domain \""+domain+"\" file");
		}
		parseEntities(nodes.get(section++),entityTree,domain);

		if(nodes.get(section).getNodeName().equals("union_entities")) {
			parseUnionEntities(nodes.get(section++),domain);
		}

		if (!nodes.get(section).getNodeName().equals("relationships")) {
			throw new Exception("Missing relationships section in domain \""+domain+"\" file");
		}
		
		parseRelationships(nodes.get(section++),relationshipTree,domain);

		if(section<nodes.size() && nodes.get(section).getNodeName().equals("axioms")) {
			parseAxioms(nodes.get(section++),domain);
		}
		Collections.sort(subjects);
		Collections.sort(objects);
	}
	
	/**
	 * Parses the axioms from the given XML node and adds them to the {@code Hashset<Axiom>} of axioms.
	 * 
	 * @param axioms_tag the XML node containing the axioms (to be called on the {@code <axioms>} tag).
	 * @param domainName The domain to be assigned.
	 * @throws IllegalArgumentException if the {@code <axioms>} tag contains an invalid child tag (allowed: {@code <axiom>}).
	 * @throws IllegalArgumentException if an {@code <axiom>} contains an invalid attribute (allowed: name, formalism).
	 * @throws IllegalArgumentException if an axiom with the same name already exists in the domain.
	 * 
	 */
	// Parses the axioms from the given XML node and adds them to the set of axioms for the specified domain.
	private void parseAxioms(Node axioms_tag, String domainName) {
		NodeList axiomNodes = axioms_tag.getChildNodes();
//		IntStream.range(0, axiomNodes.getLength())
//		.mapToObj(axiomNodes::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.peek(node-> validateTag(node, List.of("axiom")))
//		.peek(axiom->validateTagAttributes(axiom, List.of("name","formalism"), "name"))
//		.forEach(axiom->{
//			String name = axiom.getAttributes().getNamedItem("name").getNodeValue();
//			String formalism = axiom.getAttributes().getNamedItem("formalism").getNodeValue();
//			String expression = axiom.getTextContent();
//			System.out.println(name+" "+formalism+" "+expression);
//			if(!axioms.add(new Axiom(name, formalism, expression, domainName))) {
//				throw new IllegalArgumentException("Duplicate Axiom: \"" + name + "\" in domain \""+domainName+"\"");
//			}
//		});
		
		IntStream.range(0, axiomNodes.getLength())
	    .mapToObj(axiomNodes::item)
	    .filter(node -> node.getNodeType() == Node.ELEMENT_NODE)
	    .peek(node -> validateTag(node, Arrays.asList("axiom")))
	    .peek(axiom -> validateTagAttributes(axiom, Arrays.asList("name", "formalism", "rule"), "name"))
	    .forEach(axiom -> {
	        String name = axiom.getAttributes().getNamedItem("name").getNodeValue();
	        String formalism = axiom.getAttributes().getNamedItem("formalism").getNodeValue();
	        String expression = axiom.getAttributes().getNamedItem("rule").getNodeValue();
	        // ? String expression = axiom.getTextContent(); 
	        System.out.println(name + " " + formalism + " " + expression);
	        if (!axioms.add(new Axiom(name, formalism, expression, domainName))) {
	            throw new IllegalArgumentException("Duplicate Axiom: \"" + name + "\" in domain \"" + domainName + "\"");
	        }
	    });
	}
	
	class Pair<K, V> {
	    private final K key;
	    private final V value;

	    public Pair(K key, V value) {
	        this.key = key;
	        this.value = value;
	    }

	    public K getKey() {
	        return key;
	    }

	    public V getValue() {
	        return value;
	    }
	}

	/**
	 * Parses the union entities from the given XML node and adds them to the domain data.
	 * adds the parsed list of Union objects to the {@code HashSet<Union>} of the domain.
	 * @param union_entities The XML node {@code <union_entities>} containing the union entities.
	 * @param domainName The domain to be assigned.
	 * @throws IllegalArgumentException if {@code <union_entities>} tag contains an invalid child tag (allowed: {@code <union>}).
	 * @throws IllegalArgumentException if an {@code <entity>} with the same name as one parsed {@code <union>} already exists.
	 * @throws IllegalArgumentException if an {@code <union>} contains an invalid attribute (allowed: name).
	 * @throws IllegalArgumentException if an {@code <union>} tag contains an invalid child tag (allowed: {@code <uvalue>}).
	 */
	// Parses the union entities from the given XML node and adds them to the domain's set of Union entities.
	private void parseUnionEntities(Node union_entities, String domainName) {
		NodeList unionNodes = union_entities.getChildNodes();
//		addUnions( IntStream.range(0, unionNodes.getLength())
//							.mapToObj(unionNodes::item)
//							.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//							.peek(node-> validateTag(node, List.of("union")))
//							.peek(node-> validateTagAttributes(node, List.of("name"), "name"))
//							.map(item-> Map.entry(item.getAttributes().getNamedItem("name").getNodeValue(),item))
//							.peek(pair -> {
//								if (findInTree(entityTree, pair.getKey()) != null) {
//									throw new IllegalArgumentException("Entity \"" + pair.getKey() + "\" already exists, can't create union entity with the same name");
//								}
//							})
//							.map(pair ->new Union(pair.getKey(), domainName, new HashSet<>(readValuesList(pair.getValue(), "uvalue", false))))
//							.collect(Collectors.toList())
//		);
		
		addUnions(
			    IntStream.range(0, unionNodes.getLength())
			        .mapToObj(unionNodes::item)
			        .filter(node -> node.getNodeType() == Node.ELEMENT_NODE)
			        .peek(node -> validateTag(node, Arrays.asList("union")))
			        .peek(node -> validateTagAttributes(node, Arrays.asList("name"), "name"))
			        .map(item -> new Pair<>(item.getAttributes().getNamedItem("name").getNodeValue(), item))
			        .peek(pair -> {
			            if (findInTree(entityTree, pair.getKey()) != null) {
			                throw new IllegalArgumentException("Entity \"" + pair.getKey() + "\" already exists, can't create union entity with the same name");
			            }
			        })
			        .map(pair -> new Union(pair.getKey(), domainName, new HashSet<>(readValuesList(pair.getValue(), "uvalue", false))))
			        .collect(Collectors.toList())
			);

	}

	/**
	 * Adds a list of Union objects to the domain.<br>
	 * adds the given list of Union objects to the {@code HashSet<Union>} of the domain. 
	 * @param _unions the list of Union objects to be added
	 * @throws IllegalArgumentException if any of the Union objects contain values that do not exist in the entityTree,
	 * or if a duplicate Union is found in the domain with a different domain name
	 */
	// Adds a list of Union objects to the domain, checking for duplicates and ensuring all values are valid entities.
	private void addUnions(List<Union> _unions) {
		//check that all uvalues are existing entities
		_unions.stream().forEach(e->{ 
			e.getValues().stream().forEach(t->{
				if (findInTree(entityTree, t) == null) {
					throw new IllegalArgumentException("Entity \"" + t + "\" required by union \""+e.getName()+"\" does not exist");
				}
			});
		});
		for (Union new_union : _unions) 
		{
			Optional<Union> match = unions.stream().filter(u->u.equals(new_union)).findFirst();
			if (match.isPresent()) {
				Union old_union = match.get();
				if(new_union.getDomain().equals(old_union.getDomain())) {
					throw new IllegalArgumentException("Duplicate Union: \"" + new_union.getName()+"\" in domain \""+new_union.getDomain()+"\"");
				} else {
					old_union.setDomain(new_union.getDomain());
					old_union.getValues().addAll(new_union.getValues());					
				}
			}
			else
			{
				unions.add(new_union);
			}
		}
	}
	
	// Adds an entity to the domain, replacing any existing entity with the same name.
	public void addEntity(Entity entity) { //ste solo top entities; la sostituisce se esiste? Non va bene
		Entity found = null;
		for(Entity e : getTopEntities()) {
			if(e.getName().equals(entity.getName())) {
				found = e;
			}
		}
		if(found != null) {
			getTopEntities().remove(found);
		}
		entityTree.addChild(entity);
		entity.setParent(entityTree);
	}
	
	// Adds a relationship to the domain, replacing any existing relationship with the same name.
	public void addRelationship(Relationship relationship) {
		Relationship found = null;
		for(Entity er : getTopRelationships()) {
			Relationship r = (Relationship) er;
			if(r.getName().equals(relationship.getName())) {
				found = r;
			}
		}
		if(found != null) {
			getTopEntities().remove(found);
		}
		relationshipTree.addChild(relationship);
		relationship.setParent(relationshipTree);	
	}

	/**
	 * It constructs the relationships tree by recursively parsing the relationships and their attributes,references and subrelationships.
	 * 
	 * @param parentNode The XML parent node containing the relationship nodes. should be called on the {@code <relationships>} tag and recursively on the {@code <relationship>} tags.
	 * @param root The root entity of the relationship tree examined (the Relationship equivalent to the parentNode).
	 * @param domainName The name of the domain to be assigned.
	 * @throws Exception if there is an error during parsing.
	 * @throws IllegalArgumentException if the {@code <relationship>} tag contains an invalid attribute (allowed: name, inverse, description, abstract).
	 * @throws IllegalArgumentException if the root {@code <relationships>} tag contains an invalid child tag (allowed: {@code <relationship>}).
	 * 
	 */
	// Recursively constructs the relationships tree by parsing relationships and their attributes, references, and sub-relationships.
	private void parseRelationships(org.w3c.dom.Node parentNode, Relationship root, String domainName) throws Exception{
		NodeList rNodeList = parentNode.getChildNodes();
//		List<Node> node_relationships = IntStream.range(0, rNodeList.getLength())
//		.mapToObj(rNodeList::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.peek(node-> validateTag(node, root==relationshipTree?List.of("relationship"):List.of("relationship","attribute","reference")))
//		.filter(node-> node.getNodeName().equals("relationship"))
//		.peek(node-> validateTagAttributes(node, List.of("name","inverse","description","abstract"), "name"))
//		.collect(Collectors.toList());
		
		List<Node> node_relationships = IntStream.range(0, rNodeList.getLength())
		        .mapToObj(rNodeList::item)
		        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
		        .peek(node -> validateTag(node, root == relationshipTree ? Arrays.asList("relationship") : Arrays.asList("relationship", "attribute", "reference")))
		        .filter(node -> node.getNodeName().equals("relationship"))
		        .peek(node -> validateTagAttributes(node, Arrays.asList("name", "inverse", "description", "abstract"), "name"))
		        .collect(Collectors.toList());
		for(Node en : node_relationships) 
		{
				String relationName = en.getAttributes().getNamedItem("name").getNodeValue();
				String relationInverse = en.getAttributes().getNamedItem("inverse").getNodeValue();
				String description = en.getAttributes().getNamedItem("description") != null ?
						en.getAttributes().getNamedItem("description").getNodeValue() : null;
				String notes = en.getAttributes().getNamedItem("notes") != null ?
						en.getAttributes().getNamedItem("notes").getNodeValue() : null;
				Node str_abstract= en.getAttributes().getNamedItem("abstract");
				boolean _abstract = str_abstract != null && str_abstract.getNodeValue().equals("true");
				Relationship currentRelationship = (Relationship) findInTree(relationshipTree, relationName);
				if(currentRelationship == null) 
				{ // se non esiste già
					currentRelationship = (Relationship)findInTree(relationshipTree, relationName);
					//ste da qui...
					if(currentRelationship != null) 
					{ // se sta da un'altra parte
						if((root.hasAncestor(currentRelationship.getParent().getName())|| currentRelationship.getParent()==relationshipTree) && !currentRelationship.getDomain().equals(domainName)) {
							currentRelationship.detach();
						} else {
								// INCONSISTENZA
								System.out.println("INCONSISTENZA");
								throw new Exception("Inconsistency due to " + relationName);
								}
					} else {
						currentRelationship = new Relationship(domainName, relationName, relationInverse);
					}
					root.addChild(currentRelationship);
//					currentRelationship.getAttributes().addAll(root.getAttributes());
				}
				currentRelationship.setDomain(domainName); //ste andrebbe aggiunto, per cui in Entity deve diventare una lista di domini
				currentRelationship.setDescription(description);
				currentRelationship.setAbstract(_abstract);
				currentRelationship.setNotes(notes);
				currentRelationship.addAttributes(readAttributes(en));
				parseReferences(en, currentRelationship);
				parseRelationships(en, currentRelationship, domainName);
			}
	}
	
	/* Davide: forse da rimuovere
	private void parseRelationships(NodeList relationNodes) {
		for(int rni = 1; rni < relationNodes.getLength(); rni+=2) { // per ogni relazione
			org.w3c.dom.Node rn = relationNodes.item(rni);
			if(rn.getNodeType() == Node.ELEMENT_NODE) {
				String relationName = rn.getAttributes().getNamedItem("name").getNodeValue();
				String relationInverse = rn.getAttributes().getNamedItem("inverse").getNodeValue();
				String relationParent = "";
				Integer nAttributes = rn.getAttributes().getLength();
				if(nAttributes == 3) {
					relationParent = rn.getAttributes().getNamedItem("childOf").getNodeValue();
				}
				Relationship relation = null;
				for(Relationship r : relationships) {
					if(r.getName().equals(relationName)) { //ste integrare invece che sostituire
						relation = r;
						relation.setDomain(domain); //ste andrebbe aggiunto, per cui in Entity deve diventare una lista di domini
						break; // trovata, esce dal ciclo anticipatamente
					}
				}
				if(relation == null) { // relazione non era gia' presente
					relation = new Relationship(domain, relationName, relationInverse, relationParent);
					relationships.add(relation); //ste in futuro sara' una tassonomia
					if(!relationParent.equals("")) {
						getRelationship(relationParent).addChildrenRelationship(relationName);
						relation.addReferences(getRelationship(relationParent).getReferences());
					}
				}
				inverseRels.put(relationName, relationInverse);
				inverseRels.put(relationInverse, relationName);
				Vector<Attribute> fullAttrs = new Vector<Attribute>();
				NodeList relationFeatureNodes = rn.getChildNodes(); // i figli sono le feature
				for(int rfni = 1; rfni < relationFeatureNodes.getLength(); rfni+=2) { // per ogni feature
					org.w3c.dom.Node rfn = relationFeatureNodes.item(rfni);
					if(rfn.getNodeType() == Node.ELEMENT_NODE) {
						if(rfn.getNodeName().equals("references")) { // se rappresenta i riferimenti (soggetti-oggetti)
							NodeList referenceNodes = rfn.getChildNodes(); // i figli sono i riferimenti
							parseReferences(referenceNodes, relation, relationName);
						} else if(rfn.getNodeName().equals("attributes")) { // se rappresenta gli attributi
							//readAttributes(rfn, fullAttrs);
							NodeList attributeNodes = rfn.getChildNodes(); // i figli sono i riferimenti
							parseAttributes(attributeNodes, relation);
							relation.addAttributes(fullAttrs);
						}
					}
				}
			}
		}
		
	}
	*/
	
	/* Davide: forse da rimuovere
	private void parseAttributes(NodeList attributeNodes, Relationship relation) {
		for(int rrn = 1; rrn < attributeNodes.getLength(); rrn+=2) { // per ogni riferimento
			if(attributeNodes.item(rrn).getNodeType() == Node.ELEMENT_NODE) {
				String name = attributeNodes.item(rrn).getAttributes().getNamedItem("name").getNodeValue();
				String mandatory = attributeNodes.item(rrn).getAttributes().getNamedItem("mandatory").getNodeValue();
				String datatype = attributeNodes.item(rrn).getAttributes().getNamedItem("datatype").getNodeValue();
				String description = attributeNodes.item(rrn).getAttributes().getNamedItem("description") != null ?
						attributeNodes.item(rrn).getAttributes().getNamedItem("description").getNodeValue() : "";
				Attribute attr = new Attribute(name, datatype, mandatory);
				attr.setDescription(description);
				if(attr.getName().equals("reason")) {
					System.out.println("ok");
					System.out.println(attr.getDescription());
				}
				if(!description.equals("")) {
					System.out.println(description);
				}
				//TODO tartarello fix null target for attributes in relationship with datatype="entity"
				//TODO tartarello fix missing values for attributes in relationship with datatype="select" and datatype="tree"
				org.w3c.dom.Node an = attributeNodes.item(rrn);
				
				if(datatype.equals("select") || datatype.equals("tree")) { // valori specificati
					org.w3c.dom.Node valuesNode = an.getChildNodes().item(1); // <values>
					if(datatype.equals("select")) {
						attr.setValuesString(readValuesList(valuesNode));
					} else if(datatype.equals("tree")) {
						attr.setSubClasses(readValuesTree(valuesNode,"- Select one -"));
					}
				} else if(datatype.equals("entity")) {
					attr.setTarget(an.getAttributes().getNamedItem("target").getNodeValue());
				}
				
				relation.addAttribute(attr);
			}	
		}
	}
	*/

	/**
	 * Parses the references from the given parent node and adds them to the specified relationship.
	 * 
	 * @param parentNode The parent node containing the references (to be called on {@code <relationship>} tag).
	 * @param relation The relationship to which the references will be added.
	 * @throws Exception If an error occurs during parsing.
	 * @throws IllegalArgumentException If the {@code <reference>} tag contains an invalid attribute (allowed: subject, object).
	 * @throws IllegalArgumentException If the parent node contains an invalid child tag (allowed: {@code <reference>}).
	 */
	private void parseReferences(org.w3c.dom.Node parentNode, Relationship relation) throws Exception{
		String relationName=relation.getName();
		NodeList referenceNodes = parentNode.getChildNodes(); // i figli sono i riferimenti parentNode= <relationship>
//		List<Node> nodes = IntStream.range(0, referenceNodes.getLength())
//		.mapToObj(referenceNodes::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.filter(node-> node.getNodeName().equals("reference"))
//		.peek(node-> validateTagAttributes(node, List.of("subject","object"), ""))
//		.collect(Collectors.toList());
		
		List<Node> nodes = IntStream.range(0, referenceNodes.getLength())
		        .mapToObj(referenceNodes::item)
		        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
		        .filter(node -> node.getNodeName().equals("reference"))
		        .peek(node -> validateTagAttributes(node, Arrays.asList("subject", "object"), ""))
		        .collect(Collectors.toList());
		for(Node node: nodes) { // per ogni riferimento
				String subject = node.getAttributes().getNamedItem("subject").getNodeValue();
				if(!subjects.contains(subject))
					subjects.add(subject);
				String object = node.getAttributes().getNamedItem("object").getNodeValue();
				if(!objects.contains(object))
					objects.add(object);
				Reference ref = new Reference(subject, object); //ste aggiungere attributi specifici qui
				ref.setAttributes(readAttributes(node));
				relation.addReference(ref);
				nRelRefs++;
				subjRelObjs.add(subject + "." + relationName + "." + object);
				addValue(subjRels,subject,relationName); // o relation.getName()
				addValue(subjObjs,subject,object);
				addValue(relSubjs,relationName,subject); // o relation.getName()
				addValue(relObjs,relationName,object); // o relation.getName()
				addValue(objRels,object,relationName); // o relation.getName()
				addValue(objSubjs,object,subject);
				addValue(subjRel_Objs,subject + "." + relationName,object); // o relation.getName()
				addValue(subjObj_Rels,subject + "." + object,relationName); // o relation.getName()
				addValue(relObj_Subjs,relationName + "." + object,subject); // o relation.getName()
		}
	}

	
	/**
	 * Parses the entities from the given parent node and adds them to the entity tree.<br>
	 * It constructs the entity tree by recursively parsing the entities and their attributes and subentities.
	 * 
	 * @param parentNode The XML parent node containing the entity nodes. should be called on the entities tag and recursively on the entity tags.
	 * @param root The root entity of the entity tree examined (the Entity equivalent to the parentNode).
	 * @param domainName The name of the domain to be assigned.
	 * @throws Exception if there is an error during parsing.
	 * @throws IllegalArgumentException if the entity tag contains an invalid attribute (allowed: name, description, abstract, notes).
	 * @throws IllegalArgumentException if the entity tag contains an invalid child tag (allowed: attribute, entity).
	 * @throws IllegalArgumentException if the entities tag contains an invalid child tag (allowed: entity).
	 * 
	 */
	// Parses entities from the given parent node and processes them based on the root entity.
	// Parameters:
	// parentNode: The parent node containing the entity data to parse.
	// root: The root entity where child entities will be added.
	// domainName: The domain name used for the entities.
	private void parseEntities(org.w3c.dom.Node parentNode, Entity root, String domainName) throws Exception {
		NodeList entityNodes = parentNode.getChildNodes();
//		List<Node> nodes = IntStream.range(0, entityNodes.getLength())
//		.mapToObj(entityNodes::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.peek(node-> validateTag(node, root==entityTree?List.of("entity"):List.of("entity","attribute")))
//		.filter(node-> node.getNodeName().equals("entity"))
//		.peek(node-> validateTagAttributes(node, List.of("name","description","abstract","notes"), "name"))
//		.collect(Collectors.toList());
		
		List<Node> nodes = IntStream.range(0, entityNodes.getLength())
		        .mapToObj(entityNodes::item)
		        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
		        .peek(node -> validateTag(node, root == entityTree ? Arrays.asList("entity") : Arrays.asList("entity", "attribute")))
		        .filter(node -> node.getNodeName().equals("entity"))
		        .peek(node -> validateTagAttributes(node, Arrays.asList("name", "description", "abstract", "notes"), "name"))
		        .collect(Collectors.toList());
		for(Node en : nodes) {
				String entityName = en.getAttributes().getNamedItem("name").getNodeValue();
				String description = en.getAttributes().getNamedItem("description") != null ?
						en.getAttributes().getNamedItem("description").getNodeValue() : null;
				String notes = en.getAttributes().getNamedItem("notes") != null ?
						en.getAttributes().getNamedItem("notes").getNodeValue() : null;
				boolean _abstract = en.getAttributes().getNamedItem("abstract") != null && en.getAttributes().getNamedItem("abstract").getNodeValue().equals("true");

				Entity currentEntity = findInTree(root, entityName);
				if(currentEntity == null) { // se non esiste già
					currentEntity = findInTree(entityTree, entityName);
					//ste da qui...
					if(currentEntity != null) 
					{ // se sta da un'altra parte
						if((root.hasAncestor(currentEntity.getParent().getName()) || currentEntity.getParent()==entityTree)&& !currentEntity.getDomain().equals(domainName)) {
							currentEntity.detach();
						} else {
								// INCONSISTENZA
								System.out.println("INCONSISTENZA");
								throw new Exception("Inconsistency due to " + entityName);
								}
					} else {
						currentEntity = new Entity(entityName, domainName);
					}
					root.addChild(currentEntity);
//					currentEntity.getAttributes().addAll(root.getAttributes());
				}
				

				currentEntity.setDomain(domainName); //ste andrebbe aggiunto, per cui in Entity deve diventare una lista di domini
				currentEntity.setDescription(description);
				currentEntity.setAbstract(_abstract);
				currentEntity.setNotes(notes);
				/*
				for(Entity e : getTopEntities()) {
					if(e.getName().equalsIgnoreCase(entityName)) { //ste integrare invece che sostituire
						entity = e;
						break; // trovata, esce dal ciclo anticipatamente
					}
				}
				*/
				currentEntity.addAttributes(readAttributes(en)); //add attributes to CurrentEntity
				parseEntities(en, currentEntity, domainName); //add subentities to CurrentEntity
				//attrs.put(entityName, fullAttrs);
		}
	}

/**
 * Parses the imports from importsNode which is the {@code <imports>} tag.<br>
 * it populates the importedFiles list with the imported files.<br>
 * It then eventually remove the entities and relationships specified in the {@code <deleted>} tag.<br>
 * It loads the imported files and parses them in Depth First Search order.<br>
 * 
 * @param folder The folder where to get the files linked inside {@code <import>} tag if only the name of the domain is provided instead of the full path.
 * @param importsNode The importsNode containing the import references.
 * @throws ParserConfigurationException If a parser configuration error occurs.
 * @throws SAXException If a SAX error occurs.
 * @throws IOException If an I/O error occurs.
 * @throws Exception If an error occurs during parsing.
 * @throws IllegalArgumentException If the deleted tag is present and not the last child of the imports tag.
 * @throws IllegalArgumentException If the imports tag contains an invalid tag as child (allowed: {@code <import>},{@code <deleted>}).
 * @throws IllegalArgumentException If the import tag contains an invalid attribute (allowed: schema).
 * @throws IllegalArgumentException If the deleted tag contains an invalid tag as child (allowed: {@code <entity>},{@code <relationship>}).
 * @throws IllegalArgumentException If the deleted tag contains an invalid attribute (allowed: name).
 */
	// Parses the imports from the given node and processes them, including checking for deleted elements.
	// Parameters:
	// folder: The folder containing the files to import.
	// importsNode: The XML node representing the imports data to process.
	private void parseImports(File folder, Node importsNode) throws ParserConfigurationException, SAXException, IOException, Exception {
		
		NodeList imports = importsNode.getChildNodes(); // i figli sono i riferimenti parentNode= <relationship>
//		List<Node> nodes = IntStream.range(0, imports.getLength())
//			.mapToObj(imports::item)
//			.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//			.peek(node-> validateTag(node, List.of("import","deleted")))
//			.collect(Collectors.toList());
		
		List<Node> nodes = IntStream.range(0, imports.getLength())
		        .mapToObj(imports::item)
		        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
		        .peek(node -> validateTag(node, Arrays.asList("import", "deleted")))
		        .collect(Collectors.toList());
		
 		IntStream.range(0, nodes.size()-1).filter(i->nodes.get(i).getNodeName().equals("deleted")).findAny().ifPresent(e-> { throw new IllegalArgumentException("<deleted> can only be found as last child of <imports>");} );
		Node deletedNode = null;

		if (!nodes.isEmpty() && nodes.get(nodes.size() - 1).getNodeName().equals("deleted")) {
			deletedNode = nodes.get(nodes.size() - 1);
			nodes.remove(nodes.size() - 1);
		}
		
//		List<String> importPaths=nodes.stream()
//			 						  //.peek(node-> validateTag(node, List.of("import"))) implicit
//									  .peek(node-> validateTagAttributes(node, List.of("schema"), "schema"))
//			 						  .map(node-> node.getAttributes().getNamedItem("schema").getNodeValue())
//			 						  .collect(Collectors.toList());
		List<String> importPaths = nodes.stream()
		        //.peek(node -> validateTag(node, Arrays.asList("import"))) implicit
		        .peek(node -> validateTagAttributes(node, Arrays.asList("schema"), "schema"))
		        .map(node -> node.getAttributes().getNamedItem("schema").getNodeValue())
		        .collect(Collectors.toList());
		
		for(String imported : importPaths) 
		{
				importedFiles.add(imported);
				if(!imported.contains("/")) {
					loadFile(parseFile(new File(folder, imported + ".gbs")), folder.getAbsolutePath() + "/" + imported + ".gbs");
				} else {
					loadFile(parseFile(new File(imported)), imported);
				}
		}
		if(deletedNode!=null)
		{
			NodeList deleted = deletedNode.getChildNodes();
//			List<Node> nodesDeleted = IntStream.range(0, deleted.getLength())
//											   .mapToObj(deleted::item)
//											   .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//											   .peek(node-> validateTag(node, List.of("entity","relationship")))
//											   .collect(Collectors.toList());
			
			List<Node> nodesDeleted = IntStream.range(0, deleted.getLength())
			        .mapToObj(deleted::item)
			        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
			        .peek(node -> validateTag(node, Arrays.asList("entity", "relationship")))
			        .collect(Collectors.toList());
			for(Node del : nodesDeleted) 
			{
				String type = del.getNodeName();
				String name = del.getAttributes().getNamedItem("name").getNodeValue();
				if(type.equals("entity")) {
					removeEntity(name);
					removedEntities.add(name);
				} else {
					removeRelationship(name);
					removedRelationships.add(name);
				}
			}
		}
	}
	
	// Parses and processes the types from the given node, converting attributes into types.
	// Parameters:
	// webInf: The folder containing the web information.
	// typesNode: The XML node representing the types data to process.
	private void parseTypes(File webInf, org.w3c.dom.Node typesNode) {
		try {
			types = fromAttributesToTypes(readAttributes(typesNode));
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	// Converts a list of attributes into a list of types.
	// Parameters:
	// attributes: The list of attributes to be converted into types.
	private Vector<Attribute> fromAttributesToTypes(Vector<Attribute> attributes) {
		Vector<Attribute> types = new Vector<>();
		for(Attribute a : attributes) {
			/*Attribute type = new UType();
			type = (UType) a;*/
			types.add(a);
		}
		return types;
	}

	// Substitutes an entity in the specified file with a new entity.
	// Parameters:
	// fileToModify: The file where the entity needs to be substituted.
	// entityToRemove: The name of the entity to remove from the file.
	// entityToAdd: The new entity to add in place of the removed one.
	private void substitute(File fileToModify, String entityToRemove, org.w3c.dom.Node entityToAdd) {
		try {
			org.w3c.dom.Node parent = null;
			DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		    DocumentBuilder db = dbf.newDocumentBuilder();
			Document docToModify = db.parse(fileToModify);
			
			docToModify.getDocumentElement().normalize();
			
			NodeList entities = docToModify.getElementsByTagName("entity");
			for(int i=0; i<entities.getLength(); i++) {
				org.w3c.dom.Node entity = entities.item(i);
				parent = entity.getParentNode();
				if(entity.getAttributes().getNamedItem("name").getNodeValue().equalsIgnoreCase(entityToRemove)) {					
					entity.getParentNode().removeChild(entity);
				}
			}
			org.w3c.dom.Node newNode = clone(docToModify, entityToAdd);
			parent.appendChild(newNode);
			
			saveXML(docToModify, fileToModify);
			
		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (TransformerFactoryConfigurationError e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (TransformerException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
	}

	// Saves the modified XML document to the specified file.
	// Parameters:
	// docToModify: The XML document to save.
	// fileToModify: The file to save the document to.
	private void saveXML(Document docToModify, File fileToModify) throws TransformerException, IOException {
		TransformerFactory transformerFactory = TransformerFactory.newInstance();
		Transformer transformer = transformerFactory.newTransformer();
		DOMSource source = new DOMSource(docToModify);
        FileWriter writer = new FileWriter(fileToModify.getAbsolutePath());
        StreamResult result = new StreamResult(writer);
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.transform(source, result);
	}

	// Clones an entity and its attributes from the given node and returns the new entity node.
	// Parameters:
	// docToModify: The document where the new entity will be added.
	// entityToAdd: The entity node to clone.
	private Node clone(Document docToModify, Node entityToAdd) {
		Element newNode = docToModify.createElement("entity");
		Attr attr = docToModify.createAttribute("name");
		attr.setValue(entityToAdd.getAttributes().getNamedItem("name").getNodeValue()); 
		newNode.setAttributeNode(attr);
		NodeList children = entityToAdd.getChildNodes();
		if(children.getLength() > 3) {
			Element attributesToAdd = cloneAttributes(docToModify, children.item(1));
			Element valuesToAdd = cloneValues(docToModify, children.item(3));
			newNode.appendChild(attributesToAdd);
			newNode.appendChild(valuesToAdd);
		}else {
			if(children.getLength() > 0) {
				if(children.item(1).getNodeName().equalsIgnoreCase("attributes")) {
					Element newNodeAttributes = cloneAttributes(docToModify, children.item(1));
					newNode.appendChild(newNodeAttributes);
				}else {
					Element newNodeValues = cloneAttributes(docToModify, children.item(1));
					newNode.appendChild(newNodeValues);
				}
			}
		}
		return newNode;
	}

	// Clones the attributes from the given node and returns them as a new element.
	// Parameters:
	// docToModify: The document where the attributes will be cloned.
	// attributesToAdd: The node containing the attributes to clone.
	private Element cloneAttributes(Document docToModify, Node attributesToAdd) {
		Element attributes = docToModify.createElement("attributes");
		NodeList children = attributesToAdd.getChildNodes();
		for(int i=1; i<children.getLength(); i+=2) {
			Node attributeToAdd = children.item(i);
			Element attribute = docToModify.createElement("attribute");
			Attr attrName = docToModify.createAttribute("name");
			Attr attrMandatory = docToModify.createAttribute("mandatory");
			Attr attrDatatype = docToModify.createAttribute("datatype");
			attrName.setValue(attributeToAdd.getAttributes().getNamedItem("name").getNodeValue());
 			attrMandatory.setValue(attributeToAdd.getAttributes().getNamedItem("mandatory").getNodeValue());
			attrDatatype.setValue(attributeToAdd.getAttributes().getNamedItem("datatype").getNodeValue());
			attribute.setAttributeNode(attrName);
			attribute.setAttributeNode(attrMandatory);
			attribute.setAttributeNode(attrDatatype);
			if(attributeToAdd.getAttributes().getNamedItem("datatype").getNodeValue().equalsIgnoreCase("select")) {
				Element values = docToModify.createElement("values");
				for(int j=1; j<attributeToAdd.getChildNodes().item(1).getChildNodes().getLength(); j+=2) {
					Node valueToAdd = attributeToAdd.getChildNodes().item(1).getChildNodes().item(j);
					Element value = docToModify.createElement("value");
					Attr valueName = docToModify.createAttribute("name");
					valueName.setValue(valueToAdd.getAttributes().getNamedItem("name").getNodeValue());
					value.setAttributeNode(valueName);
					values.appendChild(value);
				}
				attribute.appendChild(values);
			}
			attributes.appendChild(attribute);
		}
		return attributes;
	}
	
	// Clones the values from the given node and returns them as a new element.
	// Parameters:
	// docToModify: The document where the values will be cloned.
	// valuesToAdd: The node containing the values to clone.
	private Element cloneValues(Document docToModify, Node valuesToAdd) {
		Element values = docToModify.createElement("taxonomy");
		NodeList children = valuesToAdd.getChildNodes();
		for(int i=1; i<children.getLength(); i+=2) {
			Node valueToAdd = children.item(i);
			Element value = docToModify.createElement("value");
			Attr attrName = docToModify.createAttribute("name");
			attrName.setValue(valueToAdd.getAttributes().getNamedItem("name").getNodeValue());
			value.setAttributeNode(attrName);
			if(valueToAdd.getChildNodes().getLength() > 3) {
				Element nestedAttributes = cloneAttributes(docToModify, valueToAdd.getChildNodes().item(1));
				Element nestedValues = cloneValues(docToModify, valueToAdd.getChildNodes().item(3));
				value.appendChild(nestedAttributes);
				value.appendChild(nestedValues);
			} else {
				if(valueToAdd.getChildNodes().getLength() > 0) {
					if(valueToAdd.getChildNodes().item(1).getNodeName().equalsIgnoreCase("attributes")) {
						Element nestedAttributes = cloneAttributes(docToModify, valueToAdd.getChildNodes().item(1));
						value.appendChild(nestedAttributes);
					}else {
						Element nestedValues = cloneValues(docToModify, valueToAdd.getChildNodes().item(1));
						value.appendChild(nestedValues);
					}
					
				}
			}
			values.appendChild(value);
		}
		return values;
	}

	// Retrieves the top entities from the entity tree.
	// Returns a list of the top-level entities in the entity tree.
	public List<Entity> getTopEntities() {
		return entityTree.getChildren();
	}
	
	/**
	 * Returns a list of top relationships, children of the root relationship.
	 * 
	 * @return a list of top relationships, children of the root relationship.
	 */
	// Retrieves the top relqtionships from the entity tree.
	// Returns a list of the top-level relqtionships in the entity tree.
	public List<Relationship> getTopRelationships() {
		return toRelationships(getRelationshipTree().getChildren());
	}
	
	
	/**
	 * Returns a list of relationship names for the top relationships,  .
	 *
	 * @return a list of relationship names
	 * @see #getTopRelationships()
	 */
	// Returns a list of the names of the top-level relationships.
	public List<String> getTopRelationshipsToString() {
		return getTopRelationships().stream()
									.map(Relationship::getName)
									.collect(Collectors.toList());
	}
	
	// Converts a list of Entity objects to a list of Relationship objects by casting.
	public static List<Relationship> toRelationships(List<Entity> entities) {
		return entities.stream()
					   .map(er -> (Relationship) er)
					   .collect(Collectors.toList());
	}
	
	// Returns the entity tree.
	public Entity getEntityTree() {
		return entityTree;
	}
	
	// Returns the relationship tree.
	public Relationship getRelationshipTree() {
		return relationshipTree;
	}

	// Returns the list of removed entities.
	public ArrayList<String> getRemovedEntities() {
		return removedEntities;
	}

	// Returns the list of removed relationships.
	public ArrayList<String> getRemovedRelationships() {
		return removedRelationships;
	}
	
	/* Davide: forse da rimuovere
	private void removEntity(String entity) {
		if(getEntity(entity) != null) { //ste la remove dovrebbe funzionare anche se non c'era
			getTopEntities().remove(getEntity(entity));
		}
		Vector<Relationship> relationshipsToRemove = new Vector<>();
		for(Relationship r : relationships) {
			Vector<Reference> refsToRemove = new Vector<Reference>();
			for(Reference ref : r.getReferences()) {
				if(ref.getSubject().equalsIgnoreCase(entity) || ref.getObject().equalsIgnoreCase(entity)) {
					refsToRemove.add(ref);
				}
			}
			r.removeAll(refsToRemove);
			if(r.getReferences().size() == 0) {
				relationshipsToRemove.add(r);
			}
		}
		relationships.removeAll(relationshipsToRemove);
	}
	*/
	
	// Retrieves a list of attributes for a given entity.
	public List<Attribute> properties(String entity) {
		Entity e = getEntity(entity);
		return propertiesCommon(e);
	}
	
	// Retrieves a list of attributes for a given relationship.
	public List<Attribute> propertiesRelation(String relation) {
		Relationship r = getRelationship(relation);
		return propertiesCommon(r);
	}
	
	// Retrieves a list of attributes for an entity or relationship, considering its parent attributes if available.
	private List<Attribute> propertiesCommon(Entity e) {
		ArrayList<Attribute> attributes = new ArrayList<>();
		if (e != null) {
			attributes.addAll(e.getAttributes());
			if(e.getParent()!=null) {
				attributes.addAll(propertiesCommon(e.getParent()));
			}
			return attributes;
		} else
			return new ArrayList<Attribute>();
	}
	
	// Generates a relationship name string from subject, relationship, and object.
	public static String relationName(String subject, String relationship, String object) {
		return subject + "." + relationship + "." + object;
	}
	
	// Removes an entity from the entity tree and detaches it.
	public void removeEntity(String name) {

		Entity currentEntity=findInTree(entityTree, name);
		if(currentEntity != null) 
		{ // se sta da un'altra parte
		currentEntity.detach();
		}
		// REMOVE REFERENCES AND RELATIONSHIPS
	}
	
	// Removes a relationship from the relationship tree and detaches it.
	public void removeRelationship(String name) {

		Relationship currentRelationship = (Relationship)findInTree(relationshipTree, name);

		if(currentRelationship != null) 
		{ // se sta da un'altra parte
		currentRelationship.detach();
		}
	}
	
	/**
	 * Reads the attributes from the given parent node and returns a vector of Attribute objects.
	 *
	 * @param parentNode The parent node containing the attribute nodes.
	 * @return A vector of Attribute objects representing the attributes.
	 * @throws CloneNotSupportedException If cloning of Attribute objects is not supported.
	 * @throws IllegalArgumentException If the {@code <attribute>} tag contains an invalid attribute (allowed: name, datatype, description, mandatory, distinguishing, display, target, notes).
	 * @throws IllegalArgumentException If the {@code <attribute>} tag has datatype select or tree and contains an invalid child tag (allowed: {@code <value>}).
	 * @throws IllegalArgumentException If the {@code <attribute>} tag has datatype select or tree and the {@code <value>} tag contains an invalid attribute (allowed: name).
	 * @throws IllegalArgumentException If the {@code <attribute>} tag has datatype tree and has one descendantof which is not a {@code <value>} tag.
	 */
	private Vector<Attribute> readAttributes(org.w3c.dom.Node parentNode) throws CloneNotSupportedException { // nodo <attributes>
		Vector<Attribute> fullAttrs = new Vector<>();
		NodeList attributeNodes = parentNode.getChildNodes(); // parentNode e' <entity> in entity, altrimenti <attributes>, i figli sono gli attributi
//		List<Node> nodes = IntStream.range(0, attributeNodes.getLength())
//		.mapToObj(attributeNodes::item)
//		.filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
//		.filter(node-> node.getNodeName().equals("attribute"))
//		.peek(tag->validateTagAttributes(tag, List.of("name","datatype","description","mandatory","distinguishing","display","target","notes"), "name"))
//		.collect(Collectors.toList());
		List<Node> nodes = IntStream.range(0, attributeNodes.getLength())
		        .mapToObj(attributeNodes::item)
		        .filter(an -> an.getNodeType() == Node.ELEMENT_NODE)
		        .filter(node -> node.getNodeName().equals("attribute"))
		        .peek(tag -> validateTagAttributes(tag, Arrays.asList("name", "datatype", "description", "mandatory", "distinguishing", "display", "target", "notes"), "name"))
		        .collect(Collectors.toList());
		for(Node an : nodes) 
		{
				NamedNodeMap n = an.getAttributes(); // LEGGE GLI ATTRIBUTI DEL TAG!!! qui dell'attributo
				String attribute = n.getNamedItem("name").getNodeValue();
				String datatype = n.getNamedItem("datatype") != null ?
						n.getNamedItem("datatype").getNodeValue() : "";
				String description = n.getNamedItem("description") != null ?
						n.getNamedItem("description").getNodeValue() : "";
				Attribute currentAttr = new Attribute(attribute,datatype);
				currentAttr.setDescription(description);
				setOptionalAttributes(n, currentAttr);
				switch (datatype) {
					case "select":
						currentAttr.setValuesString(readValuesList(an,"value",true));
						break;
					case "tree":
						currentAttr.setSubClasses(readValuesTree(an,null));
						break;
					case "entity": //DA VEDERE
						currentAttr.setTarget(n.getNamedItem("target").getNodeValue());
						break;
					case "user-types":
						String target = n.getNamedItem("target").getNodeValue(); 
						if(fromAttributesToString(types).contains(target)) {
							Attribute type = types.get(fromAttributesToString(types).indexOf(target));
							currentAttr = (Attribute) type.clone(); //nik why clone?
							currentAttr.setName(attribute);
							currentAttr.setDescription(description);
							setOptionalAttributes(n, currentAttr);
						}
						break;
				}
				fullAttrs.add(currentAttr);
		}
		return fullAttrs;
	}
	
	/**
	 * Converts a vector of Attribute objects to a vector of their corresponding names.
	 *
	 * @param attributes the vector of Attribute objects to convert
	 * @return a vector of strings containing the names of the attributes
	 */
	private Vector<String> fromAttributesToString(Vector<Attribute> attributes) {
		return attributes.stream()
						 .map(Attribute::getName)
						 .collect(Collectors.toCollection(Vector::new));
	}
	
	private Vector<String> fromTypesToString(Vector<UType> types) {
		return types.stream()
					.map(UType::getName)
					.collect(Collectors.toCollection(Vector::new));
	}
	
	/**
	 * Reads the values from the given XML node and returns them as a list of strings.
	 * 
	 * @param parentNode  The XML node containing the values. should be called on either a {@code <attribute datatype="select">} tag or on a {@code <axioms>} tag.
	 * @param tag_name    The tag name the child of the parentNode must have.
	 * @param add_other   Flag indicating whether to add "Other" to the list of values.
	 * @return            The list of values extracted from the XML node.
	 * @throws IllegalArgumentException If the parentNode contains an invalid child tag (allowed: tag_name parameter).
	 * @throws IllegalArgumentException If the child tag contains an invalid attribute (allowed: name).
	 */
	private List<String> readValuesList(org.w3c.dom.Node parentNode, String tag_name, boolean add_other) { // parentNode = nodo <attribute datatype="select">
		NodeList valueNodes = parentNode.getChildNodes(); // i figli sono i valori
//		List<String> values = IntStream.range(0, valueNodes.getLength())
//				 					   .mapToObj(valueNodes::item)
//				 					   .filter(vn -> vn.getNodeType() == Node.ELEMENT_NODE)
//				 					   .peek(vn -> validateTag(vn,List.of(tag_name)))
//									   .peek(e->validateTagAttributes(e, List.of("name"), "name"))
//				 					   .map(vn -> vn.getAttributes().getNamedItem("name").getNodeValue())
//				 					   .collect(Collectors.toList());
		
		List<String> values = IntStream.range(0, valueNodes.getLength())
		        .mapToObj(valueNodes::item)
		        .filter(vn -> vn.getNodeType() == Node.ELEMENT_NODE)
		        .peek(vn -> validateTag(vn, Arrays.asList(tag_name)))
		        .peek(e -> validateTagAttributes(e, Arrays.asList("name"), "name"))
		        .map(vn -> vn.getAttributes().getNamedItem("name").getNodeValue())
		        .collect(Collectors.toList());
		if(add_other)
		values.add("Other");
		//System.out.println(parentNode.getAttributes().getNamedItem("name") + " " + values.size());
		//values.stream().forEach(System.out::println);
		return values;
	}

	
	/** parse the values from the given XML node, parsing the tree in DFS and return a tree of strings.
	 * @param parentNode The XML node containing the values. should be called on a {@code <attribute datatype="tree">} tag (root) or on a {@code <value>} tag .
	 * @param parent The parent node of the subtree to be created.
	 * @return the tree created from the XML node.
	 * @throws IllegalArgumentException If the parentNode contains an invalid child tag (allowed: {@code <value>}).
	 * @throws IllegalArgumentException If the child tag contains an invalid attribute (allowed: name).
	 */
	private DefaultTreeNode readValuesTree(org.w3c.dom.Node parentNode, DefaultTreeNode parent) { // nodo <String> deve riempire un albero di valori
		String name= parentNode.getNodeName().equals("attribute")? "- Select one -" : parentNode.getAttributes().getNamedItem("name").getNodeValue();
        DefaultTreeNode treeNode = new DefaultTreeNode(name, parent);
		NodeList valueNodes = parentNode.getChildNodes(); // i figli sono i valori
//		IntStream.range(0, valueNodes.getLength())
//				 .mapToObj(valueNodes::item)
//				 .filter(vn -> vn.getNodeType() == Node.ELEMENT_NODE)
//				 .peek(tag-> validateTag(tag,List.of("value")))
//				 .peek(tag->validateTagAttributes(tag, List.of("name"), "name"))
//				 .forEach(child-> {DefaultTreeNode subtree=readValuesTree(child, treeNode);
//							  if(!subtree.isLeaf())
//							  new DefaultTreeNode("Other " + child.getAttributes().getNamedItem("name").getNodeValue(), subtree); //ste ultimo figlio della radice
//							 }
//					     );
		IntStream.range(0, valueNodes.getLength())
        .mapToObj(valueNodes::item)
        .filter(vn -> vn.getNodeType() == Node.ELEMENT_NODE)
        .peek(tag -> validateTag(tag, Arrays.asList("value")))
        .peek(tag -> validateTagAttributes(tag, Arrays.asList("name"), "name"))
        .forEach(child -> {
            DefaultTreeNode subtree = readValuesTree(child, treeNode);
            if (!subtree.isLeaf()) {
                new DefaultTreeNode("Other " + child.getAttributes().getNamedItem("name").getNodeValue(), subtree); //ste ultimo figlio della radice
            }
        });
		return treeNode;
	}

	// Adds a value to a map if not already present, sorting the values.
	private void addValue(Map<String,Vector<String>> map, String key, String value) {
		Vector<String> oldValues = map.get(key);
		if(oldValues == null) {
			Vector<String> newValues = new Vector<String>();
			newValues.add(value);
			map.put(key, newValues);
		} else {
			if(!oldValues.contains(value)) {
				oldValues.add(value);
				Collections.sort(oldValues); //ste per evitare l'ordinamento ad ogni lettura
				map.put(key, oldValues);
			}
		}
	}
	
	// Sets optional attributes (mandatory, distinguishing, display) for an attribute.
	private void setOptionalAttributes(NamedNodeMap n, Attribute a) {
		try {
			a.setMandatory(n.getNamedItem("mandatory").getNodeValue().equals("true"));
		} catch (Exception e) {
			a.setMandatory(false); // inutile (di default)
		}
		try {
			a.setDistinguishing(n.getNamedItem("distinguishing").getNodeValue().equals("true"));
		} catch (Exception e) {
			a.setDistinguishing(false); // inutile (di default)
		}
		try{
			a.setDisplay(n.getNamedItem("display").getNodeValue().equals("true"));
		}
		catch (Exception e) {
			a.setDisplay(false); // inutile (di default)
		}
	}
	
	// Gets the inverse relationship for the given relationship name.
	public String getInverseRel(String relationship) {
		return getRelationship(relationship).getInverse();
	}
	
	// Returns the domain name.
	public String getDomain() {
		return domain;
	}
	
	// Returns a list of entities that have not been removed, filtering out those in the toRemove list.
	public List<Entity> getEntitiesNotRemoved(ArrayList<String> toRemove) {
		List<Entity> result = getTopEntities();
		Vector<Entity> entToRemove = new Vector<>();
		for(Entity e : getTopEntities()) {
			if(toRemove != null) {
				if(toRemove.contains(e.getName()))
					entToRemove.add(e);
			}
		}
		result.removeAll(entToRemove);
		return result;
	}
	
	// Returns all entities, including their children, from the entity tree.
	public Vector<Entity> getAllEntities() {
		Vector<Entity> s = new Vector<>();
		for (Entity e : getTopEntities()) {
			s.add(e);
			s.addAll(getAllChildren(e));
		}
		return s;
	}
	
	// Returns all entity names, including those of their children, from the entity tree.
	public Vector<String> getAllEntitiesToString() {
		Vector<String> s = new Vector<>();
		for (Entity e : getTopEntities()) {
			s.add(e.getName());
			s.addAll(getAllChildrenToString(e));
		}
		return s;
	}
	
	// Retrieves a relationship by its name, searching through the top-level relationships and their children.
	public Relationship getRelationship(String relName) {
		ArrayList<Relationship> children = new ArrayList<>();
		for (Relationship r : getTopRelationships()) {
			if(r.getName().equals(relName)) {
				return r;
			}
			for(Entity er : r.getChildren()) {
				Relationship rer = (Relationship) er;
				children.add(rer);
			}
		}
		return getRelationship(relName, children);
	}
	
	// Retrieves a relationship by its name from a list of relationships, searching through their children.
	public Relationship getRelationship(String relName, ArrayList<Relationship> topRels) {
		ArrayList<Relationship> children = new ArrayList<>();
		for (Relationship r : topRels) {
			if(r.getName().equals(relName)) {
				return r;
			}
			children.addAll(r.getChildrenRelationships());
		}
		return null;
	}
	
	// Returns all relationships, including nested ones, from the relationship tree.
	public List<Relationship> getAllRelationships() {
			List<Relationship> s = new ArrayList<>();
			Stack<Relationship> stack = new Stack<>();
			stack.addAll(getTopRelationships());
			while (!stack.isEmpty()) {
				Relationship current = stack.pop();
				s.add(current);
				for (Entity child : current.getChildren()) {
					if (child instanceof Relationship) {
						stack.push((Relationship) child);
					}
				}
			}

		return s;
	}
	
	// Returns all relationship names, including those of their children, from the relationship tree.
	public TreeSet<String> getAllRelationshipsToString() {
		return getAllRelationships().stream()
									.map(Relationship::getName)
									.collect(Collectors.toCollection(TreeSet::new));
	}
	
	private Vector<Entity> getAllChildren(Entity e) {
		Vector<Entity> s = new Vector<>();
		for(Entity child : e.getChildren()) {
			s.add(child);
			s.addAll(getAllChildren(child));
		}
		return s;
	}
	
	private Vector<String> getAllChildrenToString(Entity e) {
		Vector<String> s = new Vector<>();
		for(Entity child : e.getChildren()) {
			s.add(child.getName());
			s.addAll(getAllChildrenToString(child));
		}
		return s;
	}
	
	public Vector<String> getTopEntitiesToString() {
		Vector<String> s = new Vector<>();
		for (int i=0; i<getTopEntities().size(); i++) {
			s.add(getTopEntities().get(i).name);
		}
		return s;
	}
	
	public TreeSet<String> getSubjsFromRel(String relationship) {
		for(String relName : getAllRelationshipsToString()) {
			if(relName.equals(relationship)) {
				Relationship r = getRelationship(relName);
				return r.getSubjects();
			}			
		}
		return null;
	}
	
	public TreeSet<String> getObjsFromRel(String relationship) {
		for(String relName : getAllRelationshipsToString()) {
			if(relName.equals(relationship)) {
				Relationship r = getRelationship(relName);
				return r.getObjects();
			}			
		}
		return null;
	}
	
	
	public TreeSet<String> getSubjects() {
		return new TreeSet<String>(subjects);
	}	
	
	public TreeSet<String> getObjects() {
		return new TreeSet<String>(objects);
	}
	
	//Davide: probabilmente da rimuovere
	/*
	public Vector<String> getSubj_Rels(String subject) {
		return subjRels.get(subject);
	}
	public Vector<String> getSubj_Objs(String subject) {
		return subjObjs.get(subject);
	}
	public Vector<String> getRel_Subjs(String relation) {
		return relSubjs.get(relation);
	}
	public Vector<String> getRel_Objs(String relation) {
		return relObjs.get(relation);
	}
	public Vector<String> getObj_Subjs(String object) {
		return objSubjs.get(object);
	}
	public Vector<String> getObj_Rels(String object) {
		return objRels.get(object);
	}
	public Vector<String> getSubjRel_Objs(String subject, String relation) {
		return subjRel_Objs.get(subject + "." + relation);
	}
	*/
	public Set<String> getSubjObj_Rels(String subject, String object) {
		return new HashSet<String>(subjObj_Rels.get(subject + "." + object));
	}
	/*
	public Vector<String> getRelObj_Subjs(String relation, String object) {
		return relObj_Subjs.get(relation + "." + object);
	}
	public Set<String> getSubjRelObjs() { //ste VERIFICARE, LA CHIAMA UN UNICO METODO MAI USATO?? IN TAL CASO NON SERVE NEPPURE subjRelObjs
		return subjRelObjs;
	}
	*/
	
//	public void toXML() {
//		try {
//			PrintWriter xmlFile = new PrintWriter("/home/gbxmls/" + domain + ".gbs");
//			xmlFile.println("<?xml version=\"1.0\"?>");
//			xmlFile.println("<domain name=\"" + domain + "\">");
//			xmlFile.println("\t<entities>");
//			for(Entity e : getTopEntities()) {
//				xmlFile.println("\t\t<entity name = \"" + e + "\">");
//				xmlFile.println("\t\t</entity>");
//			}
//			xmlFile.println("\t</entities>");
//			xmlFile.println("\t<relationships>");
//			for(Relationship rr : relationships) {
//				String r = rr.getName();
//				xmlFile.println("\t\t<relationship name = \"" + r + "\" inverse = \"" + getInverseRel(r) + "\">");
//				xmlFile.println("\t\t</relationship>");
//			}
//			xmlFile.println("\t</relationships>");
//			xmlFile.println("</domain>");
//			xmlFile.close();
//		} catch(IOException e) {
//			e.printStackTrace();
//		}
//	}

	// Scaraggi
	
	private ArrayList<String> domainList;
	private String inverse;
	public Map<String, Vector<Attribute>> attrsRel = new HashMap<String, Vector<Attribute>>();

	public void setDomain(String domain) {
		this.domain = domain;
	}
	
	// Davide: forse da rimuovere
	/*
	public void loadFile(byte[] byteArray) throws ParserConfigurationException, SAXException, IOException {
		InputStream is = new ByteArrayInputStream(byteArray);
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document doc = builder.parse(is);
		try {
			loadFile(doc, doc.getDocumentElement().getAttributes().getNamedItem("name").getNodeValue());
		} catch (Exception e) {
			System.out.println("Invalid domain file!!!");
		}
	}
	*/

	public Map<String, String> getInverseRels() {
		return inverseRels;
	}
	public void setInverseRels(Map<String, String> inverseRels) {
		this.inverseRels = inverseRels;
	}

	public Map<String, Vector<String>> getRelSubjs() {
		return relSubjs;
	}
	public void setRelSubjs(Map<String, Vector<String>> relSubjs) {
		this.relSubjs = relSubjs;
	}

	public Map<String, Vector<String>> getRelObjs() {
		return relObjs;
	}
	public void setRelObjs(Map<String, Vector<String>> relObjs) {
		this.relObjs = relObjs;
	}

	public Map<String, Vector<Attribute>> getAttrsRel() {
		return attrsRel;
	}
	public void setAttrsRel(Map<String, Vector<Attribute>> attrsRel) {
		this.attrsRel = attrsRel;
	}

	public String getInverse() {
		return inverse;
	}
	public void setInverse(String inverse) {
		this.inverse = inverse;
	}

	public ArrayList<String> getDomainList() {
		return domainList;
	}
	public void setDomainList(ArrayList<String> domainList) {
		this.domainList = domainList;
	}
	
	/*
	public Relationship getRelationship(String relationshipName) {
		for(Relationship r : getTopRelationships()) {
			if(r.getName().equals(relationshipName)) {
				return r;
			}
		}
		return null;
	}
	*/
	
//	public Vector<Relationship> getRelationships(Entity entity) { //ste mai usata?
//		Vector<Relationship> includes = new Vector<>();
//		for(Relationship r : relationships) {
//			if(r.getSubjects().contains(entity.getName()) || r.getObjects().contains(entity.getName())) {
//				includes.add(r);
//			}
//		}
//		return includes;
//	}
	// Retrieves all the children of the given entity, recursively.
	public Vector<Relationship> getRelationshipsToString(String entity) {
		Vector<Relationship> includes = new Vector<>();
		for(Relationship r : getAllRelationships()) {
			if(r.getSubjects().contains(entity) || r.getObjects().contains(entity))
				includes.add(r);
		}
		return includes;
	}
	public List<Relationship> getRelationshipsForSubj(String entity) {
		List<Relationship> includes = new LinkedList<>();
		for(Relationship r : getAllRelationships()) {
			if(r.getSubjects().contains(entity))
				includes.add(r);
		}
		return includes;
	}
	
	// Retrieves all the names of the children of the given entity, recursively.
	public List<Relationship> getRelationshipsForObj(String entity) {
		List<Relationship> includes = new LinkedList<>();
		for(Relationship r : getAllRelationships()) {
			if(r.getObjects().contains(entity))
				includes.add(r);
		}
		return includes;
	}

	// Retrieves a list of top-level entities as strings.
	public List<String> getImportedFiles() {
		return importedFiles;
	}
	
	// Retrieves a set of subjects for a given relationship.
	public Entity getEntity(String entityName) {
		List<Entity> children = new ArrayList<>();
		for(Entity e : getTopEntities()) {
			if(e.getName().equals(entityName)) {
				return e;
			}else {
				children.addAll(e.getChildren());
			}
		}
		return children.size() == 0 ? null : getSubEntity(children, entityName);
	}
	
	// Retrieves a set of objects for a given relationship.
	public Entity getSubEntity(List<Entity> entities, String entityName) {
		List<Entity> children = new ArrayList<>();
		for(Entity e : entities) {
			if(e.getName().equals(entityName)) {
				return e;
			}else {
				children.addAll(e.getChildren());
			}
		}
		return children.size() == 0 ? null : getSubEntity(children, entityName);
	}
	
	public void removeEntities(List<Entity> entities) {
		for(Entity e : entities) {
			if(!e.getDomain().equals(domain))
				getTopEntities().remove(e);
		}
	}
	
	public void removeRelationships(String domainToRemove) {
		ArrayList<Relationship> toRemove = new ArrayList<>();
		for(Relationship r : getAllRelationships()) {
			if(r.getDomain().equals(domainToRemove))
				toRemove.add(r);
		}

		for(Relationship r : toRemove) {
			removeRelationship(r.getName());
		}
		
	}
	
	/**
	 * Finds the entity with the given name in the tree, exploring it in DFS order.
	 * @param parent The parent entity to start the search from.
	 * @param childEntity The name of the entity to find.
	 * @return The entity with the given name, or null if it is not found.
	 */
	public Entity findInTree(Entity parent, String childEntity) {
		List<Entity> children = parent.getChildren();
		Entity result = null;
		for(Entity child : children) {
				if(child.toString().equalsIgnoreCase(childEntity)) {
					return child;
				}else {
					result = findInTree(child, childEntity);
					if(result != null) {
						break;
					}
				}
		}
		return result;
	}
	
	
	
	public int getnTopEntities() {
		return getTopEntities().size();
	}

	public int getnSubEntities() {
		return getAllEntitiesToString().size()-getnTopEntities();
	}
	public int getnTopRels() {
		return relationshipTree.getChildren().size();
	}

	public int getnRelRefs() {
		return nRelRefs;
	}
	static String readFile(String path, Charset encoding) throws IOException {
		byte[] encoded = Files.readAllBytes(Paths.get(path));
		return new String(encoded, encoding);
	}

	// Retrieves a set of relationships that have the specified subject.
	public TreeSet<String> getRelationshipsWithSubj(String subject) {
		TreeSet<String> relationships = new TreeSet<>();
		for(String relName : getAllRelationshipsToString()) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				Entity subjEntity = findInTree(entityTree, subject);
				if(ref.getSubject().equals(subject) || findInTree(subjEntity, ref.getSubject())!=null) {
					//relationships.add(relName);
					relationships.add(r.getTop());
				}
			}
		}
		return new TreeSet<>(relationships);
	}
	
	// Retrieves a set of relationships that have the specified object.
	public TreeSet<String> getRelationshipsWithObj(String object) {
		TreeSet<String> relationships = new TreeSet<>();
		for(String relName : getAllRelationshipsToString()) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				Entity objEntity = findInTree(entityTree, object);
				if(ref.getObject().equals(object) || findInTree(objEntity, ref.getObject())!=null) {
					relationships.add(r.getTop());
				}
			}
		}
		return new TreeSet<>(relationships);
	}

	// Retrieves a list of objects from the specified relationships.
	public Vector<String> getObjsFromRel(List<String> relationships) {
		TreeSet<String> objects = new TreeSet<>();
		for(String relName : relationships) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				objects.add(ref.getObject());
			}
		}
		return new Vector<String>(objects);
	}
	
	// Retrieves a list of subjects from the specified relationships.
	public Vector<String> getSubjsFromRel(List<String> relationships) {
		Set<String> subjects = new HashSet<>();
		for(String relName : relationships) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				subjects.add(ref.getSubject());
			}
		}
		return new Vector<String>(subjects);
	}

	// Retrieves a set of objects related to the specified subject and relationship.
	public TreeSet<String> getObjsFromSubjRel(String subject, String relName) {
		Entity parent = findInTree(entityTree, subject);
		TreeSet<String> objects = new TreeSet<>();
		Relationship r = getRelationship(relName);
		for(Reference ref : r.getReferences()) {
			if(ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null)
				objects.add(ref.getObject());
		}
		return objects;
	}
	
	// Retrieves a set of subjects related to the specified object and relationship.
	public TreeSet<String> getSubjsFromObjRel(String object, String relName) {
		Entity parent = findInTree(entityTree, object);
		TreeSet<String> subjects = new TreeSet<>();
		Relationship r = getRelationship(relName);
		for(Reference ref : r.getReferences()) {
			if(ref.getObject().equals(object) || findInTree(parent, ref.getObject())!=null)
				subjects.add(ref.getSubject());
		}
		return subjects;
	}

	// Retrieves a set of relationships related to the specified subject and object.
	public TreeSet<String> getRelFromSubjObj(String subject, String object) {
		TreeSet<String> rels = new TreeSet<>();
		Entity parentSubject = findInTree(entityTree, subject);
		Entity parentObject = findInTree(entityTree, object);
		for(String relName : getAllRelationshipsToString()) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				if((ref.getSubject().equals(subject) || findInTree(parentSubject, ref.getSubject())!=null) && 
						(ref.getObject().equals(object) || findInTree(parentObject, ref.getObject())!=null)) 
					rels.add(r.getTop());
			}
		}
		return new TreeSet<>(rels);
	}

	// Retrieves a list of objects related to the specified subject and relationships.
	public List<String> getObjsFromSubRels(String subject, List<String> relationships) {
		Entity parent = findInTree(entityTree, subject);
		Set<String> objects = new HashSet<>();
		for(String relName : relationships) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				if(ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null)
					objects.add(ref.getObject());
			}
		}
		return new Vector<String>(objects);
	}
	
	// Retrieves a set of objects related to the specified subject.
	public TreeSet<String> getObjsFromSubj(String subject) {
		Entity parent = findInTree(entityTree, subject);
		TreeSet<String> objects = new TreeSet<>();
		for(String relName : getAllRelationshipsToString()) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				if(ref.getSubject().equals(subject) || findInTree(parent, ref.getSubject())!=null)
					objects.add(ref.getObject());
			}
		}
		return new TreeSet<String>(objects);
	}
	
	// Retrieves a set of subjects related to the specified object.
	public TreeSet<String> getSubjsFromObj(String object) {
		Entity parent = findInTree(entityTree, object);
		TreeSet<String> subjects = new TreeSet<>();
		for(String relName : getAllRelationshipsToString()) {
			Relationship r = getRelationship(relName);
			for(Reference ref : r.getReferences()) {
				if(ref.getObject().equals(object) || findInTree(parent, ref.getObject())!=null)
					subjects.add(ref.getSubject());
			}
		}
		return new TreeSet<String>(subjects);
	}
	
	public HashSet<Axiom> getAxioms() {
		return axioms;
	}

	public void setAxioms(HashSet<Axiom> axioms) {
		this.axioms = axioms;
	}
	
	/*
	public TreeSet<String> getSubjsFromRelsObj(String object, List<String> relationships) {
		return relationships.stream()
							.map(this::getRelationship)
							.flatMap(r -> r.getReferences().stream())
							.filter(ref -> ref.getObject().equals(object))
							.map(Reference::getSubject)
							.collect(Collectors.toCollection(TreeSet::new));
	}*/
	
	// NEW METHODS
	
//	public Vector<String> getSubjRelObjs() {
//		Vector<String> subjRelObjs = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref: r.getReferences())
//				subjRelObjs.add(ref.getSubject() + "." + r.getName() + "." + ref.getObject());
//		}
//		return subjRelObjs;
//	}
	
//	public Vector<String> getSubjRels(Entity entity) {  // Sostituire con String se si passa solo il nome
//		Vector<String> subjRels = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref : r.getReferences()) {
//				if(ref.getSubject().equalsIgnoreCase(entity.name)) { // Eliminare .name se si passa solo il nome
//					if(!subjRels.contains(r.getName()))
//						subjRels.add(r.getName());
//				}
//			}
//		}
//		return subjRels;
//	}
	
//	public Vector<String> getSubjObjs(Entity entity) {
//		Vector<String> subjObjs = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref : r.getReferences()) {
//				if(ref.getSubject().equalsIgnoreCase(entity.name)) { 
//					if(!subjObjs.contains(ref.getObject()))
//						subjObjs.add(ref.getObject());
//				}
//			}
//		}
//		return subjObjs;
//	}
	
//	public Vector<String> getRelSubjs(Relationship relationship) {  
//		Vector<String> relSubjs = new Vector<>();
//		for(Reference ref : relationship.getReferences()) {
//			if(!relSubjs.contains(ref.getSubject()))
//				relSubjs.add(ref.getSubject());
//		}
//		return relSubjs;
//	}
	
//	public Vector<String> getRelObjs(Relationship relationship) {  
//		Vector<String> relObjs = new Vector<>();
//		for(Reference ref : relationship.getReferences()) {
//			if(!relObjs.contains(ref.getObject()))
//				relObjs.add(ref.getObject());
//		}
//		return relObjs;
//	}
	
//	public Vector<String> getObjSubjs(Entity entity) {
//		Vector<String> objSubjs = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref : r.getReferences()) {
//				if(ref.getObject().equalsIgnoreCase(entity.name)) { 
//					if(!objSubjs.contains(ref.getSubject()))
//						objSubjs.add(ref.getSubject());
//				}
//			}
//		}
//		return objSubjs;
//	}
	
//	public Vector<String> getObjRels(Entity entity) {  // Sostituire con String se si passa solo il nome
//		Vector<String> objRels = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref : r.getReferences()) {
//				if(ref.getObject().equalsIgnoreCase(entity.name)) { // Eliminare .name se si passa solo il nome
//					if(!objRels.contains(r.getName()))
//						objRels.add(r.getName());
//				}
//			}
//		}
//		return objRels;
//	}
	
//	public Vector<String> getSubjRel_Objs(Entity subject, Relationship relationship) {
//		Vector<String> objs = new Vector<>();
//		for(Reference ref : relationship.getReferences()) {
//			if(ref.getSubject().equals(subject.name)) 
//				objs.add(ref.getObject());
//		}
//		return objs;
//	}
	
//	public Vector<String> getSubjObj_Rels(Entity subject, Entity object) {  // Sostituire con Vector<Relationship> se non si vuole solo il nome
//		Vector<String> rels = new Vector<>();
//		for(Relationship r : relationships) {
//			for(Reference ref : r.getReferences()) {
//				if(ref.getSubject().equals(subject.name) && ref.getObject().equals(object.name)) {
//					if(rels.contains(r.getName()))
//						rels.add(r.getName());
//				}
//			}
//		}
//		return rels;
//	}
	
//	public Vector<String> getRelObj_Subjs(Relationship relationship, Entity object) {
//		Vector<String> subjs = new Vector<>();
//		for(Reference ref : relationship.getReferences()) {
//			if(ref.getObject().equals(object.name))
//				subjs.add(ref.getSubject());
//		}
//		return subjs;
//	}
}