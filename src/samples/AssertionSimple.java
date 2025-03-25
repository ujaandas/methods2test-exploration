public class MyClass {
    public static void main(String[] args) {
        int result = add(2, 3);
        assertEquals(5, result);
    }

    public static int add(int a, int b) {
        return a + b;
    }
}