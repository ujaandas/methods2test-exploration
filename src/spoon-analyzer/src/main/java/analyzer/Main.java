package analyzer;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Usage: java analyzer.Main <directory containing JSON files>");
            System.exit(1);
        }

        String directoryPath = args[0];
        List<Reader.PairEntry> pairEntries = Reader.readPairEntries(directoryPath);
        if (pairEntries.isEmpty()) {
            System.out.println("No matching JSON files found under: " + directoryPath);
            return;
        }

        Analyzer analyzer = new Analyzer();
        int overallAssertions = 0;
        int overallStdLibTypeUsage = 0;
        int overallStdLibStaticUsage = 0;
        int overallNoMethodCalls = 0;
        int overallOnlyVariables = 0;

        for (Reader.PairEntry entry : pairEntries) {
            String testSource = entry.getTestClass();
            Analyzer.AnalyzerMetrics metrics = analyzer.analyzeTestClass(testSource);

            System.out.println("============ Analysis for a Test Class ============");
            System.out.println("Total Assertions: " + metrics.getTotalAssertions());
            System.out.println("Std Lib Type Usage: " + metrics.getStdLibTypeUsage());
            System.out.println("Std Lib Static Usage: " + metrics.getStdLibStaticUsage());
            System.out.println("Assertions with no method calls: " + metrics.getNoMethodCallAssertions());
            System.out.println("Assertions with only variables: " + metrics.getOnlyVariableAssertions());

            overallAssertions += metrics.getTotalAssertions();
            overallStdLibTypeUsage += metrics.getStdLibTypeUsage();
            overallStdLibStaticUsage += metrics.getStdLibStaticUsage();
            overallNoMethodCalls += metrics.getNoMethodCallAssertions();
            overallOnlyVariables += metrics.getOnlyVariableAssertions();
        }

        System.out.println("============ Overall Summary ============");
        System.out.println("Overall Assertions: " + overallAssertions);
        System.out.println("Overall Std Lib Type Usage: " + overallStdLibTypeUsage);
        System.out.println("Overall Std Lib Static Usage: " + overallStdLibStaticUsage);
        System.out.println("Overall Assertions with no method calls: " + overallNoMethodCalls);
        System.out.println("Overall Assertions with only variables: " + overallOnlyVariables);
    }
}
