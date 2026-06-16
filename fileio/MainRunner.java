import java.util.*;

public class MainRunner {
    public static void main(String[] args) {
        try {
            String paragraph = "This is a sample paragraph.\nIt has multiple lines.\nEnd.";
            CharFileIO.writeParagraph("charfile.txt", paragraph);
            System.out.println("Read paragraph:\n" + CharFileIO.readParagraph("charfile.txt"));

            byte[] bytes = new byte[256];
            for (int i = 0; i < bytes.length; i++) bytes[i] = (byte) i;
            BinaryFileIO.writeBinary("binaryfile.bin", bytes);
            System.out.println("Read binary length: " + BinaryFileIO.readBinary("binaryfile.bin").length);

            List<Student> students = new ArrayList<>();
            students.add(new Student(1, "Alice", 3.8));
            students.add(new Student(2, "Bob", 3.4));
            students.add(new Student(3, "Carol", 3.9));
            StudentSerialization.writeStudents("students.dat", students);
            List<Student> read = StudentSerialization.readStudents("students.dat");
            System.out.println("Deserialized students:");
            for (Student s : read) System.out.println(s);

            TextFileCopy.copy("charfile.txt", "charfile_copy.txt");
            System.out.println("Copied charfile.txt to charfile_copy.txt");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
