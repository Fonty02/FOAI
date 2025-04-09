package domain;

import java.util.Comparator;

public class HallComparator implements Comparator<HallUser> {

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
