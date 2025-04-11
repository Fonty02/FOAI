package domain;  

/**
 * Represents an attachment with its associated information.
 * This class stores data such as identifier, file extension, description, and filename.
 */
public class Attachment {
    private String progr;
    private String extension;
    private String description;
    private String fileName;
    
    /**
     * Constructs a new Attachment object with the specified parameters.
     * 
     * @param p The identifier/progressive number of the attachment
     * @param e The file extension (e.g., ".pdf", ".jpg")
     * @param d The description of the attachment
     * @param f The filename without extension
     */
    public Attachment(String p, String e, String d, String f) {
        progr = p;
        extension = e;
        description = d;
        fileName=f;
    }
    
    /**
     * Returns the identifier of the attachment.
     * 
     * @return The attachment identifier
     */
    public String getProgr() {
        return progr;
    }
    
    /**
     * Returns the file extension.
     * 
     * @return The file extension
     */
    public String getExtension() {
        return extension;
    }
    
    /**
     * Returns the description of the attachment.
     * 
     * @return The attachment description
     */
    public String getDescription() {
        return description;
    }
    
    /**
     * Returns the complete filename including extension.
     * 
     * @return The complete filename with extension
     */
    public String getFilename() {
        return fileName + extension;
    }

}
