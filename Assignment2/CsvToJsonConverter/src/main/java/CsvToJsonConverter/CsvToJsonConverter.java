package CsvToJsonConverter;

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
     * The type of the entity, e.g., "Item", "Document", "Artifact", "Person", "Organization", "Category".
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
    { entityType = "Artifact"; } // Set default entity type for Artifact

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

    // Constructors, getters, and setters are omitted for brevity in this example.
    // Jackson can work directly with public fields.

    /**
     * Compares this Artifact to another object for equality based on all fields, including those from BaseEntity.
     * Used for storing unique entities in Sets.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same artifact, {@code false} otherwise.
     */
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

    /**
     * Generates a hash code for this Artifact based on all fields, including those from BaseEntity.
     * Consistent with the {@link #equals(Object)} method.
     * @return The hash code value for this object.
     */
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
     * Its presence (and format) helps distinguish Items from other Artifacts.
     */
    @JsonProperty("PartNum")
    public String partNum;
    /**
     * Notes regarding the condition of the item. Populated from the "ConditionNts" CSV field.
     */
    @JsonProperty("ConditionNts")
    public String conditionNts;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Item to another object for equality. Checks both base class (Artifact) fields
     * and Item-specific fields (partNum, conditionNts).
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same item, {@code false} otherwise.
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false; // Check base class fields first
        Item item = (Item) o;
        return Objects.equals(partNum, item.partNum) &&
                Objects.equals(conditionNts, item.conditionNts);
    }

    /**
     * Generates a hash code for this Item. Includes the hash code from the base class (Artifact)
     * and hashes of the Item-specific fields. Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
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
     * Table of Contents information for the document. Populated from the "ToC" CSV field.
     */
    @JsonProperty("ToC")
    public String toC;
    /**
     * The extent or size of the document (e.g., number of pages, file size). Populated from the "Extent" CSV field.
     */
    @JsonProperty("Extent")
    public String extent;
    /**
     * A serial number associated with the document. Populated from the "SerialNum" CSV field.
     */
    @JsonProperty("SerialNum")
    public String serialNum;
    /**
     * Bibliographic citation information. Populated from the "BibCit" CSV field.
     */
    @JsonProperty("BibCit")
    public String bibCit;
    /**
     * The creation date or period of the document. Populated from "Created" or falls back to "DateCR" CSV fields.
     */
    @JsonProperty("Created")
    public String created;
    /**
     * Indicates if the document is copyrighted. Populated from the "Copyrighted" CSV field ('y'/'n'/'0').
     * Uses {@link Boolean} wrapper class to allow for {@code null} if the value is missing or unrecognized.
     */
    @JsonProperty("Copyrighted")
    public Boolean copyrighted;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Document to another object for equality. Checks both base class (Artifact) fields
     * and Document-specific fields.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same document, {@code false} otherwise.
     */
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

    /**
     * Generates a hash code for this Document. Includes the hash code from the base class (Artifact)
     * and hashes of the Document-specific fields. Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), toC, extent, serialNum, bibCit, created, copyrighted);
    }
}

/**
 * Represents a person entity, typically extracted from Creator, Contributor, or AddlAuth CSV fields.
 * Contains Name (first name) and Surname (last name).
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Person extends BaseEntity {
    // Initializer block sets the specific entity type for Person instances.
    { entityType = "Agent:Person"; }

    /**
     * The first name (given name) of the person. Derived by parsing name strings.
     */
    @JsonProperty("Name")
    public String name;
    /**
     * The last name (surname) of the person. Can include middle names/initials as derived by parsing.
     */
    @JsonProperty("Surname")
    public String surname;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Person to another object for equality based on ontology, name, and surname.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same person, {@code false} otherwise.
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person person = (Person) o;
        return Objects.equals(ontology, person.ontology) &&
                Objects.equals(name, person.name) &&
                Objects.equals(surname, person.surname);
    }

    /**
     * Generates a hash code for this Person based on ontology, name, and surname.
     * Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(ontology, name, surname);
    }
}

/**
 * Represents an organization entity, often extracted from Creator, Contributor, or AddlAuth fields
 * when the value doesn't parse as a Person. Contains the organization's name.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Organization extends BaseEntity {
    // Initializer block sets the specific entity type for Organization instances.
    { entityType = "Agent:Organization"; }

    /**
     * The name of the organization. Mapped to lowercase "name" in JSON for consistency with example.
     */
    @JsonProperty("name") // Lowercase 'n' as specified
    public String name;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Organization to another object for equality based on ontology and name.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same organization, {@code false} otherwise.
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Organization that = (Organization) o;
        return Objects.equals(ontology, that.ontology) &&
                Objects.equals(name, that.name);
    }

    /**
     * Generates a hash code for this Organization based on ontology and name.
     * Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(ontology, name);
    }
}

/**
 * Represents a category or subject classification, derived from the 'SubjectTop' CSV field.
 * Does not include an 'ontology' field. Contains the category name.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Category extends BaseEntity {
    // Initializer block sets the specific entity type for Category instances.
    { entityType = "ContentDescription:Category"; }

    /**
     * The name of the category. Mapped to "name" in JSON.
     */
    @JsonProperty("name")
    public String name;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Category to another object for equality based solely on the name.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same category name, {@code false} otherwise.
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Category category = (Category) o;
        return Objects.equals(name, category.name);
    }

    /**
     * Generates a hash code for this Category based on its name.
     * Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}

/**
 * Represents the material an item is made of, derived from the 'Material' CSV field
 * (e.g., 'papr' -> 'paper', 'digi' -> 'digital').
 * Does not include an 'ontology' field. Contains the material name.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Material extends BaseEntity{
    // Initializes the specific entity type for Material instances.
    { entityType = "Material"; }

    /**
     * The name of the material (e.g., "paper", "digital", "mix"). Mapped to "name" in JSON.
     */
    @JsonProperty("name")
    public String name;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Material to another object for equality based solely on the name.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same material name, {@code false} otherwise.
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Material material = (Material) o;
        return Objects.equals(name, material.name);
    }

    /**
     * Generates a hash code for this Material based on its name.
     * Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}


/**
 * Represents a relationship between two entities (Subject and Object) with a specific Type.
 * Includes fields identifying the subject, object, their types, and potentially a related number (IdNum).
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Relationship extends BaseEntity {
    @JsonIgnore
    public String entityType;

    /**
     * The type of the relationship (e.g., "belongsTo", "madeOf", "developed", "produced", "describe", "collaborated").
     */
    @JsonProperty("Type")
    public String type;
    /**
     * The identifier (often name or title) of the subject entity in the relationship.
     */
    @JsonProperty("Subject")
    public String subject;
    /**
     * The type of the subject entity (e.g., "Collection", "Item", "Person", "Organization", "Category").
     */
    @JsonProperty("SubjectType")
    public String subjectType;
    /**
     * The identifier (often title or name) of the object entity in the relationship.
     * Note: "Object" is a reserved keyword in Java, but acceptable as a field name.
     */
    @JsonProperty("Object") // Using "Object" as field name is acceptable
    public String object;
    /**
     * The type of the object entity (e.g., "Item", "Document", "Artifact", "Material").
     */
    @JsonProperty("ObjectType")
    public String objectType;
    /**
     * An associated number, typically the 'IdNum' from the CSV, primarily used in 'belongsTo' relationships.
     * Can be null for other relationship types. Mapped to "number" in JSON.
     */
    @JsonProperty("number")
    public String number;

    // Constructors, getters, setters omitted.

    /**
     * Compares this Relationship to another object for equality based on all fields, including BaseEntity fields.
     * Ensures uniqueness when adding relationships to a Set.
     * @param o The object to compare with.
     * @return {@code true} if the objects represent the same relationship, {@code false} otherwise.
     */
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

    /**
     * Generates a hash code for this Relationship based on all fields, including BaseEntity fields.
     * Consistent with {@link #equals(Object)}.
     * @return The hash code value for this object.
     */
    @Override
    public int hashCode() {
        return Objects.hash(ontology, type, subject, subjectType, object, objectType, number);
    }
}


// --- Classes for JSON Output Structure ---

/**
 * Simple container for the collection information, intended to be nested within the {@link Entities} object.
 */
class CollectionInfo extends BaseEntity{
    // Initializes the specific entity type for CollectionInfo instances.
    { entityType = "Collection"; }

    /**
     * The name of the collection, hardcoded to "HCLE". Mapped to "name" in JSON.
     */
    @JsonProperty("name")
    public String name = "HCLE";

    public CollectionInfo() {
        this.entityType = "Collection";
        this.ontology = "general";
    }
}

/**
 * Container class grouping all extracted entities by their type AND including the collection information
 * for the final JSON output structure.
 */
class Entities {
    /**
     * Information about the collection, nested under the "Collection" key within "Entities".
     * Changed to a List to match the desired JSON output format.
     */
    @JsonProperty("Collection")
    public List<CollectionInfo> collection;

    /** List of generic Artifact entities (those not classified as Item or Document). */
    @JsonProperty("Artifacts")
    public List<Artifact> artifacts;
    /** List of Item entities. */
    @JsonProperty("Items")
    public List<Item> items;
    /** List of Document entities. */
    @JsonProperty("Documents")
    public List<Document> documents;
    /** List of Person entities. */
    @JsonProperty("People")
    public List<Person> people;
    /** List of Organization entities. */
    @JsonProperty("Organizations")
    public List<Organization> organizations;
    /** List of Category entities (derived from SubjectTop). */
    @JsonProperty("Categories")
    public List<Category> categories;
    /** List of Material entities. */
    @JsonProperty("Materials")
    public List<Material> materials;

    /**
     * Constructs an Entities object. It converts the provided Sets of unique entities (gathered during parsing)
     * into Lists suitable for JSON serialization. The {@link CollectionInfo} is initialized internally as a List.
     *
     * @param artifactsSet     Set of unique {@link Artifact} entities.
     * @param itemsSet         Set of unique {@link Item} entities.
     * @param documentsSet     Set of unique {@link Document} entities.
     * @param peopleSet        Set of unique {@link Person} entities.
     * @param organizationsSet Set of unique {@link Organization} entities.
     * @param categoriesSet    Set of unique {@link Category} entities.
     * @param materialsSet     Set of unique {@link Material} entities.
     */
    public Entities(Set<Artifact> artifactsSet, Set<Item> itemsSet, Set<Document> documentsSet,
                    Set<Person> peopleSet, Set<Organization> organizationsSet,
                    Set<Category> categoriesSet, Set<Material> materialsSet) {
        this.collection = new ArrayList<>();
        this.collection.add(new CollectionInfo()); // Initialize collection as a list containing one CollectionInfo

        this.artifacts = new ArrayList<>(artifactsSet);
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
 * Contains the main "Entities" object (which includes collection info and entity lists)
 * and the top-level "Relationships" list.
 */
class JsonOutput {
    /**
     * The main container for collection information and lists of all extracted entities, grouped by type.
     * Mapped to the "Entities" key in the root JSON object.
     */
    @JsonProperty("Entities")
    public Entities entities;

    /**
     * List of all relationships connecting the entities.
     * Mapped to the "Relationships" key in the root JSON object.
     * Relationships missing essential fields might be filtered out before serialization.
     */
    @JsonProperty("Relationships")
    public List<Relationship> relationships;

    /**
     * Constructs the final JSON output structure.
     * It takes the populated {@link Entities} object and the set of unique {@link Relationship} objects.
     * It filters the relationships to include only those that have non-null and non-empty values
     * for essential fields (ontology, type, subject, subjectType, object, objectType) before
     * assigning them to the {@code relationships} list. The 'number' field is allowed to be null.
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
                        // 'number' can be null (e.g., for madeOf, describe relationships), so it's not part of the filter here.
                )
                .collect(Collectors.toList());
    }
}


// --- Main Converter Class ---

/**
 * Main class responsible for converting data from a CSV file (e.g., HCLEcatalog.csv) into a structured JSON format.
 * It reads the CSV row by row, attempts to parse each row into appropriate entity types (Item, Document, Artifact,
 * Person, Organization, Category, Material), creates corresponding objects using the defined POJO classes,
 * establishes relationships between them based on predefined logic, collects unique entities and relationships
 * using Sets, and finally writes the aggregated data into a JSON file (e.g., data.json) according to the
 * {@link JsonOutput} structure. A log file (e.g., parsing.log) is generated to track the processing status
 * and potential errors encountered for each CSV row.
 */
public class CsvToJsonConverter {

    // --- Regex Patterns ---
    /**
     * Regex to identify a string likely representing a single person's name in a standard format.
     * Matches common titles (Dr., Prof.), capitalized first/last names, optional middle name/initial, and common suffixes (Jr., Sr.).
     * Used for identifying potential 'Person' entities in fields like 'Creator'.
     */
    private static final Pattern PERSON_REGEX_STRICT = Pattern.compile(
            "^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+\\s[A-Z][a-z]+(?:\\s[A-Z][a-z]+)?(?:,?\\s(?:Jr\\.|Sr\\.|III))?$"
    );

    /**
     * Regex to identify a string potentially containing a list of person names,
     * separated by common delimiters (commas, semicolons, 'and', '{@literal &}'). More lenient than {@link #PERSON_REGEX_STRICT}.
     * Used for parsing fields like 'Contributor' and 'AddlAuth' which might contain multiple names.
     */
    private static final Pattern PERSON_REGEX_LIST = Pattern.compile(
            "^(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)+(?:\\s(?:Jr\\.|Sr\\.|III))?(?:(?:\\s*(?:,|;|\\band\\b|&)\\s*)(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*(?:\\s(?:Jr\\.|Sr\\.|III))?)*$"
    );

    /**
     * Regex defining the delimiters used to split strings containing multiple names or identifiers.
     * Matches whitespace around ',', ';', 'and', '{@literal &}'. Used in conjunction with {@link String#split(String)}.
     */
    private static final Pattern NAME_SPLIT_DELIMITER = Pattern.compile("\\s*(?:,|;|\\band\\b|&)\\s*");

    /**
     * Main entry point of the CSV to JSON conversion application.
     * Defines file paths, initializes sets for storing unique entities and relationships,
     * reads and parses the CSV file record by record, processes each record to create entities
     * and relationships, and finally serializes the collected data into the output JSON file.
     * Handles potential {@link IOException} during file operations.
     *
     * @param args Command line arguments (not currently used).
     */
    public static void main(String[] args) {

        // --- Configuration ---
        String csvFilePath = "src/main/resources/HCLEcatalog.csv"; // Path to the input CSV file
        String logFilePath = "src/main/output/parsing.log";     // Path for the output log file
        String jsonFilePath = "src/main/output/data.json";    // Path for the output JSON file

        // --- Data Structures ---
        // Using Sets ensures that we store only unique entities and relationships,
        // relying on the equals() and hashCode() implementations in the entity classes.
        Set<Item> setOfItems = new HashSet<>();
        Set<Document> setOfDocuments = new HashSet<>();
        Set<Artifact> setOfArtifacts = new HashSet<>(); // For Artifacts that are neither Item nor Document specifically
        Set<Material> setOfMaterialTypes = new HashSet<>();
        Set<Organization> setOfOrganizations = new HashSet<>();
        Set<Relationship> setOfRelationships = new HashSet<>();
        Set<Person> setOfPeople = new HashSet<>();
        Set<Category> setOfContentDescriptions = new HashSet<>(); // Corresponds to 'SubjectTop'

        // --- File Processing ---
        // Using try-with-resources ensures that the Reader, CSVParser, and PrintWriter are automatically closed.
        try (
                Reader reader = Files.newBufferedReader(Paths.get(csvFilePath), StandardCharsets.UTF_8);
                // Configure the CSV parser: Use default comma delimiter, expect a header row (case-insensitive), and trim whitespace from values.
                CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT
                        .withHeader()           // Treat the first row as headers
                        .withIgnoreHeaderCase() // Match headers regardless of case (e.g., "IdNum" vs "idnum")
                        .withTrim());          // Remove leading/trailing whitespace from parsed values
                PrintWriter logWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(logFilePath), StandardCharsets.UTF_8)) // Open log file in UTF-8
        ) {

            int rowIndex = 0; // Keep track of the data row number (starting from 1 after the header) for logging
            // Iterate over each record (row) in the CSV file
            for (CSVRecord csvRecord : csvParser) {
                rowIndex++;
                // --- Basic Row Validation & Data Extraction ---
                String idNum = getRecordValue(csvRecord, "IdNum"); // Get the primary identifier

                // Skip rows that lack a valid IdNum, logging an error.
                if (isNullOrEmpty(idNum)) {
                    logWriter.printf("Row %d ERROR -> IdNum is null or empty%n", rowIndex);
                    continue; // Move to the next row
                }

                // Load all columns for the current row into a Map for easy access by header name.
                // Also, perform basic cleaning (remove potential surrounding quotes, though Commons CSV usually handles this).
                Map<String, String> rowData = new HashMap<>();
                for (String header : csvParser.getHeaderMap().keySet()) { // Iterate through all expected headers
                    String value = getRecordValue(csvRecord, header);
                    if (value != null) {
                        rowData.put(header, value.replace("\"", "")); // Store cleaned value
                    } else {
                        rowData.put(header, null); // Store null if value was missing
                    }
                }

                // --- Determine Entity Type (Document, Item, or generic Artifact) ---
                String entityType = "Artifact"; // Assume generic Artifact by default

                // Check for Document characteristics first: presence of ToC, Extent, SerialNum, or BibCit.
                String toc = rowData.get("ToC");
                String extent = rowData.get("Extent");
                String serialNum = rowData.get("SerialNum");
                String bibCit = rowData.get("BibCit");
                boolean isDocument = !isNullOrNone(toc) || !isNullOrNone(extent) || !isNullOrNone(serialNum) || !isNullOrNone(bibCit);

                if (isDocument) {
                    entityType = "Document";
                } else {
                    // If it's not a Document, check if it's an Item.
                    // An Item must have a PartNum that is present and not just a single digit.
                    String partNum = rowData.get("PartNum");
                    if (!isNullOrNone(partNum) && !partNum.matches("^\\d$")) { // Check if PartNum exists and is not a single digit
                        entityType = "Item";
                    }
                    // If neither Document nor Item criteria are met, it remains an "Artifact".
                }

                // --- Check Mandatory Fields (Title) ---
                String title = rowData.get("Title");
                if (isNullOrNone(title)) {
                    logWriter.printf("Row %d ERROR -> Title is null or None. Skipping row.%n", rowIndex);
                    continue; // Skip this row if the essential Title field is missing
                }

                logWriter.printf("Row %d -> Type: %s -> ID: %s, Title: %s -> Processing...%n", rowIndex, entityType, idNum, title); // Log progress

                // --- Create the Core Entity Object (Document, Item, or Artifact) ---
                Artifact currentEntity; // Use the base class type for polymorphism

                if ("Document".equals(entityType)) {
                    Document doc = new Document();
                    doc.title = title;
                    // Populate Document-specific fields if they have values
                    if (!isNullOrNone(toc)) doc.toC = toc;
                    if (!isNullOrNone(extent)) doc.extent = extent;
                    if (!isNullOrNone(serialNum)) doc.serialNum = serialNum;
                    if (!isNullOrNone(bibCit)) doc.bibCit = bibCit;

                    // Handle 'Created' date: use "Created" field, fallback to "DateCR" if "Created" is missing/null/None
                    String created = rowData.get("Created");
                    if (isNullOrNone(created)) {
                        created = rowData.get("DateCR"); // Fallback
                    }
                    if (!isNullOrNone(created)) {
                        doc.created = created;
                    }

                    // Handle 'Copyrighted' field: convert 'y'/'n'/'0' to Boolean true/false, leave null otherwise
                    String copyrightedStr = rowData.get("Copyrighted");
                    if (!isNullOrNone(copyrightedStr)) {
                        if ("y".equalsIgnoreCase(copyrightedStr.trim())) {
                            doc.copyrighted = true;
                        } else if ("n".equalsIgnoreCase(copyrightedStr.trim()) || "0".equals(copyrightedStr.trim())) {
                            doc.copyrighted = false;
                        }
                        // Any other value (or if isNullOrNone was true) leaves doc.copyrighted as null
                    }
                    currentEntity = doc; // Assign the specific Document object

                } else if ("Item".equals(entityType)) {
                    Item item = new Item();
                    item.title = title;
                    item.partNum = rowData.get("PartNum"); // PartNum is guaranteed non-null/non-single-digit here

                    // Populate Item-specific fields
                    String conditionNts = rowData.get("ConditionNts");
                    if (!isNullOrNone(conditionNts)) {
                        item.conditionNts = conditionNts;
                    }
                    currentEntity = item; // Assign the specific Item object

                } else { // Default case: Generic Artifact
                    Artifact artifact = new Artifact();
                    artifact.title = title;
                    // No specific fields beyond the common ones handled next
                    currentEntity = artifact; // Assign the generic Artifact object
                }

                // --- Populate Common Artifact Fields (apply to all types: Document, Item, Artifact) ---
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

                // --- Add the created Core Entity to its respective Set (handles uniqueness) ---
                if (currentEntity instanceof Document) {
                    setOfDocuments.add((Document) currentEntity);
                } else if (currentEntity instanceof Item) {
                    setOfItems.add((Item) currentEntity);
                } else {
                    // This catches Artifacts that didn't meet Document or Item criteria
                    setOfArtifacts.add(currentEntity);
                }

                // --- Process Related Entities (Material, Category, Creator, Contributors) and Create Relationships ---

                // 1. Material Entity (from "Material" field: papr, digi, mix)
                String materialStr = rowData.get("Material");
                Material currentMaterial = null; // To hold the Material entity if created for this row
                if (materialStr != null) {
                    String materialName = null;
                    String trimmedMaterial = materialStr.trim();
                    // Map standard codes to full names
                    if ("papr".equalsIgnoreCase(trimmedMaterial)) materialName = "paper";
                    else if ("digi".equalsIgnoreCase(trimmedMaterial)) materialName = "digital";
                    else if ("mix".equalsIgnoreCase(trimmedMaterial)) materialName = "mix";

                    if (materialName != null) {
                        currentMaterial = new Material();
                        currentMaterial.name = materialName;
                        setOfMaterialTypes.add(currentMaterial); // Add to the set of unique materials found
                    } else if (!trimmedMaterial.isEmpty() && !"none".equalsIgnoreCase(trimmedMaterial) && !"null".equalsIgnoreCase(trimmedMaterial)) {
                        logWriter.printf("Row %d WARNING -> Unrecognized Material code: '%s'%n", rowIndex, trimmedMaterial);
                    }
                }

                // 2. Category Entity (from "SubjectTop" field)
                String subjectTop = rowData.get("SubjectTop");
                Category currentCategory = null; // To hold the Category entity if created for this row
                if (!isNullOrNone(subjectTop)) {
                    currentCategory = new Category();
                    currentCategory.name = subjectTop.trim(); // Use the value directly as category name
                    setOfContentDescriptions.add(currentCategory); // Add to the set of unique categories found
                }

                // 3. Creator Entity (Person or Organization from "Creator" field)
                String creatorStr = rowData.get("Creator");
                Person creatorPerson = null;        // To hold the Person if creator is identified as such
                Organization creatorOrg = null;     // To hold the Organization if creator is identified as such
                boolean isCreatorPerson = false;    // Flag

                if (!isNullOrNone(creatorStr)) {
                    String trimmedCreator = creatorStr.trim();
                    // Attempt to match the strict person name pattern first
                    if (PERSON_REGEX_STRICT.matcher(trimmedCreator).matches()) {
                        creatorPerson = parsePerson(trimmedCreator); // Try parsing into Name/Surname
                        if (creatorPerson != null) {
                            setOfPeople.add(creatorPerson); // Add unique person to set
                            isCreatorPerson = true;
                        }
                        // If parsePerson returns null despite regex match, it logs internally. We treat it as non-person below.
                    }
                    // If it wasn't successfully parsed as a strict Person, treat it as an Organization.
                    if (!isCreatorPerson) {
                        creatorOrg = new Organization();
                        creatorOrg.name = trimmedCreator; // Use the raw string as the organization name
                        setOfOrganizations.add(creatorOrg); // Add unique organization to set
                    }
                }

                // --- Create Relationships ---

                // Relationship 1: "belongsTo" (Collection -> Entity)
                // Every valid entity from the CSV belongs to the main 'HCLE' collection.
                Relationship relBelongs = new Relationship();
                relBelongs.type = "belongsTo";
                relBelongs.subject = "HCLE";        // Subject is the collection name
                relBelongs.subjectType = "Collection";
                // Object is the entity's identifier (Title or Title + PartNum for Items)
                relBelongs.object = currentEntity.title;
                if (currentEntity instanceof Item) {
                    // Append PartNum to title for uniqueness if it's an Item
                    relBelongs.object += " " + ((Item) currentEntity).partNum;
                }
                relBelongs.objectType = currentEntity.entityType; // Type of the object (Item, Document, Artifact)
                relBelongs.number = idNum;             // Include the original IdNum in this relationship
                setOfRelationships.add(relBelongs);    // Add unique relationship to set

                // Relationship 2: "madeOf" (Item -> Material)
                // Only created for Items that have a valid Material identified in this row.
                if (currentEntity instanceof Item && currentMaterial != null) {
                    Relationship relMadeOf = new Relationship();
                    relMadeOf.type = "madeOf";
                    // Subject is the Item identifier (Title + PartNum)
                    relMadeOf.subject = currentEntity.title + " " + ((Item) currentEntity).partNum;
                    relMadeOf.subjectType = currentEntity.entityType; // Should be "Item"
                    relMadeOf.object = currentMaterial.name;         // Object is the material name
                    relMadeOf.objectType = "Material";
                    setOfRelationships.add(relMadeOf);
                }

                // Relationship 3: "describe" (Category -> Entity)
                // Only created for non-Items (Documents/Artifacts) that have a Category (SubjectTop) identified.
                if (!(currentEntity instanceof Item) && currentCategory != null) {
                    Relationship relDescribe = new Relationship();
                    relDescribe.type = "describe";
                    relDescribe.subject = currentCategory.name; // Subject is the Category name
                    relDescribe.subjectType = "Category";
                    relDescribe.object = currentEntity.title;   // Object is the entity title (Document or Artifact)
                    relDescribe.objectType = currentEntity.entityType;
                    setOfRelationships.add(relDescribe);
                }

                // Relationship 4: Creator Relationships ("developed" by Person / "produced" by Org)
                // Only created for non-Items (Documents/Artifacts) that have a Creator identified.
                if (!(currentEntity instanceof Item)) { // Logic applies only to Documents and generic Artifacts
                    if (isCreatorPerson && creatorPerson != null) {
                        // If Creator was identified and parsed as a Person
                        Relationship relDev = new Relationship();
                        relDev.type = "developed"; // Relationship type for Person creator
                        relDev.subject = creatorPerson.name + " " + creatorPerson.surname; // Full name as subject ID
                        relDev.subjectType = "Person";
                        relDev.object = currentEntity.title; // Entity title as object ID
                        relDev.objectType = currentEntity.entityType; // "Document" or "Artifact"
                        setOfRelationships.add(relDev);
                    } else if (creatorOrg != null) {
                        // If Creator was identified as an Organization (or failed Person parsing)
                        Relationship relProd = new Relationship();
                        relProd.type = "produced"; // Relationship type for Organization creator
                        relProd.subject = creatorOrg.name; // Organization name as subject ID
                        relProd.subjectType = "Organization";
                        relProd.object = currentEntity.title; // Entity title as object ID
                        relProd.objectType = currentEntity.entityType; // "Document" or "Artifact"
                        setOfRelationships.add(relProd);
                    }
                }

                // Relationship 5 & 6: Contributor / Additional Author Relationships
                // Use the helper method to handle fields that might contain single or multiple Persons/Organizations.
                // For "Contributor", the base relationship is "developed" (becomes "produced" for Orgs).
                processContributorField(rowData.get("Contributor"), "developed", currentEntity,
                        setOfPeople, setOfOrganizations, setOfRelationships, logWriter, rowIndex);
                // For "AddlAuth", the base relationship is "collaborated".
                processContributorField(rowData.get("AddlAuth"), "collaborated", currentEntity,
                        setOfPeople, setOfOrganizations, setOfRelationships, logWriter, rowIndex);

                logWriter.printf("Row %d -> Completed processing.%n", rowIndex);

            } // End of loop iterating through CSV records

            logWriter.printf("Finished processing %d data rows.%n", rowIndex);
            logWriter.printf("Found %d unique Items, %d unique Documents, %d unique Artifacts.%n",
                    setOfItems.size(), setOfDocuments.size(), setOfArtifacts.size());
            logWriter.printf("Found %d unique People, %d unique Organizations.%n",
                    setOfPeople.size(), setOfOrganizations.size());
            logWriter.printf("Found %d unique Categories, %d unique Materials.%n",
                    setOfContentDescriptions.size(), setOfMaterialTypes.size());
            logWriter.printf("Created %d unique Relationships.%n", setOfRelationships.size());


            // --- Prepare Final Data Structure for JSON Output ---
            // Create the Entities object, passing the sets of unique entities. It handles conversion to lists.
            Entities entitiesContainer = new Entities(
                    setOfArtifacts, setOfItems, setOfDocuments,
                    setOfPeople, setOfOrganizations,
                    setOfContentDescriptions, setOfMaterialTypes
            );
            // Create the top-level JsonOutput object, passing the entities container and the set of relationships.
            // The JsonOutput constructor handles filtering invalid relationships.
            JsonOutput outputData = new JsonOutput(entitiesContainer, setOfRelationships);

            // --- Write JSON Output File ---
            ObjectMapper objectMapper = new ObjectMapper();
            // Configure Jackson for pretty-printing (indented output)
            objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
            // Exclude null fields (already handled by @JsonInclude on classes, but good practice)
            // objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL); // Redundant if classes use annotation

            try (PrintWriter jsonWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(jsonFilePath), StandardCharsets.UTF_8))) { // Use UTF-8 for JSON
                objectMapper.writeValue(jsonWriter, outputData); // Serialize the Java object structure to JSON
            }

            System.out.println("CSV to JSON conversion complete.");
            System.out.println("Log file generated at: " + logFilePath);
            System.out.println("JSON output generated at: " + jsonFilePath);

        } catch (IOException e) {
            // Handle potential errors during file reading/writing or CSV parsing
            System.err.println("An error occurred during processing: " + e.getMessage());
            e.printStackTrace(); // Print stack trace for debugging
        } catch (Exception e) {
            // Catch any other unexpected exceptions during processing
            System.err.println("An unexpected error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    } // End of main method

    // --- Helper Methods ---

    /**
     * Safely retrieves a value from a {@link CSVRecord} using the header name.
     * Checks if the header exists in the record's map before attempting to get the value,
     * preventing {@link IllegalArgumentException} if the header is missing.
     *
     * @param record     The {@code CSVRecord} object representing the current row.
     * @param headerName The case-insensitive name of the header/column to retrieve the value for.
     * @return The string value from the specified column (trimmed by the parser configuration),
     *         or {@code null} if the column header is not found in the record or if the value is missing.
     */
    private static String getRecordValue(CSVRecord record, String headerName) {
        try {
            // isMapped checks if the header (case-insensitively due to parser config) exists for this record
            if (record.isMapped(headerName)) {
                return record.get(headerName); // Retrieve the value (already trimmed)
            } else {
                // This case might indicate an issue with the CSV file or header definition
                // System.err.printf("Warning: Header '%s' not found in CSV record map.%n", headerName);
                return null; // Header not present for this record
            }
        } catch (IllegalArgumentException e) {
            // Should ideally not be reached if isMapped works correctly, but acts as a safeguard.
            System.err.printf("Warning: Error retrieving value for header '%s'. %s%n", headerName, e.getMessage());
            return null;
        }
    }


    /**
     * Checks if a string is effectively null or empty, also considering common string representations of null
     * like "None" or "NULL" (case-insensitive) after trimming whitespace.
     *
     * @param s The string to check.
     * @return {@code true} if the string is null, empty/whitespace-only, or equals "None" or "NULL" (case-insensitive),
     *         {@code false} otherwise.
     */
    private static boolean isNullOrNone(String s) {
        if (s == null) {
            return true;
        }
        String trimmed = s.trim();
        return trimmed.isEmpty() || "None".equalsIgnoreCase(trimmed) || "NULL".equalsIgnoreCase(trimmed);
    }

    /**
     * Checks if a string is null or consists only of whitespace characters after trimming.
     * This is a simpler check than {@link #isNullOrNone(String)}.
     *
     * @param s The string to check.
     * @return {@code true} if the string is null or its trimmed version is empty, {@code false} otherwise.
     */
    private static boolean isNullOrEmpty(String s) {
        return s == null || s.trim().isEmpty();
    }

    /**
     * Processes a CSV field (like "Contributor" or "AddlAuth") that might contain one or more names,
     * potentially a mix of persons and organizations, separated by delimiters.
     * It attempts to parse each delimited part as a {@link Person}. If successful, a Person entity and
     * the corresponding relationship are created. If parsing fails, or if the input doesn't look like
     * a list of persons, it treats the part(s) as {@link Organization}(s) and creates entities and relationships accordingly.
     * Logs warnings for parsing issues.
     *
     * @param fieldContent          The raw string content from the CSV field.
     * @param relationshipBaseType  The base type for the relationship (e.g., "developed", "collaborated"). This is adapted to "produced" for organizations if base is "developed".
     * @param currentEntity         The core entity (Item, Document, Artifact) that is the object of the relationship.
     * @param peopleSet             The set to add newly identified unique {@link Person} entities to.
     * @param orgSet                The set to add newly identified unique {@link Organization} entities to.
     * @param relSet                The set to add newly created unique {@link Relationship} objects to.
     * @param logWriter             The {@link PrintWriter} for logging warnings or errors.
     * @param rowIndex              The current CSV row index for logging context.
     */
    private static void processContributorField(String fieldContent, String relationshipBaseType,
                                                Artifact currentEntity,
                                                Set<Person> peopleSet, Set<Organization> orgSet, Set<Relationship> relSet,
                                                PrintWriter logWriter, int rowIndex) {

        // Ignore if the field is effectively empty or null
        if (isNullOrNone(fieldContent)) {
            return;
        }

        String content = fieldContent.trim();
        // Check if the content roughly matches the pattern for a list of people
        boolean looksLikePersonList = PERSON_REGEX_LIST.matcher(content).matches();

        if (looksLikePersonList) {
            // If it looks like a list, split it by defined delimiters (",", ";", "and", "&")
            String[] potentialNames = NAME_SPLIT_DELIMITER.split(content);
            for (String nameStr : potentialNames) {
                String trimmedName = nameStr.trim();
                if (trimmedName.isEmpty()) continue; // Skip empty segments resulting from split

                Person person = parsePerson(trimmedName); // Attempt to parse the segment as a Person
                if (person != null) {
                    // Successfully parsed as a Person
                    boolean added = peopleSet.add(person); // Add unique person to set
                    if(added) { // Log only if it's a newly discovered person
                        logWriter.printf("Row %d -> Identified Person: %s %s from field '%s'%n", rowIndex, person.name, person.surname, fieldContent);
                    }
                    // Create the relationship (Person -> developed/collaborated -> Entity)
                    addPersonRelationship(person, relationshipBaseType, currentEntity, relSet);
                } else {
                    // If parsing as a person failed (parsePerson returned null, logged internally),
                    // treat this specific segment as an Organization as a fallback.
                    logWriter.printf("Row %d -> Treating '%s' (from '%s') as Organization after failed person parse.%n", rowIndex, trimmedName, fieldContent);
                    addOrganizationAndRelationship(trimmedName, relationshipBaseType, currentEntity, orgSet, relSet, logWriter, rowIndex, false); // Assume not new for logging
                }
            }
        } else {
            // If the entire string doesn't match the person list pattern,
            // treat the whole content as a single Organization name.
            logWriter.printf("Row %d -> Treating '%s' as a single Organization (did not match person list pattern).%n", rowIndex, content);
            addOrganizationAndRelationship(content, relationshipBaseType, currentEntity, orgSet, relSet, logWriter, rowIndex, true); // Assume new for logging
        }
    }

    /**
     * Creates a {@link Relationship} linking a {@link Person} to the {@code currentEntity}.
     *
     * @param person               The subject Person entity.
     * @param relationshipType     The type of the relationship (e.g., "developed", "collaborated").
     * @param currentEntity        The object Artifact/Item/Document entity.
     * @param relSet               The set to add the new relationship to.
     */
    private static void addPersonRelationship(Person person, String relationshipType, Artifact currentEntity, Set<Relationship> relSet) {
        Relationship rel = new Relationship();
        rel.type = relationshipType;
        rel.subject = person.name + " " + person.surname;
        rel.subjectType = "Person";
        rel.object = currentEntity.title;
        if (currentEntity instanceof Item) { // Append PartNum for Items
            rel.object += " " + ((Item) currentEntity).partNum;
        }
        rel.objectType = currentEntity.entityType;
        relSet.add(rel); // Add unique relationship
    }


    /**
     * Creates an {@link Organization} entity from a name string, adds it to the provided set (if unique),
     * and creates the corresponding {@link Relationship} linking the organization to the {@code currentEntity}.
     * Adjusts the relationship type from "developed" to "produced" for organizations.
     * Logs the identification of a new organization.
     *
     * @param orgName               The name of the organization.
     * @param relationshipBaseType  The base type for the relationship ("developed", "collaborated", etc.).
     * @param currentEntity         The entity the organization is related to (the object of the relationship).
     * @param orgSet                The set of unique Organizations to add the new one to.
     * @param relSet                The set of unique Relationships to add the new one to.
     * @param logWriter             The PrintWriter for logging.
     * @param rowIndex              The current row index for logging context.
     * @param logAsNew              Flag to indicate if finding this org name should be logged as 'newly identified'.
     */
    private static void addOrganizationAndRelationship(String orgName, String relationshipBaseType,
                                                       Artifact currentEntity, Set<Organization> orgSet, Set<Relationship> relSet,
                                                       PrintWriter logWriter, int rowIndex, boolean logAsNew) {
        // Create and attempt to add the Organization entity to the set
        Organization org = new Organization();
        org.name = orgName;
        boolean added = orgSet.add(org); // Returns true if the org was not already in the set

        if (added && logAsNew) { // Log only if it's newly added and flagged for logging
            logWriter.printf("Row %d -> Identified Organization: %s%n", rowIndex, org.name);
        }

        // Create the relationship (Organization -> produced/collaborated -> Entity)
        Relationship rel = new Relationship();
        // If the base relationship type is 'developed', change it to 'produced' for Organizations.
        // Otherwise, use the provided base type (e.g., 'collaborated').
        rel.type = relationshipBaseType.equals("developed") ? "produced" : relationshipBaseType;
        rel.subject = org.name;
        rel.subjectType = "Organization";
        rel.object = currentEntity.title;
        if (currentEntity instanceof Item) { // Append PartNum for Items
            rel.object += " " + ((Item) currentEntity).partNum;
        }
        rel.objectType = currentEntity.entityType;
        relSet.add(rel); // Add the unique relationship
    }


    /**
     * Attempts to parse a single string potentially representing a person's full name into a {@link Person} object
     * with separate {@code name} (first) and {@code surname} (last) fields.
     * It first cleans the input string by removing common titles (Dr., Prof., Mr., Ms., Sir) and suffixes (Jr., Sr., III).
     * Then, it splits the cleaned name by whitespace. If there are at least two resulting parts,
     * the first part is assigned to {@code person.name} and the remaining parts (joined by spaces)
     * are assigned to {@code person.surname}.
     * Logs a warning if parsing fails to produce at least two name parts.
     *
     * @param nameStr The input string potentially representing a person's name (e.g., "Dr. John A. Smith, Jr.").
     * @return A {@link Person} object with {@code name} and {@code surname} populated if parsing is successful
     *         (at least two name parts found after cleaning). Returns {@code null} if the string cannot be
     *         reliably parsed into a first and last name (e.g., empty after cleaning, only one part found),
     *         indicating it should likely be treated as an organization or logged as unparseable.
     */
    private static Person parsePerson(String nameStr) {
        if (isNullOrEmpty(nameStr)) {
            return null;
        }
        // Clean titles from the start and suffixes from the end. Handles optional comma before suffix. Trim result.
        String cleanedName = nameStr.replaceAll("^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)|((?:,\\s*)?(?:Jr\\.|Sr\\.|III))$", "").trim();

        // If cleaning resulted in an empty string, cannot parse.
        if (cleanedName.isEmpty()) {
            // This might happen if the original string was just a title or suffix.
            // System.err.printf("Warning: Name string '%s' became empty after cleaning titles/suffixes.%n", nameStr);
            return null;
        }

        // Split the cleaned name by one or more whitespace characters.
        String[] nameParts = cleanedName.split("\\s+");

        if (nameParts.length >= 2) {
            // We have at least a potential first name and last name part.
            Person person = new Person();
            person.name = nameParts[0]; // First part is assigned as the 'Name' (first name).
            // Join the second part through the end with spaces to form the 'Surname' (last name + any middle parts).
            person.surname = String.join(" ", Arrays.copyOfRange(nameParts, 1, nameParts.length));
            return person;
        } else {
            // If only one part remains after cleaning (e.g., "Smith", "Cher"), we cannot reliably separate first/last names
            // based on the current simple logic. Log this situation.
            System.err.printf("Warning: Could not parse '%s' (cleaned: '%s') into Name/Surname (only %d part found). Treating as non-person.%n",
                    nameStr, cleanedName, nameParts.length);
            return null; // Indicate parsing failure. Caller should handle this (e.g., treat as Organization).
        }
    }

} // End CsvToJsonConverter class