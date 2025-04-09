package domain;


public class HallUser {

	public String id;
	public String username;
	public int usageStatistic;
	public double trustIndex;

//ste per current user:
//	private int credit;
//	private int bonus;
//
//	private int instances;
//	private int attributes;
//	private int updates;
//	private int deletions;
//	private int supports;
//	private int attacks;
//	private int comments;
//	private int supports_received;
//	private int attacks_received;
//	private int updates_received;
//	private int deletions_received;
	
	public HallUser(String randomId, String randomUsername, int randomUsageStatistic, double randomTrustIndex) {
		this.id=randomId;
		this.username=randomUsername;
		this.trustIndex=randomTrustIndex;
		this.usageStatistic=randomUsageStatistic;

	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String u) {
		this.username = u;
	}

	public double getTrustIndex() {
		return trustIndex;
	}

	public void setTrustIndex(double t) {
		this.trustIndex = t;
	}

	public int getUsageStatistic() {
		return usageStatistic;
	}

	public void setUsageStatistic(int s) {
		this.usageStatistic = s;
	}

}
