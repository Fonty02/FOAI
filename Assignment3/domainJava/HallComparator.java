package domain;

import java.util.Comparator;

/**
 * A comparator for HallUser objects that sorts users based on their usage statistics
 * and trust index in descending order.
 * <p>
 * Users with higher usage statistics are ranked higher. If two users have the same
 * usage statistic, the one with the higher trust index is ranked higher.
 * </p>
 */
public class HallComparator implements Comparator<HallUser> {

    /**
     * Compares two HallUser objects for ordering.
     * 
     * @param u1 the first HallUser to be compared
     * @param u2 the second HallUser to be compared
     * @return a negative integer if u1 should be ranked higher than u2,
     *         a positive integer if u2 should be ranked higher than u1,
     *         or zero if they are considered equal in ranking
     */
    public int compare(HallUser u1, HallUser u2) {
//        if (u1.getUsageStatistic() == u2.getUsageStatistic())
//            return (u2.getTrustIndex() < u1.getTrustIndex()) ? -1 : 1;
//        return (u2.getUsageStatistic() < u1.getUsageStatistic()) ? -1 : 1;
        if (u1.getUsageStatistic() < u2.getUsageStatistic())
            return 1;
        else if (u1.getUsageStatistic() > u2.getUsageStatistic())
            return -1;
        else {
             if (u2.getTrustIndex() < u1.getTrustIndex())
                 return 1;
             else if (u2.getTrustIndex() > u1.getTrustIndex())
                 return -1;
             else
                 return 0;
        }
    }

}
