package analyzer;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.io.FileWriter;
import java.io.IOException;

public class Main {

    private static void writeCsvLog(String filename, Map<String, Analyzer.StdLibUsage> overallStdLibDistribution) {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.append("Library,Instance,Static,Total\n");
            for (Map.Entry<String, Analyzer.StdLibUsage> entry : overallStdLibDistribution.entrySet()) {
                Analyzer.StdLibUsage usage = entry.getValue();
                int total = usage.getInstanceCount() + usage.getStaticCount();
                writer.append(String.format("%s,%d,%d,%d\n",
                        usage.getLibName(), usage.getInstanceCount(), usage.getStaticCount(), total));
            }
            writer.flush();
        } catch (IOException e) {
            System.err.println("Error writing to CSV file: " + e.getMessage());
        }
    }
    
    private static void writeCsvLogPackagePrefixes(String filename, Map<String, int[]> overallPkgDistribution) {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.append("Package Prefix,Instance,Static,Total\n");
            for (Map.Entry<String, int[]> entry : overallPkgDistribution.entrySet()) {
                int instanceCount = entry.getValue()[0];
                int staticCount = entry.getValue()[1];
                int total = instanceCount + staticCount;
                writer.append(String.format("%s,%d,%d,%d\n", entry.getKey(), instanceCount, staticCount, total));
            }
            writer.flush();
        } catch (IOException e) {
            System.err.println("Error writing package prefix CSV file: " + e.getMessage());
        }
    }

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

        Map<String, Analyzer.StdLibUsage> overallStdLibDistribution = new HashMap<>();
        Map<String, int[]> overallPackagePrefixDistribution = new HashMap<>();

        for (Reader.PairEntry entry : pairEntries) {
            String testSource = entry.getTestClass();
            Analyzer.AnalyzerMetrics metrics = analyzer.analyzeTestClass(testSource);

            System.out.println("============ Analysis for a Test Class ============");
            System.out.println("Total Assertions: " + metrics.getTotalAssertions());
            System.out.println("Std Lib Type Usage: " + metrics.getStdLibTypeUsage());
            System.out.println("Std Lib Static Usage: " + metrics.getStdLibStaticUsage());
            System.out.println("Assertions with no method calls: " + metrics.getNoMethodCallAssertions());
            System.out.println("Assertions with only variables: " + metrics.getOnlyVariableAssertions());

            System.out.println("---- Standard Library Usage Distribution for this Test Class ----");
            for (Map.Entry<String, Analyzer.StdLibUsage> usageEntry : metrics.getStdLibUsageDistribution().entrySet()) {
                Analyzer.StdLibUsage usage = usageEntry.getValue();
                System.out.println("Library: " + usage.getLibName() +
                        " | Instance Count: " + usage.getInstanceCount() +
                        " | Static Count: " + usage.getStaticCount());

                overallStdLibDistribution.merge(usage.getLibName(), usage, (existing, newUsage) -> {
                    existing.merge(newUsage);
                    return existing;
                });
                
                String pkgPrefix = usage.getPackagePrefix();
                int[] counts = overallPackagePrefixDistribution.getOrDefault(pkgPrefix, new int[]{0, 0});
                counts[0] += usage.getInstanceCount();
                counts[1] += usage.getStaticCount();
                overallPackagePrefixDistribution.put(pkgPrefix, counts);
            }
            System.out.println("---------------------------------------------------------------");

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

        System.out.println("---- Overall Standard Library Usage Distribution ----");
        for (Map.Entry<String, Analyzer.StdLibUsage> entry : overallStdLibDistribution.entrySet()) {
            Analyzer.StdLibUsage usage = entry.getValue();
            System.out.println("Library: " + usage.getLibName() +
                    " | Total Instance Count: " + usage.getInstanceCount() +
                    " | Total Static Count: " + usage.getStaticCount());
        }
        System.out.println("------------------------------------------------------");

        System.out.println("---- Overall Package Prefix Usage Distribution ----");
        for (Map.Entry<String, int[]> pkgEntry : overallPackagePrefixDistribution.entrySet()) {
            int[] counts = pkgEntry.getValue();
            int total = counts[0] + counts[1];
            System.out.println("Package Prefix: " + pkgEntry.getKey() + 
                    " | Total Instance Count: " + counts[0] + 
                    " | Total Static Count: " + counts[1] +
                    " | Total: " + total);
        }
        System.out.println("------------------------------------------------------");

        writeCsvLog("analysis_output.csv", overallStdLibDistribution);
        System.out.println("Analysis results logged to analysis_output1.csv");

        writeCsvLogPackagePrefixes("package_prefix_usage_output.csv", overallPackagePrefixDistribution);
        System.out.println("Package prefix analysis results logged to analysis_output2.csv");
    }
}
