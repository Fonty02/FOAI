import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class test {

    public static void main(String[] args) {
        String gbsFilePath = "general.gbs";
        System.out.println("Attempting to load GBS file: " + gbsFilePath);

        File gbsFile = new File(gbsFilePath);
        if (!gbsFile.exists() || !gbsFile.isFile()) {
            System.err.println("Error: GBS file not found or is not a valid file at path: " + gbsFilePath);
            return;
        }

        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(gbsFile);
            doc.getDocumentElement().normalize(); // Optional, but good practice

            Element root = doc.getDocumentElement();

            if (!"domain".equals(root.getTagName())) {
                throw new IllegalArgumentException("Root element is <" + root.getTagName() + ">, expected <domain>");
            }

            String domainName = root.getAttribute("name");
            if (domainName == null || domainName.isEmpty()) {
                domainName = "N/A";
            }

            List<String> importedFiles = new ArrayList<>();
            NodeList importsNodes = root.getElementsByTagName("imports");
            if (importsNodes.getLength() > 0) {
                Element importsTag = (Element) importsNodes.item(0); // Assuming only one <imports> tag directly under root
                NodeList importList = importsTag.getElementsByTagName("import");
                for (int i = 0; i < importList.getLength(); i++) {
                    Node importNode = importList.item(i);
                    if (importNode.getNodeType() == Node.ELEMENT_NODE) {
                        Element importElement = (Element) importNode;
                        String schema = importElement.getAttribute("schema");
                        importedFiles.add((schema == null || schema.isEmpty()) ? "N/A" : schema);
                    }
                }
            }

            int topEntitiesCount = 0;
            NodeList entitiesNodes = root.getElementsByTagName("entities");
            if (entitiesNodes.getLength() > 0) {
                Element entitiesTag = (Element) entitiesNodes.item(0); // Assuming one <entities> tag
                // To count only direct children 'entity' of 'entities' tag:
                NodeList entityList = entitiesTag.getChildNodes();
                for (int i = 0; i < entityList.getLength(); i++) {
                    Node entityNode = entityList.item(i);
                    if (entityNode.getNodeType() == Node.ELEMENT_NODE && "entity".equals(entityNode.getNodeName())) {
                        topEntitiesCount++;
                    }
                }
                // If you wanted to count all <entity> descendants of <entitiesTag>:
                // topEntitiesCount = entitiesTag.getElementsByTagName("entity").getLength();
            }

            // .//relationship means any 'relationship' element in the document starting from root
            NodeList allRelationships = root.getElementsByTagName("relationship");
            int allRelationshipsCount = allRelationships.getLength();

            // .//relationship/reference means 'reference' elements that are direct children of 'relationship' elements
            int nRelRefs = 0;
            for (int i = 0; i < allRelationships.getLength(); i++) {
                Node relationshipNode = allRelationships.item(i);
                if (relationshipNode.getNodeType() == Node.ELEMENT_NODE) {
                    Element relationshipElement = (Element) relationshipNode;
                    NodeList referenceChildren = relationshipElement.getChildNodes();
                    for (int j = 0; j < referenceChildren.getLength(); j++) {
                        Node refNode = referenceChildren.item(j);
                        if (refNode.getNodeType() == Node.ELEMENT_NODE && "reference".equals(refNode.getNodeName())) {
                            nRelRefs++;
                        }
                    }
                }
            }
            // Alternative for nRelRefs if you are sure 'reference' only appears under 'relationship':
            // NodeList allReferencesUnderRelationships = root.getElementsByTagName("reference");
            // int nRelRefs = 0;
            // for (int i=0; i<allReferencesUnderRelationships.getLength(); i++) {
            //    Node refNode = allReferencesUnderRelationships.item(i);
            //    if (refNode.getParentNode() != null && "relationship".equals(refNode.getParentNode().getNodeName())) {
            //        nRelRefs++;
            //    }
            // }


            int axiomsCount = 0;
            NodeList axiomsNodes = root.getElementsByTagName("axioms");
            if (axiomsNodes.getLength() > 0) {
                Element axiomsTag = (Element) axiomsNodes.item(0); // Assuming one <axioms> tag
                // To count only direct children 'axiom' of 'axioms' tag:
                NodeList axiomList = axiomsTag.getChildNodes();
                for (int i = 0; i < axiomList.getLength(); i++) {
                    Node axiomNode = axiomList.item(i);
                    if (axiomNode.getNodeType() == Node.ELEMENT_NODE && "axiom".equals(axiomNode.getNodeName())) {
                        axiomsCount++;
                    }
                }
                // If you wanted to count all <axiom> descendants of <axiomsTag>:
                // axiomsCount = axiomsTag.getElementsByTagName("axiom").getLength();
            }

            System.out.println("Successfully loaded domain: " + domainName);
            System.out.println("Imported files: " + importedFiles);
            System.out.println("Total top-level entities: " + topEntitiesCount);
            System.out.println("Total relationships loaded (including nested): " + allRelationshipsCount);
            System.out.println("Total relationship references: " + nRelRefs);
            System.out.println("Axioms loaded: " + axiomsCount);

        } catch (ParserConfigurationException e) {
            System.err.println("Error configuring XML parser: " + e.getMessage());
            e.printStackTrace(System.err);
        } catch (SAXException e) {
            System.err.println("Error parsing GBS file (XML structure issue): " + e.getMessage());
            e.printStackTrace(System.err);
        } catch (IOException e) {
            // This will catch FileNotFoundError if the file is deleted between check and parse
            System.err.println("Error reading GBS file: " + e.getMessage());
            e.printStackTrace(System.err);
        } catch (IllegalArgumentException e) { // For our custom root tag check
            System.err.println("Error during loading (Invalid structure/value): " + e.getMessage());
            e.printStackTrace(System.err);
        } catch (Exception e) {
            System.err.println("An unexpected error occurred during loading: " + e.getMessage());
            e.printStackTrace(System.err);
        }
    }
}