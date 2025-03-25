public class MyClass {
    public static void main(String[] args) {
        SomeClass obj = new SomeClass();
        assertEquals(0, obj.foo(0).bar(1));
    }
}

class SomeClass {
    public SomeClass foo(int input) {
        return this;
    }

    public int bar(int input) {
        return input - input;
    }
}
