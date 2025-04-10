package domain;  

public class Attachment {
	private String progr;
	private String extension;
	private String description;
	private String fileName;
	
	public Attachment(String p, String e, String d, String f) {
		progr = p;
		extension = e;
		description = d;
		fileName=f;
	}
	
	public String getProgr() {
		return progr;
	}
	public String getExtension() {
		return extension;
	}
	public String getDescription() {
		return description;
	}
	public String getFilename() {
		return fileName + extension;
	}

}
