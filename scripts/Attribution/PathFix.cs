public static class PathFix
{
    public static string AddIxToASPath(ScopeArray<string> ixHopList, string hopASNs)
    {
        string[] asns = hopASNs.Split(',');

        foreach (string ixHop in ixHopList)
        {
            string[] hopSplit = ixHop.Split(':');
            int hopNum = int.Parse(hopSplit[0]);
            string ixName = hopSplit[1];

            asns[hopNum] = ixName;
        }

        return string.Join(",", asns);
    }

    public static int FirstMsftHop(string aspath)
    {
        int msftIndex = aspath.IndexOf(",8075");
        if (msftIndex == -1)
        {
            return -1;
        }

        string msftSub = aspath.Substring(0, msftIndex);
        int count =  msftSub.Split(',').Length;
        return count > 0 ? count : -1;
    }

    public static string[] FixPath(string sourceASN, string[] asPath)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(sourceASN) || asPath == null)
            {
                return null;
            }

            string[] noloops = RemoveLoops(sourceASN, asPath);
            string[] noempty = RemoveEmpty(sourceASN, asPath);

            return noempty;
        }
        catch(Exception e)
        {
            return null;
        }
    }

    public static string[] RemoveLoops(string sourceASN, string[] asPath)
    {
        if (string.IsNullOrWhiteSpace(asPath[0]))
        {
            asPath[0] = sourceASN;
        }

        var lastIndexes = new Dictionary<string, int>();

        string previousASN = asPath[0];
        lastIndexes[previousASN] = 0;

        for (int i = 1; i < asPath.Length; i++)
        {
            string asn = asPath[i];

            if (string.IsNullOrWhiteSpace(asn))
            {
                continue;
            }

            lastIndexes[asn] = i;
        }

        for (int i = 1; i < asPath.Length; i++)
        {
            string asn = asPath[i];

            if (string.IsNullOrWhiteSpace(asn))
            {
                continue;
            }

            if (asn != previousASN && i < lastIndexes[previousASN])
            {
                asPath[i] = previousASN;
            }
            else
            {
                previousASN = asn;
            }
        }

        return asPath;
    }

    public static string[] RemoveEmpty(string sourceASN, string[] asPath)
    {
        if (string.IsNullOrWhiteSpace(asPath[0]))
        {
            asPath[0] = sourceASN;
        }

        string lastASN = asPath[0];
        int i = 1;

        while (i < asPath.Length)
        {
            if (!string.IsNullOrWhiteSpace(asPath[i]))
            {
                lastASN = asPath[i];
                i++;
                continue;
            }

            int j = i + 1;
            while (j < asPath.Length && string.IsNullOrWhiteSpace(asPath[j]))
            {
                j++;
            }

            if (j == asPath.Length)
            {
                break;
            }

            string nextASN = asPath[j];
            if (nextASN == lastASN)
            {
                for (int k = i; k <= j; k++)
                {
                    asPath[k] = lastASN;
                }
            }

            i = j + 1;
        }

        return asPath;
    }
}
