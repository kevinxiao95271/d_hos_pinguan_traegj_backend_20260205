import org.mindrot.jbcrypt.BCrypt;

public class GenBcrypt {
    public static void main(String[] args) {
        System.out.println("ops2026=" + BCrypt.hashpw("ops2026", BCrypt.gensalt(8)));
        System.out.println("committee2026=" + BCrypt.hashpw("committee2026", BCrypt.gensalt(8)));
    }
}
