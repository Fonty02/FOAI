package converter;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

// --- Entity Classes ---
// (Entity class definitions remain largely the same as provided in the prompt,
// except for removing the Artifact list from the Entities container class
// and updating its constructor)

/**
 * Abstract base class for entities sharing common properties.
 * Provides a default 'ontology' field.
 */
abstract class BaseEntity {
    /**
     * The ontology category, defaulting to "general".
     */
    @JsonProperty("ontology")
    public String ontology = "General";
    /**
     * The type of the entity, e.g., "Item", "Document", "Person", "Organization", "Category".
     * Will be overridden in subclasses like Item and Document.
     */
    @JsonProperty("EntityType")
    public String entityType = "";
}

/**
 * Represents a general artifact entity. Base class for more specific types like Item and Document.
 * Includes common artifact properties like Title, Description, etc.
 * Fields with null values will be excluded from the JSON output using {@link JsonInclude.Include#NON_NULL}.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Artifact extends BaseEntity {
    // Initializes the specific entity type for Artifact instances.
    // NOTE: This class remains as a base, but we won't create direct Artifact instances from rows anymore.
    { entityType = "Artifact"; } // Base type definition

    /**
     * The title of the artifact. Expected to be a mandatory field based on parsing logic.
     */
    @JsonProperty("Title")
    public String title;
    /**
     * A description of the artifact. Populated from the "Description" CSV field.
     */
    @JsonProperty("Description")
    public String description;
    /**
     * Comments related to the description. Populated from the "DescComment" CSV field.
     */
    @JsonProperty("DescComment")
    public String descComment;
    /**
     * Information about where the artifact was made. Populated from the "WherMade" CSV field.
     */
    @JsonProperty("WherMade")
    public String wherMade;

    // equals() and hashCode() remain the same as provided

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Artifact artifact = (Artifact) o;
        return Objects.equals(ontology, artifact.ontology) &&
                Objects.equals(entityType, artifact.entityType) &&
                Objects.equals(title, artifact.title) &&
                Objects.equals(description, artifact.description) &&
                Objects.equals(descComment, artifact.descComment) &&
                Objects.equals(wherMade, artifact.wherMade);
    }

    @Override
    public int hashCode() {
        return Objects.hash(ontology, entityType, title, description, descComment, wherMade);
    }
}

/**
 * Represents a specific type of Artifact, typically a physical object with a part number.
 * Inherits properties from {@link Artifact} and adds Item-specific fields like PartNum and ConditionNts.
 * The {@code entityType} is set to "Item".
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Item extends Artifact {
    // Initializes the specific entity type for Item instances.
    { entityType = "Item"; }

    /**
     * The part number associated with the item. Populated from the "PartNum" CSV field.
     * Can be set to "N/A" if the original value is invalid.
     */
    @JsonProperty("PartNum")
    public String partNum; // MODIFIED: Can now hold "N/A"
    /**
     * Notes regarding the condition of the item. Populated from the "ConditionNts" CSV field.
     */
    @JsonProperty("ConditionNts")
    public String conditionNts;

    // equals() and hashCode() remain the same as provided

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false; // Check base class fields first
        Item item = (Item) o;
        // PartNum comparison now includes potential "N/A" value
        return Objects.equals(partNum, item.partNum) &&
                Objects.equals(conditionNts, item.conditionNts);
    }

    @Override
    public int hashCode() {
        // PartNum hash now includes potential "N/A" value
        return Objects.hash(super.hashCode(), partNum, conditionNts);
    }
}

/**
 * Represents a document entity, such as a paper or digital file.
 * Inherits properties from {@link Artifact} and adds Document-specific fields like ToC, Extent, SerialNum, etc.
 * The {@code entityType} is set to "Document".
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Document extends Artifact {
    // Initializes the specific entity type for Document instances.
    { entityType = "Document"; }

    /**
     * Table of Contents information for the document. Populated from the "ToC" CSV field. Can be "N/A".
     */
    @JsonProperty("ToC")
    public String toC; // MODIFIED: Can now hold "N/A"
    /**
     * The extent or size of the document. Populated from the "Extent" CSV field. Can be "N/A".
     */
    @JsonProperty("Extent")
    public String extent; // MODIFIED: Can now hold "N/A"
    /**
     * A serial number associated with the document. Populated from the "SerialNum" CSV field. Can be "N/A".
     */
    @JsonProperty("SerialNum")
    public String serialNum; // MODIFIED: Can now hold "N/A"
    /**
     * Bibliographic citation information. Populated from the "BibCit" CSV field. Can be "N/A".
     */
    @JsonProperty("BibCit")
    public String bibCit; // MODIFIED: Can now hold "N/A"
    /**
     * The creation date or period of the document. Populated from "Created" or falls back to "DateCR" CSV fields. Can be "N/A".
     */
    @JsonProperty("Created")
    public String created; // MODIFIED: Can now hold "N/A"
    /**
     * Indicates if the document is copyrighted. Populated from the "Copyrighted" CSV field ('y'/'n'/'0').
     * Uses {@link Boolean} wrapper class to allow for {@code null}.
     */
    @JsonProperty("Copyrighted")
    public Boolean copyrighted;

    // equals() and hashCode() remain the same as provided (comparing potential "N/A" values)

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false; // Check base class fields first
        Document document = (Document) o;
        return Objects.equals(toC, document.toC) &&
                Objects.equals(extent, document.extent) &&
                Objects.equals(serialNum, document.serialNum) &&
                Objects.equals(bibCit, document.bibCit) &&
                Objects.equals(created, document.created) &&
                Objects.equals(copyrighted, document.copyrighted);
    }

    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), toC, extent, serialNum, bibCit, created, copyrighted);
    }
}

/**
 * Represents a person entity.
 * Class definition remains the same as provided.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Person extends BaseEntity {
    { entityType = "Agent:Person"; }
    @JsonProperty("Name")
    public String name;
    @JsonProperty("Surname")
    public String surname;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person person = (Person) o;
        return Objects.equals(ontology, person.ontology) &&
                Objects.equals(name, person.name) &&
                Objects.equals(surname, person.surname);
    }
    @Override
    public int hashCode() {
        return Objects.hash(ontology, name, surname);
    }
}

/**
 * Represents an organization entity.
 * Class definition remains the same as provided.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Organization extends BaseEntity {
    { entityType = "Agent:Organization"; }
    @JsonProperty("name") // Lowercase 'n' as specified
    public String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Organization that = (Organization) o;
        return Objects.equals(ontology, that.ontology) &&
                Objects.equals(name, that.name);
    }
    @Override
    public int hashCode() {
        return Objects.hash(ontology, name);
    }
}

/**
 * Represents a category or subject classification.
 * Class definition remains the same as provided.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Category extends BaseEntity {
    { entityType = "ContentDescription:Category"; }
    @JsonProperty("name")
    public String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Category category = (Category) o;
        return Objects.equals(name, category.name);
    }
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}

/**
 * Represents the material an item is made of.
 * Class definition remains the same as provided.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Material extends BaseEntity {
    { entityType = "Material"; }
    @JsonProperty("name")
    public String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Material material = (Material) o;
        return Objects.equals(name, material.name);
    }
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}

/**
 * Represents a relationship between two entities.
 * Class definition remains the same as provided.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Relationship extends BaseEntity {
    @JsonIgnore // EntityType not needed in Relationship JSON
    public String entityType; // Overrides BaseEntity definition

    @JsonProperty("Type")
    public String type;
    @JsonProperty("Subject")
    public String subject;
    @JsonProperty("SubjectType")
    public String subjectType;
    @JsonProperty("Object")
    public String object;
    @JsonProperty("ObjectType")
    public String objectType;
    @JsonProperty("number")
    public String number;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Relationship that = (Relationship) o;
        return Objects.equals(ontology, that.ontology) &&
                Objects.equals(type, that.type) &&
                Objects.equals(subject, that.subject) &&
                Objects.equals(subjectType, that.subjectType) &&
                Objects.equals(object, that.object) &&
                Objects.equals(objectType, that.objectType) &&
                Objects.equals(number, that.number);
    }
    @Override
    public int hashCode() {
        return Objects.hash(ontology, type, subject, subjectType, object, objectType, number);
    }
}


// --- Classes for JSON Output Structure ---

/**
 * Simple container for the collection information.
 * Class definition remains the same as provided.
 */
class CollectionInfo extends BaseEntity {
    { entityType = "Collection"; }
    @JsonProperty("name")
    public String name = "HCLE";

    public CollectionInfo() {
        this.entityType = "Collection";
        this.ontology = "General"; // Ensure ontology consistency
    }
}

/**
 * Container class grouping all extracted entities by their type AND including the collection information
 * for the final JSON output structure.
 * MODIFIED: Removed the 'Artifacts' list and updated the constructor.
 */
class Entities {
    @JsonProperty("Collection")
    public List<CollectionInfo> collection;

    // @JsonProperty("Artifacts") // REMOVED
    // public List<Artifact> artifacts; // REMOVED

    @JsonProperty("Items")
    public List<Item> items;
    @JsonProperty("Documents")
    public List<Document> documents;
    @JsonProperty("People")
    public List<Person> people;
    @JsonProperty("Organizations")
    public List<Organization> organizations;
    @JsonProperty("Categories")
    public List<Category> categories;
    @JsonProperty("Materials")
    public List<Material> materials;

    /**
     * MODIFIED Constructor for Entities object. Removed artifactsSet parameter.
     * Converts Sets of unique entities into Lists suitable for JSON serialization.
     *
     * @param itemsSet         Set of unique {@link Item} entities.
     * @param documentsSet     Set of unique {@link Document} entities.
     * @param peopleSet        Set of unique {@link Person} entities.
     * @param organizationsSet Set of unique {@link Organization} entities.
     * @param categoriesSet    Set of unique {@link Category} entities.
     * @param materialsSet     Set of unique {@link Material} entities.
     */
    public Entities(Set<Item> itemsSet, Set<Document> documentsSet, // Removed artifactsSet
                    Set<Person> peopleSet, Set<Organization> organizationsSet,
                    Set<Category> categoriesSet, Set<Material> materialsSet) {
        this.collection = new ArrayList<>();
        this.collection.add(new CollectionInfo());

        // this.artifacts = new ArrayList<>(artifactsSet); // REMOVED
        this.items = new ArrayList<>(itemsSet);
        this.documents = new ArrayList<>(documentsSet);
        this.people = new ArrayList<>(peopleSet);
        this.organizations = new ArrayList<>(organizationsSet);
        this.categories = new ArrayList<>(categoriesSet);
        this.materials = new ArrayList<>(materialsSet);
    }
}

/**
 * Root class representing the overall structure of the JSON output file.
 * Contains the main "Entities" object and the top-level "Relationships" list.
 * Class definition remains the same as provided.
 */
class JsonOutput {
    @JsonProperty("Entities")
    public Entities entities;
    @JsonProperty("Relationships")
    public List<Relationship> relationships;

    /**
     * Constructs the final JSON output structure. Filters invalid relationships.
     *
     * @param entities        The {@link Entities} object containing collection info and lists of all unique entities.
     * @param relationshipSet The {@link Set} of unique {@link Relationship} objects generated during CSV parsing.
     */
    public JsonOutput(Entities entities, Set<Relationship> relationshipSet) {
        this.entities = entities;
        // Filter relationships to ensure essential fields are present before adding to the final list.
        this.relationships = relationshipSet.stream()
                .filter(rel -> rel.ontology != null && !rel.ontology.isEmpty() &&
                        rel.type != null && !rel.type.isEmpty() &&
                        rel.subject != null && !rel.subject.isEmpty() &&
                        rel.subjectType != null && !rel.subjectType.isEmpty() &&
                        rel.object != null && !rel.object.isEmpty() &&
                        rel.objectType != null && !rel.objectType.isEmpty()
                        // 'number' can be null
                )
                .collect(Collectors.toList());
    }
}


// --- Main Converter Class ---

/**
 * Main class responsible for converting data from a CSV file into a structured JSON format.
 * MODIFIED to classify rows as only Item or Document, handle N/A values, and remove generic Artifacts.
 */
public class CsvToJsonConverter {

    // --- Regex Patterns (remain the same) ---
    private static final Pattern PERSON_REGEX_STRICT = Pattern.compile(
            "^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+\\s[A-Z][a-z]+(?:\\s[A-Z][a-z]+)?(?:,?\\s(?:Jr\\.|Sr\\.|III))?$"
    );
    private static final Pattern PERSON_REGEX_LIST = Pattern.compile(
            "^(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)+(?:\\s(?:Jr\\.|Sr\\.|III))?(?:(?:\\s*(?:,|;|\\band\\b|&)\\s*)(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*(?:\\s(?:Jr\\.|Sr\\.|III))?)*$"
    );
    private static final Pattern NAME_SPLIT_DELIMITER = Pattern.compile("\\s*(?:,|;|\\band\\b|&)\\s*");

    /**
     * Main entry point. MODIFIED data structures and processing logic.
     *
     * @param args Command line arguments (not currently used).
     */
    @SuppressWarnings("deprecation")
    public static void main(String[] args) {

        // --- Configuration (remains the same) ---
        String csvFilePath = "src/HCLEcatalog.csv";
        String logFilePath = "src/output/parsing.log";
        String jsonFilePath = "src/output/data.json";

        // --- Data Structures (MODIFIED: removed setOfArtifacts) ---
        Set<Item> setOfItems = new HashSet<>();
        Set<Document> setOfDocuments = new HashSet<>();
        // Set<Artifact> setOfArtifacts = new HashSet<>(); // REMOVED
        Set<Material> setOfMaterialTypes = new HashSet<>();
        Set<Organization> setOfOrganizations = new HashSet<>();
        Set<Relationship> setOfRelationships = new HashSet<>();
        Set<Person> setOfPeople = new HashSet<>();
        Set<Category> setOfContentDescriptions = new HashSet<>();

        // --- File Processing ---
        try (
                Reader reader = Files.newBufferedReader(Paths.get(csvFilePath), StandardCharsets.UTF_8);
                CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT
                        .withHeader()
                        .withIgnoreHeaderCase()
                        .withTrim());
                PrintWriter logWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(logFilePath), StandardCharsets.UTF_8))
        ) {

            int rowIndex = 0;
            for (CSVRecord csvRecord : csvParser) {
                rowIndex++;
                // --- Basic Row Validation & Data Extraction (remains the same) ---
                String idNum = getRecordValue(csvRecord, "IdNum");
                if (isNullOrEmpty(idNum)) {
                    logWriter.printf("Row %d ERROR -> IdNum is null or empty%n", rowIndex);
                    continue;
                }
                Map<String, String> rowData = new HashMap<>();
                for (String header : csvParser.getHeaderMap().keySet()) {
                    rowData.put(header, getRecordValue(csvRecord, header)); // Already handles null
                }

                // --- MODIFIED: Determine Entity Type (Document or Item only) ---
                String entityType; // Will be "Document" or "Item"

                // Check for Document characteristics first
                String tocVal = rowData.get("ToC");
                String extentVal = rowData.get("Extent");
                String serialNumVal = rowData.get("SerialNum");
                String bibCitVal = rowData.get("BibCit");
                boolean isDocument = !isNullOrNone(tocVal) || !isNullOrNone(extentVal)
                        || !isNullOrNone(serialNumVal) || !isNullOrNone(bibCitVal);

                if (isDocument) {
                    entityType = "Document";
                } else {
                    // If not a Document, it's automatically an Item
                    entityType = "Item";
                }
                // Generic Artifact type is no longer assigned here.

                // --- Check Mandatory Fields (Title) ---
                String title = rowData.get("Title");
                if (isNullOrNone(title)) {
                    logWriter.printf("Row %d ERROR -> Title is null or None. Skipping row.%n", rowIndex);
                    continue;
                }

                logWriter.printf("Row %d -> Type: %s -> ID: %s, Title: %s -> Processing...%n", rowIndex, entityType, idNum, title);

                // --- MODIFIED: Create the Core Entity Object (Document or Item) ---
                Artifact currentEntity; // Use base class, but will hold Document or Item

                if ("Document".equals(entityType)) {
                    Document doc = new Document();
                    doc.title = title;

                    // --- Populate Document fields with N/A handling ---
                    doc.toC = isNullOrNone(tocVal) ? "N/A" : tocVal;
                    doc.extent = isNullOrNone(extentVal) ? "N/A" : extentVal;
                    doc.serialNum = isNullOrNone(serialNumVal) ? "N/A" : serialNumVal;
                    doc.bibCit = isNullOrNone(bibCitVal) ? "N/A" : bibCitVal;

                    // Handle 'Created' date: use "Created" field, fallback to "DateCR", then check for N/A
                    String createdRaw = rowData.get("Created");
                    if (isNullOrNone(createdRaw)) {
                        createdRaw = rowData.get("DateCR"); // Fallback
                    }
                    doc.created = isNullOrNone(createdRaw) ? "N/A" : createdRaw;

                    // Handle 'Copyrighted' (no N/A logic needed, it's Boolean/null)
                    String copyrightedStr = rowData.get("Copyrighted");
                    if (!isNullOrNone(copyrightedStr)) {
                        if ("y".equalsIgnoreCase(copyrightedStr.trim())) {
                            doc.copyrighted = true;
                        } else if ("n".equalsIgnoreCase(copyrightedStr.trim()) || "0".equals(copyrightedStr.trim())) {
                            doc.copyrighted = false;
                        } // else leave null
                    }
                    currentEntity = doc;

                } else { // Entity type is "Item"
                    Item item = new Item();
                    item.title = title;

                    // --- Populate Item fields with N/A handling for PartNum ---
                    String partNumRaw = rowData.get("PartNum");
                    // Check if PartNum is valid (exists AND not a single digit)
                    if (!isNullOrNone(partNumRaw) && !partNumRaw.trim().matches("^\\d$")) {
                        item.partNum = partNumRaw.trim(); // Use valid PartNum
                    } else {
                        item.partNum = "N/A"; // Set to N/A if missing, None, or single digit
                    }

                    // Populate other Item fields (only if not null/None)
                    String conditionNts = rowData.get("ConditionNts");
                    if (!isNullOrNone(conditionNts)) {
                        item.conditionNts = conditionNts;
                    }
                    currentEntity = item;
                }

                // --- Populate Common Artifact Fields (apply to Item/Document) ---
                // Only populate if the value is valid (not null/None)
                String description = rowData.get("Description");
                if (!isNullOrNone(description)) {
                    currentEntity.description = description;
                }
                String descComment = rowData.get("DescComment");
                if (!isNullOrNone(descComment)) {
                    currentEntity.descComment = descComment;
                }
                String wherMade = rowData.get("WherMade");
                if (!isNullOrNone(wherMade)) {
                    currentEntity.wherMade = wherMade;
                }

                // --- Add the created Core Entity to its respective Set ---
                if (currentEntity instanceof Document) {
                    setOfDocuments.add((Document) currentEntity);
                } else { // It must be an Item
                    setOfItems.add((Item) currentEntity);
                }
                // No case for adding to setOfArtifacts needed anymore

                // --- Process Related Entities and Create Relationships (Logic largely the same, but check conditions) ---

                // 1. Material Entity (remains the same)
                String materialStr = rowData.get("Material");
                Material currentMaterial = null;
                if (materialStr != null) {
                    String materialName = null;
                    String trimmedMaterial = materialStr.trim();
                    if ("papr".equalsIgnoreCase(trimmedMaterial)) materialName = "paper";
                    else if ("digi".equalsIgnoreCase(trimmedMaterial)) materialName = "digital";
                    else if ("mix".equalsIgnoreCase(trimmedMaterial)) materialName = "mix";

                    if (materialName != null) {
                        currentMaterial = new Material();
                        currentMaterial.name = materialName;
                        setOfMaterialTypes.add(currentMaterial);
                    } else if (!trimmedMaterial.isEmpty() && !"none".equalsIgnoreCase(trimmedMaterial) && !"null".equalsIgnoreCase(trimmedMaterial)) {
                        logWriter.printf("Row %d WARNING -> Unrecognized Material code: '%s'%n", rowIndex, trimmedMaterial);
                    }
                }

                // 2. Category Entity (remains the same)
                String subjectTop = rowData.get("SubjectTop");
                Category currentCategory = null;
                if (!isNullOrNone(subjectTop)) {
                    currentCategory = new Category();
                    currentCategory.name = subjectTop.trim();
                    setOfContentDescriptions.add(currentCategory);
                }

                // 3. Creator Entity (Person or Organization - remains the same)
                String creatorStr = rowData.get("Creator");
                Person creatorPerson = null;
                Organization creatorOrg = null;
                boolean isCreatorPerson = false;

                if (!isNullOrNone(creatorStr)) {
                    String trimmedCreator = creatorStr.trim();
                    if (PERSON_REGEX_STRICT.matcher(trimmedCreator).matches()) {
                        creatorPerson = parsePerson(trimmedCreator);
                        if (creatorPerson != null) {
                            setOfPeople.add(creatorPerson);
                            isCreatorPerson = true;
                        }
                    }
                    if (!isCreatorPerson) {
                        creatorOrg = new Organization();
                        creatorOrg.name = trimmedCreator;
                        setOfOrganizations.add(creatorOrg);
                    }
                }

                // --- Create Relationships (MODIFIED conditions where needed) ---

                // Relationship 1: "belongsTo" (Collection -> Entity) - Remains the same logic
                Relationship relBelongs = new Relationship();
                relBelongs.type = "belongsTo";
                relBelongs.subject = "HCLE";
                relBelongs.subjectType = "Collection";
                // Object is the entity's identifier (Title or Title + PartNum["N/A"] for Items)
                relBelongs.object = currentEntity.title;
                if (currentEntity instanceof Item) {
                    // Use the potentially "N/A" partNum
                    relBelongs.object += " " + ((Item) currentEntity).partNum;
                }
                relBelongs.objectType = currentEntity.entityType; // Item or Document
                relBelongs.number = idNum;
                setOfRelationships.add(relBelongs);

                // Relationship 2: "madeOf" (Item -> Material) - Remains the same logic
                if (currentEntity instanceof Item && currentMaterial != null) {
                    Relationship relMadeOf = new Relationship();
                    relMadeOf.type = "madeOf";
                    // Subject is the Item identifier (Title + PartNum["N/A"])
                    relMadeOf.subject = currentEntity.title + " " + ((Item) currentEntity).partNum;
                    relMadeOf.subjectType = currentEntity.entityType; // "Item"
                    relMadeOf.object = currentMaterial.name;
                    relMadeOf.objectType = "Material";
                    setOfRelationships.add(relMadeOf);
                }

                // Relationship 3: "describe" (Category -> Entity)
                // MODIFIED: Only create for Documents, not generic Artifacts
                if (currentEntity instanceof Document && currentCategory != null) { // Apply only to Documents
                    Relationship relDescribe = new Relationship();
                    relDescribe.type = "describe";
                    relDescribe.subject = currentCategory.name;
                    relDescribe.subjectType = "Category";
                    relDescribe.object = currentEntity.title; // Document title
                    relDescribe.objectType = currentEntity.entityType; // "Document"
                    setOfRelationships.add(relDescribe);
                }

                // Relationship 4: Creator Relationships ("developed" by Person / "produced" by Org)
                // MODIFIED: Only create for Documents, not generic Artifacts
                if (currentEntity instanceof Document) { // Apply only to Documents
                    if (isCreatorPerson && creatorPerson != null) {
                        Relationship relDev = new Relationship();
                        relDev.type = "developed";
                        relDev.subject = creatorPerson.name + " " + creatorPerson.surname;
                        relDev.subjectType = "Person";
                        relDev.object = currentEntity.title; // Document title
                        relDev.objectType = currentEntity.entityType; // "Document"
                        setOfRelationships.add(relDev);
                    } else if (creatorOrg != null) {
                        Relationship relProd = new Relationship();
                        relProd.type = "produced";
                        relProd.subject = creatorOrg.name;
                        relProd.subjectType = "Organization";
                        relProd.object = currentEntity.title; // Document title
                        relProd.objectType = currentEntity.entityType; // "Document"
                        setOfRelationships.add(relProd);
                    }
                }

                // Relationship 5 & 6: Contributor / Additional Author Relationships
                // The helper methods need to handle the correct object identifier (incl. PartNum for Items)
                // These relationships apply to both Items and Documents based on original logic.
                processContributorField(rowData.get("Contributor"), "developed", currentEntity,
                        setOfPeople, setOfOrganizations, setOfRelationships, logWriter, rowIndex);
                processContributorField(rowData.get("AddlAuth"), "collaborated", currentEntity,
                        setOfPeople, setOfOrganizations, setOfRelationships, logWriter, rowIndex);

                logWriter.printf("Row %d -> Completed processing.%n", rowIndex);

            } // End of loop iterating through CSV records

            logWriter.printf("Finished processing %d data rows.%n", rowIndex);
            logWriter.printf("Found %d unique Items, %d unique Documents.%n", // MODIFIED: Removed artifact count
                    setOfItems.size(), setOfDocuments.size());
            logWriter.printf("Found %d unique People, %d unique Organizations.%n",
                    setOfPeople.size(), setOfOrganizations.size());
            logWriter.printf("Found %d unique Categories, %d unique Materials.%n",
                    setOfContentDescriptions.size(), setOfMaterialTypes.size());
            logWriter.printf("Created %d unique Relationships.%n", setOfRelationships.size());


            // --- Prepare Final Data Structure for JSON Output ---
            // MODIFIED: Call Entities constructor without artifactsSet
            Entities entitiesContainer = new Entities(
                    setOfItems, setOfDocuments, // Artifact set removed
                    setOfPeople, setOfOrganizations,
                    setOfContentDescriptions, setOfMaterialTypes
            );
            JsonOutput outputData = new JsonOutput(entitiesContainer, setOfRelationships);

            // --- Write JSON Output File (remains the same) ---
            ObjectMapper objectMapper = new ObjectMapper();
            objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
            // objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL); // Optional

            try (PrintWriter jsonWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(jsonFilePath), StandardCharsets.UTF_8))) {
                objectMapper.writeValue(jsonWriter, outputData);
            }

            System.out.println("CSV to JSON conversion complete.");
            System.out.println("Log file generated at: " + logFilePath);
            System.out.println("JSON output generated at: " + jsonFilePath);

        } catch (IOException e) {
            System.err.println("An error occurred during processing: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    } // End of main method

    // --- Helper Methods ---

    // getRecordValue remains the same
    private static String getRecordValue(CSVRecord record, String headerName) {
        try {
            if (record.isMapped(headerName)) {
                return record.get(headerName);
            } else {
                return null;
            }
        } catch (IllegalArgumentException e) {
            System.err.printf("Warning: Error retrieving value for header '%s'. %s%n", headerName, e.getMessage());
            return null;
        }
    }

    // isNullOrNone remains the same
    private static boolean isNullOrNone(String s) {
        if (s == null) return true;
        String trimmed = s.trim();
        return trimmed.isEmpty() || "None".equalsIgnoreCase(trimmed) || "NULL".equalsIgnoreCase(trimmed);
    }

    // isNullOrEmpty remains the same
    private static boolean isNullOrEmpty(String s) {
        return s == null || s.trim().isEmpty();
    }

    // processContributorField remains the same (it calls helpers that are updated)
    private static void processContributorField(String fieldContent, String relationshipBaseType,
                                                Artifact currentEntity,
                                                Set<Person> peopleSet, Set<Organization> orgSet, Set<Relationship> relSet,
                                                PrintWriter logWriter, int rowIndex) {
        if (isNullOrNone(fieldContent)) {
            return;
        }
        String content = fieldContent.trim();
        boolean looksLikePersonList = PERSON_REGEX_LIST.matcher(content).matches();

        if (looksLikePersonList) {
            String[] potentialNames = NAME_SPLIT_DELIMITER.split(content);
            for (String nameStr : potentialNames) {
                String trimmedName = nameStr.trim();
                if (trimmedName.isEmpty()) continue;

                Person person = parsePerson(trimmedName);
                if (person != null) {
                    boolean added = peopleSet.add(person);
                    if(added) {
                       // logWriter.printf("Row %d -> Identified Person: %s %s from field '%s'%n", rowIndex, person.name, person.surname, content); // Reduced logging noise
                    }
                    addPersonRelationship(person, relationshipBaseType, currentEntity, relSet); // Updated helper handles object format
                } else {
                    logWriter.printf("Row %d -> Treating '%s' (from '%s') as Organization after failed person parse.%n", rowIndex, trimmedName, content);
                    addOrganizationAndRelationship(trimmedName, relationshipBaseType, currentEntity, orgSet, relSet, logWriter, rowIndex, false); // Updated helper handles object format
                }
            }
        } else {
            // logWriter.printf("Row %d -> Treating '%s' as a single Organization (did not match person list pattern).%n", rowIndex, content); // Reduced logging noise
            addOrganizationAndRelationship(content, relationshipBaseType, currentEntity, orgSet, relSet, logWriter, rowIndex, true); // Updated helper handles object format
        }
    }

    /**
     * MODIFIED: Creates Person relationship, handles Item object format.
     */
    private static void addPersonRelationship(Person person, String relationshipType, Artifact currentEntity, Set<Relationship> relSet) {
        Relationship rel = new Relationship();
        rel.type = relationshipType;
        rel.subject = person.name + " " + person.surname;
        rel.subjectType = "Person";
        // Object is the entity's identifier (Title or Title + PartNum["N/A"] for Items)
        rel.object = currentEntity.title;
        if (currentEntity instanceof Item) {
            rel.object += " " + ((Item) currentEntity).partNum; // Use potentially "N/A" partNum
        }
        rel.objectType = currentEntity.entityType; // Item or Document
        relSet.add(rel);
    }

    /**
     * MODIFIED: Creates Organization relationship, handles Item object format.
     */
    private static void addOrganizationAndRelationship(String orgName, String relationshipBaseType,
                                                       Artifact currentEntity, Set<Organization> orgSet, Set<Relationship> relSet,
                                                       PrintWriter logWriter, int rowIndex, boolean logAsNew) {
        Organization org = new Organization();
        org.name = orgName;
        boolean added = orgSet.add(org);

        if (added && logAsNew) {
           // logWriter.printf("Row %d -> Identified Organization: %s%n", rowIndex, org.name); // Reduced logging noise
        }

        Relationship rel = new Relationship();
        rel.type = relationshipBaseType.equals("developed") ? "produced" : relationshipBaseType;
        rel.subject = org.name;
        rel.subjectType = "Organization";
        // Object is the entity's identifier (Title or Title + PartNum["N/A"] for Items)
        rel.object = currentEntity.title;
        if (currentEntity instanceof Item) {
            rel.object += " " + ((Item) currentEntity).partNum; // Use potentially "N/A" partNum
        }
        rel.objectType = currentEntity.entityType; // Item or Document
        relSet.add(rel);
    }

    // parsePerson remains the same
    private static Person parsePerson(String nameStr) {
        if (isNullOrEmpty(nameStr)) {
            return null;
        }
        String cleanedName = nameStr.replaceAll("^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)|((?:,\\s*)?(?:Jr\\.|Sr\\.|III))$", "").trim();
        if (cleanedName.isEmpty()) {
            return null;
        }
        String[] nameParts = cleanedName.split("\\s+");
        if (nameParts.length >= 2) {
            Person person = new Person();
            person.name = nameParts[0];
            person.surname = String.join(" ", Arrays.copyOfRange(nameParts, 1, nameParts.length));
            return person;
        } else {
            // System.err.printf("Warning: Could not parse '%s' (cleaned: '%s') into Name/Surname (only %d part found). Treating as non-person.%n",
            //         nameStr, cleanedName, nameParts.length); // Reduced logging noise
            return null;
        }
    }

} // End CsvToJsonConverter class