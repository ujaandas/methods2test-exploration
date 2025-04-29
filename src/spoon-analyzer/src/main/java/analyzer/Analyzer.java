package analyzer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

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
    private Set<String> stdLibTypes;

    public Analyzer() {
        this.stdLibTypes = loadStdLibTypes("/Users/ooj/Dev/Research/assertion/methods2test-exploration/src/stdlibtypes.txt");
        System.out.println("Loaded standard library types: " + stdLibTypes);
    }

    private Set<String> loadStdLibTypes(String filePath) {
        Set<String> types = new HashSet<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    types.add(line);
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading stdlibtypes.txt: " + e.getMessage());
        }
        return types;
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
                boolean allVariables = true; // until proven otherwise

                for (CtExpression<?> arg : invocation.getArguments()) {
                    System.out.println("   >> Analyzing argument: " + arg);
                    CtTypeReference<?> typeRef = arg.getType();
                    if (typeRef != null) {
                        String qualifiedName = typeRef.getQualifiedName();
                        System.out.println("      Resolved type: " + qualifiedName);
                        if (stdLibTypes.contains(qualifiedName) || stdLibTypes.contains(typeRef.getSimpleName())) {
                            String detected = stdLibTypes.contains(qualifiedName) ? qualifiedName : typeRef.getSimpleName();
                            System.out.println("      => Standard library type detected: " + detected);
                            metrics.incrementStdLibTypeUsage();
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
                            String declQualifiedName = declType.getQualifiedName();
                            System.out.println("      Argument is a method call from type: " + declQualifiedName);
                            if (stdLibTypes.contains(declQualifiedName) || stdLibTypes.contains(declType.getSimpleName())) {
                                String detectedStatic = stdLibTypes.contains(declQualifiedName) ? declQualifiedName : declType.getSimpleName();
                                System.out.println("      => Standard library static method detected: " + detectedStatic);
                                metrics.incrementStdLibStaticUsage();
                            }
                        }
                    } else if (!(arg instanceof CtVariableAccess)) {
                        // If this argument isn't a method call or a variable, then it isn't "only variable".
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

    public static class AnalyzerMetrics {
        private int totalAssertions = 0;
        private int stdLibTypeUsage = 0;
        private int stdLibStaticUsage = 0;
        private int noMethodCallAssertions = 0;
        private int onlyVariableAssertions = 0;

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
    }
}
