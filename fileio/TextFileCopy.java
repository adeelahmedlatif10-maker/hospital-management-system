import java.io.*;

public class TextFileCopy {
    public static void copy(String src, String dst) throws IOException {
        try (BufferedReader br = new BufferedReader(new FileReader(src));
             BufferedWriter bw = new BufferedWriter(new FileWriter(dst))) {
            char[] buf = new char[8192];
            int n;
            while ((n = br.read(buf)) != -1) {
                bw.write(buf, 0, n);
            }
        }
    }
}
