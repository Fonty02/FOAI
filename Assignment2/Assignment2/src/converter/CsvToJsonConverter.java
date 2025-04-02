// --- START OF FILE CsvToJsonConverter.java ---

package converter;

// Added JsonIgnore import
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;


/**
 * Abstract base class for entities. EntityType helps determine the node label.
 */
abstract class BaseEntity {
    // This field is used internally, not intended for JSON output property.
    public String entityType = "";

    @Override
    public abstract boolean equals(Object o);
    @Override
    public abstract int hashCode();

    /**
     * Gets the node label based on the entityType.
     * This method is ignored during JSON serialization/conversion.
     * @return The string label for the Neo4j node.
     */
    @JsonIgnore // Ensures Jackson doesn't create a "nodeLabel" property from this getter
    public String getNodeLabel() {
        if (entityType == null) return "Unknown";
        switch (entityType) {
            case "Agent:Person": return "Person";
            case "Agent:Organization": return "Organization";
            case "ContentDescription:Category": return "Category";
            default: return entityType;
        }
    }
}

/**
 * Represents a general artifact entity. Base class for Item and Document.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Artifact extends BaseEntity {
    { entityType = "Artifact"; }

    @JsonProperty("title")
    public String title;
    @JsonProperty("description")
    public String description;
    @JsonProperty("descComment")
    public String descComment;
    @JsonProperty("wherMade")
    public String wherMade;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Artifact artifact = (Artifact) o;
        return Objects.equals(title, artifact.title);
    }

    @Override
    public int hashCode() {
        return Objects.hash(title);
    }
}

/**
 * Represents an Item. Inherits from Artifact.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Item extends Artifact {
    { entityType = "Item"; }

    @JsonProperty("partNum")
    public String partNum;
    @JsonProperty("conditionNts")
    public String conditionNts;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Item item = (Item) o;
        return Objects.equals(title, item.title) &&
                Objects.equals(partNum, item.partNum);
    }

    @Override
    public int hashCode() {
        return Objects.hash(title, partNum);
    }
}

/**
 * Represents a Document. Inherits from Artifact.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Document extends Artifact {
    { entityType = "Document"; }

    @JsonProperty("toc")
    public String toC;
    @JsonProperty("extent")
    public String extent;
    @JsonProperty("serialNum")
    public String serialNum;
    @JsonProperty("bibCit")
    public String bibCit;
    @JsonProperty("created")
    public String created;
    @JsonProperty("copyrighted")
    public Boolean copyrighted; // Keep as Boolean for internal logic

}

/**
 * Represents a Person.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Person extends BaseEntity {
    { entityType = "Agent:Person"; }
    @JsonProperty("name")
    public String name;
    @JsonProperty("surname")
    public String surname;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person person = (Person) o;
        return Objects.equals(name, person.name) &&
                Objects.equals(surname, person.surname);
    }
    @Override
    public int hashCode() {
        return Objects.hash(name, surname);
    }
}

/**
 * Represents an Organization.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class Organization extends BaseEntity {
    { entityType = "Agent:Organization"; }
    @JsonProperty("name")
    public String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Organization that = (Organization) o;
        return Objects.equals(name, that.name);
    }
    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}

/**
 * Represents a Category.
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
 * Represents a Material.
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
 * Main class responsible for converting data from a CSV file into a
 * Neo4j-compatible JSON Lines format, written to a .json file.
 */
public class CsvToJsonConverter {

    private static final Pattern PERSON_REGEX_STRICT = Pattern.compile(
            "^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+\\s[A-Z][a-z]+(?:\\s[A-Z][a-z]+)?(?:,?\\s(?:Jr\\.|Sr\\.|III))?$"
    );
    private static final Pattern PERSON_REGEX_LIST = Pattern.compile(
            "^(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)+(?:\\s(?:Jr\\.|Sr\\.|III))?(?:(?:\\s*(?:,|;|\\band\\b|&)\\s*)(?:Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)?[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*(?:\\s(?:Jr\\.|Sr\\.|III))?)*$"
    );
    private static final Pattern NAME_SPLIT_DELIMITER = Pattern.compile("\\s*(?:,|;|\\band\\b|&)\\s*");

    private static final AtomicInteger identityCounter = new AtomicInteger(0);
    private static final Map<BaseEntity, Integer> entityToIdentityMap = new HashMap<>();
    // Standard ObjectMapper, no special writer needed now
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Map<String, Integer> nodeCountsByType = new HashMap<>();
    private static final Map<String, Integer> relCountsByType = new HashMap<>();

    static {
        // Just configure NON_NULL inclusion
        objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    /**
     * Main entry point. Writes JSON Lines output to a .json file.
     * Output format will have spaces after colons/commas but keep each JSON object on one line,
     * achieved via string replacement.
     * @param args Command line arguments (not currently used).
     */
    @SuppressWarnings("deprecation")
    public static void main(String[] args) {

        String csvFilePath = "src/HCLEcatalog.csv";
        String logFilePath = "src/output/parsing.log";
        String jsonFilePath = "src/output/data.json";

        try (
                Reader reader = Files.newBufferedReader(Paths.get(csvFilePath), StandardCharsets.UTF_8);
                CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT
                        .withHeader()
                        .withIgnoreHeaderCase()
                        .withTrim());
                PrintWriter logWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(logFilePath), StandardCharsets.UTF_8));
                PrintWriter jsonWriter = new PrintWriter(new OutputStreamWriter(new FileOutputStream(jsonFilePath), StandardCharsets.UTF_8))
        ) {

            logWriter.println("Starting CSV to JSON conversion...");
            nodeCountsByType.clear();
            relCountsByType.clear();

            Map<String, Object> hcleProps = new LinkedHashMap<>();
            hcleProps.put("name", "HCLE");
            int hcleIdentity = 0;
            // Use an anonymous inner class for the specific HCLE entity
            entityToIdentityMap.put(new BaseEntity() {
                @Override public boolean equals(Object o) { return this.hashCode() == o.hashCode(); } // Simple identity check
                @Override public int hashCode() { return -1; } // Unique hashcode for this specific instance
            }, hcleIdentity);
            identityCounter.set(1); // Start next ID from 1

            Map<String, Object> hcleNodeMap = new LinkedHashMap<>();
            hcleNodeMap.put("jtype", "node");
            hcleNodeMap.put("identity", hcleIdentity);
            hcleNodeMap.put("label", "Collection");
            hcleNodeMap.put("properties", convertMapValuesToStrings(hcleProps));
            // Serialize normally, then format
            String compactJson = objectMapper.writeValueAsString(hcleNodeMap);
            String formattedJson = formatJsonString(compactJson);
            jsonWriter.println(formattedJson); // println adds newline BETWEEN json objects

            nodeCountsByType.put("Collection", 1);
            logWriter.printf("Created Collection node 'HCLE' with identity %d%n", hcleIdentity);

            int rowIndex = 0;
            for (CSVRecord csvRecord : csvParser) {
                rowIndex++;
                String idNum = getRecordValue(csvRecord, "IdNum");
                if (isNullOrEmpty(idNum)) {
                    logWriter.printf("Row %d ERROR -> IdNum is null or empty%n", rowIndex);
                    continue;
                }
                Map<String, String> rowData = new HashMap<>();
                for (String header : csvParser.getHeaderMap().keySet()) {
                    rowData.put(header, getRecordValue(csvRecord, header));
                }

                // --- Entity type determination, title check, entity creation logic remains the same ---
                 // Determine entity type
                String entityType;
                String tocVal = rowData.get("ToC");
                String extentVal = rowData.get("Extent");
                String serialNumVal = rowData.get("SerialNum");
                String bibCitVal = rowData.get("BibCit");
                boolean isDocument = !isNullOrNone(tocVal) || !isNullOrNone(extentVal)
                        || !isNullOrNone(serialNumVal) || !isNullOrNone(bibCitVal);
                entityType = isDocument ? "Document" : "Item";

                // Check for title
                String title = rowData.get("Title");
                if (isNullOrNone(title)) {
                    logWriter.printf("Row %d ERROR -> Title is null or None. Skipping row.%n", rowIndex);
                    continue;
                }
                logWriter.printf("Row %d -> Type: %s -> ID: %s, Title: %s -> Processing...%n", rowIndex, entityType, idNum, title);

                // Create primary entity (Document or Item)
                Artifact currentPrimaryEntity;
                 if ("Document".equals(entityType)) {
                    Document doc = new Document();
                    doc.title = title;
                    doc.toC = isNullOrNone(tocVal) ? null : tocVal; // Store null if N/A initially
                    doc.extent = isNullOrNone(extentVal) ? null : extentVal;
                    doc.serialNum = isNullOrNone(serialNumVal) ? null : serialNumVal;
                    doc.bibCit = isNullOrNone(bibCitVal) ? null : bibCitVal;
                    String createdRaw = rowData.get("Created");
                    if (isNullOrNone(createdRaw)) createdRaw = rowData.get("DateCR");
                    doc.created = isNullOrNone(createdRaw) ? null : createdRaw; // Store null if N/A
                    String copyrightedStr = rowData.get("Copyrighted");
                    if (!isNullOrNone(copyrightedStr)) {
                        // Parse boolean but keep the field as Boolean
                        if ("y".equalsIgnoreCase(copyrightedStr.trim())) doc.copyrighted = true;
                        else if ("n".equalsIgnoreCase(copyrightedStr.trim()) || "0".equals(copyrightedStr.trim())) doc.copyrighted = false;
                        // else leave it null if unrecognized
                    }
                    String description = rowData.get("Description");
                    if (!isNullOrNone(description)) doc.description = description;
                    String descComment = rowData.get("DescComment");
                    if (!isNullOrNone(descComment)) doc.descComment = descComment;
                    String wherMade = rowData.get("WherMade");
                    if (!isNullOrNone(wherMade)) doc.wherMade = wherMade;
                    currentPrimaryEntity = doc;
                } else { // Item
                    Item item = new Item();
                    item.title = title;
                    String partNumRaw = rowData.get("PartNum");
                    // Store null if N/A or single digit initially
                    item.partNum = (!isNullOrNone(partNumRaw) && !partNumRaw.trim().matches("^\\d$")) ? partNumRaw.trim() : null;
                    String conditionNts = rowData.get("ConditionNts");
                    if (!isNullOrNone(conditionNts)) item.conditionNts = conditionNts;
                    String description = rowData.get("Description");
                    if (!isNullOrNone(description)) item.description = description;
                    String descComment = rowData.get("DescComment");
                    if (!isNullOrNone(descComment)) item.descComment = descComment;
                    String wherMade = rowData.get("WherMade");
                    if (!isNullOrNone(wherMade)) item.wherMade = wherMade;
                    currentPrimaryEntity = item;
                }

                // --- Related entity processing (Material, Category, Creator) remains the same ---
                int primaryEntityIdentity = getOrCreateEntityIdentity(currentPrimaryEntity, jsonWriter, logWriter);

                // Process Material
                String materialStr = rowData.get("Material");
                Integer materialIdentity = null;
                if (materialStr != null) {
                    String materialName = null;
                    String trimmedMaterial = materialStr.trim();
                    if ("papr".equalsIgnoreCase(trimmedMaterial)) materialName = "paper";
                    else if ("digi".equalsIgnoreCase(trimmedMaterial)) materialName = "digital";
                    else if ("mix".equalsIgnoreCase(trimmedMaterial)) materialName = "mix";
                    if (materialName != null) {
                        Material currentMaterial = new Material();
                        currentMaterial.name = materialName;
                        materialIdentity = getOrCreateEntityIdentity(currentMaterial, jsonWriter, logWriter);
                    } else if (!trimmedMaterial.isEmpty() && !"none".equalsIgnoreCase(trimmedMaterial) && !"null".equalsIgnoreCase(trimmedMaterial)) {
                        logWriter.printf("Row %d WARNING -> Unrecognized Material code: '%s'%n", rowIndex, trimmedMaterial);
                    }
                }

                // Process Category (SubjectTop)
                String subjectTop = rowData.get("SubjectTop");
                Integer categoryIdentity = null;
                if (!isNullOrNone(subjectTop)) {
                    Category currentCategory = new Category();
                    currentCategory.name = subjectTop.trim();
                    categoryIdentity = getOrCreateEntityIdentity(currentCategory, jsonWriter, logWriter);
                }

                // Process Creator
                String creatorStr = rowData.get("Creator");
                Integer creatorIdentity = null;
                boolean isCreatorPerson = false;
                if (!isNullOrNone(creatorStr)) {
                    String trimmedCreator = creatorStr.trim();
                    // Try parsing as Person first (strict regex)
                    if (PERSON_REGEX_STRICT.matcher(trimmedCreator).matches()) {
                        Person creatorPerson = parsePerson(trimmedCreator);
                        if (creatorPerson != null) {
                            creatorIdentity = getOrCreateEntityIdentity(creatorPerson, jsonWriter, logWriter);
                            isCreatorPerson = true;
                        }
                    }
                    // If not a person (or parsing failed), treat as Organization
                    if (!isCreatorPerson) {
                        Organization creatorOrg = new Organization();
                        creatorOrg.name = trimmedCreator;
                        creatorIdentity = getOrCreateEntityIdentity(creatorOrg, jsonWriter, logWriter);
                    }
                }


                // --- Relationship writing logic remains the same (calls writeRelationship) ---
                Map<String, Object> belongsToProps = new HashMap<>();
                belongsToProps.put("originalIdNum", idNum); // Property value is String
                writeRelationship(jsonWriter, logWriter, primaryEntityIdentity, hcleIdentity, "belongsTo", belongsToProps);
                relCountsByType.merge("belongsTo", 1, Integer::sum);

                // Item -> Material
                if (currentPrimaryEntity instanceof Item && materialIdentity != null) {
                    writeRelationship(jsonWriter, logWriter, primaryEntityIdentity, materialIdentity, "madeOf", null);
                    relCountsByType.merge("madeOf", 1, Integer::sum);
                }

                // Category -> Document
                if (currentPrimaryEntity instanceof Document && categoryIdentity != null) {
                    writeRelationship(jsonWriter, logWriter, categoryIdentity, primaryEntityIdentity, "describe", null);
                    relCountsByType.merge("describe", 1, Integer::sum);
                }

                // Creator -> Document
                if (currentPrimaryEntity instanceof Document && creatorIdentity != null) {
                    if (isCreatorPerson) { // Person -> Document
                        writeRelationship(jsonWriter, logWriter, creatorIdentity, primaryEntityIdentity, "developed", null);
                        relCountsByType.merge("developed", 1, Integer::sum);
                    } else { // Organization -> Document
                        writeRelationship(jsonWriter, logWriter, creatorIdentity, primaryEntityIdentity, "produced", null);
                        relCountsByType.merge("produced", 1, Integer::sum);
                    }
                }

                // Process Contributor and AddlAuth fields
                processContributorField(rowData.get("Contributor"), "developed", primaryEntityIdentity, jsonWriter, logWriter, rowIndex);
                processContributorField(rowData.get("AddlAuth"), "collaborated", primaryEntityIdentity, jsonWriter, logWriter, rowIndex);

                logWriter.printf("Row %d -> Completed processing.%n", rowIndex);
            } // End CSV loop

            // --- Logging summary remains the same ---
             long totalNodesWritten = nodeCountsByType.values().stream().mapToLong(Integer::longValue).sum();
            long totalRelationshipsWritten = relCountsByType.values().stream().mapToLong(Integer::longValue).sum();
            logWriter.printf("Finished processing %d data rows.%n", rowIndex);
            logWriter.printf("Total Nodes Written: %d%n", totalNodesWritten);
            logWriter.println("Nodes by Type:");
            nodeCountsByType.forEach((type, count) -> logWriter.printf("  %s: %d%n", type, count));
            logWriter.printf("Total Relationships Written: %d%n", totalRelationshipsWritten);
            logWriter.println("Relationships by Type:");
            relCountsByType.forEach((type, count) -> logWriter.printf("  %s: %d%n", type, count));


            System.out.println("CSV to JSON conversion complete.");
            System.out.println("Log file generated at: " + logFilePath);
            System.out.println("JSON output generated at: " + jsonFilePath);

        } catch (IOException e) {
            System.err.println("An error occurred during file processing: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    } // End main

     /**
     * Helper method to add spaces after colons and commas in a compact JSON string.
     * WARNING: This is a simple replacement and might incorrectly add spaces
     * inside string values if they contain ':' or ','. Use with caution if
     * your string data might contain these characters.
     * @param compactJson A compact JSON string.
     * @return A formatted JSON string with spaces after colons and commas.
     */
    private static String formatJsonString(String compactJson) {
        if (compactJson == null) {
            return null;
        }
        // Add space after colon, then space after comma
        return compactJson.replace(":", ": ").replace(",", ", ");
    }

    // --- convertMapValuesToStrings method remains the same ---
    private static Map<String, Object> convertMapValuesToStrings(Map<String, Object> originalMap) {
        if (originalMap == null || originalMap.isEmpty()) {
            return Collections.emptyMap();
        }
        Map<String, Object> stringifiedMap = new LinkedHashMap<>(); // Preserve order if any
        originalMap.forEach((key, value) -> {
            if (value != null) {
                stringifiedMap.put(key, value.toString());
            }
        });
        return stringifiedMap;
    }


    /**
     * Writes a node JSON line to the output writer with spaces, on a single line.
     * Achieves formatting via string replacement after standard serialization.
     * Ensures internal fields are not included in properties.
     * Converts property values to strings before serialization.
     */
    private static int writeNode(PrintWriter writer, PrintWriter logWriter, String label, Map<String, Object> properties, Integer identity) throws IOException {
        if (identity == null) {
             logWriter.println("ERROR: Trying to write node without an identity!");
             return -1;
        }
        Map<String, Object> nodeMap = new LinkedHashMap<>();
        nodeMap.put("jtype", "node");
        nodeMap.put("identity", identity);
        nodeMap.put("label", label);
        nodeMap.put("properties", convertMapValuesToStrings(properties));

        // 1. Serialize to compact JSON using standard ObjectMapper
        String compactJson = objectMapper.writeValueAsString(nodeMap);

        // 2. Format the string to add spaces
        String formattedJson = formatJsonString(compactJson);

        // 3. Write the formatted string
        writer.println(formattedJson); // println adds newline BETWEEN json objects
        return identity;
    }

    /**
    * Helper overload for writing nodes derived from BaseEntity objects.
    * Extracts properties using Jackson annotations and REMOVES internal fields.
    * Relies on the other writeNode method for serialization and string formatting.
    */
    private static int writeNode(PrintWriter writer, PrintWriter logWriter, BaseEntity entity, int identity) throws IOException {
        @SuppressWarnings("unchecked")
        Map<String, Object> properties = objectMapper.convertValue(entity, Map.class);
        properties.remove("entityType");
        // The called writeNode method handles string conversion, serialization, and formatting.
        return writeNode(writer, logWriter, entity.getNodeLabel(), properties, identity);
    }

    /**
     * Writes a relationship JSON line to the output writer with spaces, on a single line.
     * Achieves formatting via string replacement after standard serialization.
     * Converts property values to strings before serialization.
     */
    private static void writeRelationship(PrintWriter writer, PrintWriter logWriter, int subjectId, int objectId, String relationshipName, Map<String, Object> properties) throws IOException {
        Map<String, Object> relMap = new LinkedHashMap<>();
        relMap.put("jtype", "relationship");
        relMap.put("subject", subjectId);
        relMap.put("object", objectId);
        relMap.put("name", relationshipName);
        relMap.put("properties", convertMapValuesToStrings(properties != null ? properties : Collections.emptyMap()));

        // 1. Serialize to compact JSON using standard ObjectMapper
        String compactJson = objectMapper.writeValueAsString(relMap);

        // 2. Format the string to add spaces
        String formattedJson = formatJsonString(compactJson);

        // 3. Write the formatted string
        writer.println(formattedJson); // println adds newline BETWEEN json objects
    }

    // --- getOrCreateEntityIdentity remains the same (calls the modified writeNode) ---
    private static int getOrCreateEntityIdentity(BaseEntity entity, PrintWriter jsonWriter, PrintWriter logWriter) throws IOException, UncheckedIOException {
        return entityToIdentityMap.computeIfAbsent(entity, k -> {
            int newId = identityCounter.getAndIncrement();
            try {
                // writeNode now handles serialization and formatting
                writeNode(jsonWriter, logWriter, k, newId);
                nodeCountsByType.merge(k.getNodeLabel(), 1, Integer::sum);
            } catch (IOException e) {
                logWriter.printf("ERROR writing node for entity %s: %s%n", k, e.getMessage());
                throw new UncheckedIOException(e);
            }
            return newId;
        });
    }

    // --- getRecordValue, isNullOrNone, isNullOrEmpty remain the same ---
    private static String getRecordValue(CSVRecord record, String headerName) {
        try {
            if (record.isMapped(headerName)) { return record.get(headerName); }
            else { return null; }
        } catch (IllegalArgumentException e) { return null; }
    }
    private static boolean isNullOrNone(String s) {
        if (s == null) return true;
        String trimmed = s.trim();
        return trimmed.isEmpty() || "None".equalsIgnoreCase(trimmed) || "NULL".equalsIgnoreCase(trimmed);
    }
    private static boolean isNullOrEmpty(String s) {
        return s == null || s.trim().isEmpty();
    }


    // --- processContributorField, addOrganizationAndRelationship, parsePerson remain the same ---
     private static void processContributorField(String fieldContent, String relationshipBaseType,
                                                int primaryEntityIdentity,
                                                PrintWriter jsonWriter, PrintWriter logWriter, int rowIndex) {
        if (isNullOrNone(fieldContent)) return;
        String content = fieldContent.trim();
        boolean looksLikePersonList = PERSON_REGEX_LIST.matcher(content).matches();
        try {
            if (looksLikePersonList) {
                String[] potentialNames = NAME_SPLIT_DELIMITER.split(content);
                for (String nameStr : potentialNames) {
                    String trimmedName = nameStr.trim();
                    if (trimmedName.isEmpty()) continue;
                    Person person = parsePerson(trimmedName);
                    if (person != null) {
                        int personId = getOrCreateEntityIdentity(person, jsonWriter, logWriter);
                        writeRelationship(jsonWriter, logWriter, personId, primaryEntityIdentity, relationshipBaseType, null);
                        relCountsByType.merge(relationshipBaseType, 1, Integer::sum);
                    } else {
                        logWriter.printf("Row %d -> Treating '%s' (from list '%s') as Organization after failed person parse.%n", rowIndex, trimmedName, content);
                        addOrganizationAndRelationship(trimmedName, relationshipBaseType, primaryEntityIdentity, jsonWriter, logWriter, rowIndex, false);
                    }
                }
            } else {
                addOrganizationAndRelationship(content, relationshipBaseType, primaryEntityIdentity, jsonWriter, logWriter, rowIndex, true);
            }
        } catch (IOException e) {
             logWriter.printf("Row %d ERROR -> IOException while processing contributor field '%s': %s%n", rowIndex, content, e.getMessage());
             throw new RuntimeException(e);
        } catch (UncheckedIOException e) {
             logWriter.printf("Row %d ERROR -> UncheckedIOException while processing contributor field '%s': %s%n", rowIndex, content, e.getCause().getMessage());
             throw new RuntimeException(e.getCause());
        }
    }
    private static void addOrganizationAndRelationship(String orgName, String relationshipBaseType,
                                                       int primaryEntityIdentity,
                                                       PrintWriter jsonWriter, PrintWriter logWriter,
                                                       int rowIndex, boolean logAsPotentialOrg) throws IOException, UncheckedIOException {
        Organization org = new Organization();
        org.name = orgName.trim();
        if (org.name.isEmpty()) {
            logWriter.printf("Row %d WARNING -> Attempted to add relationship for empty Organization name.%n", rowIndex);
            return;
        }
        int orgId = getOrCreateEntityIdentity(org, jsonWriter, logWriter);
        String relationshipType = relationshipBaseType.equals("developed") ? "produced" : relationshipBaseType;
        writeRelationship(jsonWriter, logWriter, orgId, primaryEntityIdentity, relationshipType, null);
        relCountsByType.merge(relationshipType, 1, Integer::sum);
    }
    private static Person parsePerson(String nameStr) {
        if (isNullOrEmpty(nameStr)) return null;
        String cleanedName = nameStr.replaceAll("^(Dr\\.|Prof\\.|Mr\\.|Ms\\.|Sir\\s)|((?:,\\s*)?(?:Jr\\.|Sr\\.|III))$", "").trim();
        if (cleanedName.isEmpty()) return null;
        String[] nameParts = cleanedName.split("\\s+");
        if (nameParts.length >= 2) {
            Person person = new Person();
            person.name = nameParts[0];
            person.surname = String.join(" ", Arrays.copyOfRange(nameParts, 1, nameParts.length));
            return person;
        } else {
            return null;
        }
    }

} // End CsvToNeo4jJsonConverter class

// --- END OF FILE CsvToNeo4jJsonConverter.java ---