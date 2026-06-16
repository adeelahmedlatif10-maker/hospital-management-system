import java.io.*;
import java.util.*;

public class FileIODemo {

    // --- Task 1: Character file write/read ---
    public static class CharFileIO {
        public static void writeParagraph(String path, String paragraph) throws IOException {
            try (BufferedWriter bw = new BufferedWriter(new FileWriter(path))) {
                bw.write(paragraph);
            }
        }

        public static String readParagraph(String path) throws IOException {
            StringBuilder sb = new StringBuilder();
            try (BufferedReader br = new BufferedReader(new FileReader(path))) {
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append(System.lineSeparator());
                }
            }
            return sb.toString();
        }
    }

    // --- Task 2: Binary file write/read ---
    public static class BinaryFileIO {
        public static void writeBinary(String path, byte[] data) throws IOException {
            try (FileOutputStream fos = new FileOutputStream(path)) {
                fos.write(data);
            }
        }

        public static byte[] readBinary(String path) throws IOException {
            File file = new File(path);
            byte[] data = new byte[(int) file.length()];
            try (FileInputStream fis = new FileInputStream(file)) {
                int read = 0;
                while (read < data.length) {
                    int n = fis.read(data, read, data.length - read);
                    if (n < 0) break;
                    read += n;
                }
            }
            return data;
        }
    }

    // --- Task 3: Serializable Student and helpers ---
    public static class Student implements Serializable {
        private static final long serialVersionUID = 1L;
        private int id;
        private String name;
        private double gpa;

        public Student(int id, String name, double gpa) {
            this.id = id; this.name = name; this.gpa = gpa;
        }

        public int getId() { return id; }
        public String getName() { return name; }
        public double getGpa() { return gpa; }

        @Override public String toString() {
            return "Student{id=" + id + ", name='" + name + "', gpa=" + gpa + "}";
        }
    }

    public static class StudentSerialization {
        public static void writeStudents(String path, List<Student> students) throws IOException {
            try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(path))) {
                oos.writeObject(students);
            }
        }

        @SuppressWarnings("unchecked")
        public static List<Student> readStudents(String path) throws IOException, ClassNotFoundException {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(path))) {
                return (List<Student>) ois.readObject();
            }
        }
    }

    // --- Task 4: Copy text files using Readers/Writers ---
    public static class TextFileCopy {
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

    // --- Demo runner ---
    public static void main(String[] args) {
        try {
            // 1) Write/read a paragraph (character I/O)
            String paragraph = "This is a sample paragraph.\nIt has multiple lines.\nEnd.";
            CharFileIO.writeParagraph("charfile.txt", paragraph);
            System.out.println("Read paragraph:\n" + CharFileIO.readParagraph("charfile.txt"));

            // 2) Binary file write/read
            byte[] bytes = new byte[256];
            for (int i = 0; i < bytes.length; i++) bytes[i] = (byte) i;
            BinaryFileIO.writeBinary("binaryfile.bin", bytes);
            System.out.println("Read binary length: " + BinaryFileIO.readBinary("binaryfile.bin").length);

            // 3) Serialize/deserialize multiple Student objects
            List<Student> students = new ArrayList<>();
            students.add(new Student(1, "Alice", 3.8));
            students.add(new Student(2, "Bob", 3.4));
            students.add(new Student(3, "Carol", 3.9));
            StudentSerialization.writeStudents("students.dat", students);
            List<Student> read = StudentSerialization.readStudents("students.dat");
            System.out.println("Deserialized students:");
            for (Student s : read) System.out.println(s);

            // 4) Copy text file using Readers/Writers
            TextFileCopy.copy("charfile.txt", "charfile_copy.txt");
            System.out.println("Copied charfile.txt to charfile_copy.txt");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
