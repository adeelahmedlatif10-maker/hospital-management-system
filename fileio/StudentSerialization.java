import java.io.*;
import java.util.*;

public class StudentSerialization {
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
