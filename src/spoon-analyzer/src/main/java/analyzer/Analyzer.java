package analyzer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

import spoon.Launcher;
import spoon.reflect.CtModel;
import spoon.reflect.code.CtExpression;
import spoon.reflect.code.CtInvocation;
import spoon.reflect.code.CtVariableAccess;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.reference.CtTypeReference;
import spoon.reflect.visitor.filter.TypeFilter;
import spoon.support.compiler.VirtualFile;

public class Analyzer {
    
    private Set<StdLibEntry> stdLibEntries;

    public Analyzer() {
        
        this.stdLibEntries = loadStdLibEntries("fqns.txt");
        System.out.println("Loaded standard library entries: " + stdLibEntries);
    }

    private Set<StdLibEntry> loadStdLibEntries(String filePath) {
        Set<StdLibEntry> entries = new HashSet<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    
                    entries.add(new StdLibEntry(line));
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading fqns.txt: " + e.getMessage());
        }
        return entries;
    }

    public AnalyzerMetrics analyzeTestClass(String testClassSource) {
        AnalyzerMetrics metrics = new AnalyzerMetrics();

        Launcher launcher = new Launcher();
        launcher.getEnvironment().setNoClasspath(true);
        launcher.getEnvironment().setComplianceLevel(17);
        launcher.addInputResource(new VirtualFile(testClassSource, "TestClass.java"));
        launcher.buildModel();
        CtModel model = launcher.getModel();

        System.out.println("==== Model successfully built ====");

        
        for (CtInvocation<?> invocation : model.getElements(new TypeFilter<>(CtInvocation.class))) {
            String invokedMethod = invocation.getExecutable().getSimpleName();
            if (invokedMethod.startsWith("assert")) {
                CtMethod<?> parentMethod = invocation.getParent(CtMethod.class);
                String currentMethod = (parentMethod != null) ? parentMethod.getSimpleName() : "Unknown";
                System.out.println("===========================================");
                System.out.println("Inside method: " + currentMethod);
                System.out.println("Assertion encountered: " + invocation);
                metrics.incrementTotalAssertions();

                boolean hasMethodCall = false;
                boolean allVariables = true; 

                
                for (CtExpression<?> arg : invocation.getArguments()) {
                    System.out.println("   >> Analyzing argument: " + arg);
                    CtTypeReference<?> typeRef = arg.getType();
                    if (typeRef != null) {
                        String resolvedType = typeRef.getQualifiedName();
                        String simpleType = typeRef.getSimpleName();
                        System.out.println("      Resolved type: " + resolvedType);
                        
                        Optional<StdLibEntry> match = stdLibEntries.stream()
                                .filter(entry -> entry.getSimpleName().equals(simpleType))
                                .findFirst();
                        if (match.isPresent()) {
                            StdLibEntry detectedEntry = match.get();
                            System.out.println("      => Standard library type detected: " + detectedEntry.getSimpleName());
                            metrics.incrementStdLibTypeUsage();
                            metrics.recordStdLibUsage(detectedEntry, false);
                        }
                    } else {
                        System.out.println("      Warning: Unable to resolve type.");
                    }

                    
                    if (arg instanceof CtInvocation) {
                        hasMethodCall = true;
                        allVariables = false;
                        CtInvocation<?> argInvocation = (CtInvocation<?>) arg;
                        CtTypeReference<?> declType = argInvocation.getExecutable().getDeclaringType();
                        if (declType != null) {
                            String declResolvedType = declType.getQualifiedName();
                            String declSimpleType = declType.getSimpleName();
                            System.out.println("      Argument is a method call from type: " + declResolvedType);
                            Optional<StdLibEntry> matchDecl = stdLibEntries.stream()
                                    .filter(entry -> entry.getSimpleName().equals(declSimpleType))
                                    .findFirst();
                            if (matchDecl.isPresent()) {
                                StdLibEntry detectedStatic = matchDecl.get();
                                System.out.println("      => Standard library static method detected: " + detectedStatic.getSimpleName());
                                metrics.incrementStdLibStaticUsage();
                                metrics.recordStdLibUsage(detectedStatic, true);
                            }
                        }
                    } else if (!(arg instanceof CtVariableAccess)) {
                        
                        allVariables = false;
                    }
                }
                if (!hasMethodCall) {
                    metrics.incrementNoMethodCallAssertions();
                    System.out.println("==> Conclusion: Assertion has no method calls in its arguments.");
                }
                if (allVariables) {
                    metrics.incrementOnlyVariableAssertions();
                    System.out.println("==> Conclusion: All arguments of this assertion are variables.");
                }
                System.out.println("===========================================\n");
            }
        }
        return metrics;
    }

    public static class StdLibEntry {
        private final String fullName;
        private final String simpleName;
        private final String packagePrefix; 

        public StdLibEntry(String fullName) {
            this.fullName = fullName;
            int lastDotIndex = fullName.lastIndexOf('.');
            this.simpleName = (lastDotIndex >= 0) ? fullName.substring(lastDotIndex + 1) : fullName;
            
            String[] parts = fullName.split("\\.");
            if (parts.length >= 2) {
                this.packagePrefix = parts[0] + "." + parts[1];
            } else {
                this.packagePrefix = fullName;
            }
        }

        public String getFullName() {
            return fullName;
        }

        public String getSimpleName() {
            return simpleName;
        }

        public String getPackagePrefix() {
            return packagePrefix;
        }

        @Override
        public String toString() {
            return "StdLibEntry{" +
                    "fullName='" + fullName + '\'' +
                    ", simpleName='" + simpleName + '\'' +
                    ", packagePrefix='" + packagePrefix + '\'' +
                    '}';
        }
    }

    public static class AnalyzerMetrics {
        private int totalAssertions = 0;
        private int stdLibTypeUsage = 0;
        private int stdLibStaticUsage = 0;
        private int noMethodCallAssertions = 0;
        private int onlyVariableAssertions = 0;

        
        private Map<String, StdLibUsage> stdLibUsageDistribution = new HashMap<>();
        
        private Map<String, Integer> stdLibPackageUsageDistribution = new HashMap<>();

        public void incrementTotalAssertions() {
            totalAssertions++;
        }

        public void incrementStdLibTypeUsage() {
            stdLibTypeUsage++;
        }

        public void incrementStdLibStaticUsage() {
            stdLibStaticUsage++;
        }

        public void incrementNoMethodCallAssertions() {
            noMethodCallAssertions++;
        }

        public void incrementOnlyVariableAssertions() {
            onlyVariableAssertions++;
        }

        public int getTotalAssertions() {
            return totalAssertions;
        }

        public int getStdLibTypeUsage() {
            return stdLibTypeUsage;
        }

        public int getStdLibStaticUsage() {
            return stdLibStaticUsage;
        }

        public int getNoMethodCallAssertions() {
            return noMethodCallAssertions;
        }

        public int getOnlyVariableAssertions() {
            return onlyVariableAssertions;
        }

        public Map<String, StdLibUsage> getStdLibUsageDistribution() {
            return stdLibUsageDistribution;
        }
        
        public Map<String, Integer> getStdLibPackageUsageDistribution() {
            return stdLibPackageUsageDistribution;
        }

        
        
        public void recordStdLibUsage(StdLibEntry entry, boolean isStatic) {
            String key = entry.getSimpleName();
            StdLibUsage usage = stdLibUsageDistribution.get(key);
            if (usage == null) {
                usage = new StdLibUsage(entry.getFullName(), entry.getPackagePrefix());
                stdLibUsageDistribution.put(key, usage);
            }
            if (isStatic) {
                usage.incrementStaticCount();
            } else {
                usage.incrementInstanceCount();
            }
            
            String pkg = entry.getPackagePrefix();
            int count = stdLibPackageUsageDistribution.getOrDefault(pkg, 0);
            stdLibPackageUsageDistribution.put(pkg, count + 1);
        }
    }

    public static class StdLibUsage {
        private final String fullName;
        private final String packagePrefix;
        private int instanceCount;
        private int staticCount;

        public StdLibUsage(String fullName, String packagePrefix) {
            this.fullName = fullName;
            this.packagePrefix = packagePrefix;
        }

        public void incrementInstanceCount() {
            instanceCount++;
        }

        public void incrementStaticCount() {
            staticCount++;
        }

        
        public String getLibName() {
            return fullName;
        }

        public String getFullName() {
            return fullName;
        }

        public String getPackagePrefix() {
            return packagePrefix;
        }

        public int getInstanceCount() {
            return instanceCount;
        }

        public int getStaticCount() {
            return staticCount;
        }

        @Override
        public String toString() {
            return "StdLibUsage{" +
                    "fullName='" + fullName + '\'' +
                    ", packagePrefix='" + packagePrefix + '\'' +
                    ", instanceCount=" + instanceCount +
                    ", staticCount=" + staticCount +
                    '}';
        }

        public void merge(StdLibUsage other) {
            this.instanceCount += other.instanceCount;
            this.staticCount += other.staticCount;
        }
    }
}
