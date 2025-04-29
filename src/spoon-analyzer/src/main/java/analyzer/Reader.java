package analyzer;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;
import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;

public class Reader {

    public static class PairEntry {
        @SerializedName("test_class")
        private String testClass;

        public String getTestClass() {
            return (testClass != null) ? testClass.replace("\\n", "\n").trim() : testClass;
        }
    }

    public static List<PairEntry> readPairEntries(String directoryPath) {
        List<PairEntry> pairEntries = new ArrayList<>();
        Path dir = Paths.get(directoryPath);
        if (!Files.isDirectory(dir)) {
            System.err.println("Provided path is not a directory: " + directoryPath);
            return pairEntries;
        }
        try (Stream<Path> stream = Files.walk(dir)) {
            stream.filter(Files::isRegularFile)
                  .filter(p -> p.getFileName().toString().matches("pair_.*\\.json"))
                  .forEach(filePath -> {
                      try {
                          String content = new String(Files.readAllBytes(filePath), StandardCharsets.UTF_8);
                          PairEntry entry = new Gson().fromJson(content, PairEntry.class);
                          pairEntries.add(entry);
                      } catch (IOException e) {
                          System.err.println("Error reading file " + filePath + ": " + e.getMessage());
                      }
                  });
        } catch (IOException e) {
            System.err.println("Error traversing directory " + directoryPath + ": " + e.getMessage());
        }
        return pairEntries;
    }
}
