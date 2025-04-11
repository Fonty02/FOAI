package domain;

/**
 * Represents a user in the hall system.
 * This class stores basic user information and statistics used for tracking user activity and trust.
 */
public class HallUser {

    /** Unique identifier for the user */
    public String id;
    
    /** Username of the user in the system */
    public String username;
    
    /** Statistical measure of the user's system usage */
    public int usageStatistic;
    
    /** Measure of the user's trustworthiness in the system */
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
    
    /**
     * Constructs a new HallUser with the specified parameters.
     *
     * @param randomId The unique identifier for the user
     * @param randomUsername The username of the user
     * @param randomUsageStatistic The initial usage statistic value
     * @param randomTrustIndex The initial trust index value
     */
    public HallUser(String randomId, String randomUsername, int randomUsageStatistic, double randomTrustIndex) {
        this.id=randomId;
        this.username=randomUsername;
        this.trustIndex=randomTrustIndex;
        this.usageStatistic=randomUsageStatistic;

    }

    /**
     * Returns the user's unique identifier.
     *
     * @return The user's ID
     */
    public String getId() {
        return id;
    }

    /**
     * Sets the user's unique identifier.
     *
     * @param id The new ID to set
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * Returns the user's username.
     *
     * @return The username
     */
    public String getUsername() {
        return username;
    }

    /**
     * Sets the user's username.
     *
     * @param u The new username to set
     */
    public void setUsername(String u) {
        this.username = u;
    }

    /**
     * Returns the user's trust index.
     *
     * @return The trust index value
     */
    public double getTrustIndex() {
        return trustIndex;
    }

    /**
     * Sets the user's trust index.
     *
     * @param t The new trust index value
     */
    public void setTrustIndex(double t) {
        this.trustIndex = t;
    }

    /**
     * Returns the user's usage statistic.
     *
     * @return The usage statistic value
     */
    public int getUsageStatistic() {
        return usageStatistic;
    }

    /**
     * Sets the user's usage statistic.
     *
     * @param s The new usage statistic value
     */
    public void setUsageStatistic(int s) {
        this.usageStatistic = s;
    }

}
