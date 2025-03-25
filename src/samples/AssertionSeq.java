public class MyClass {
    public static void main(String[] args) {
        SomeClass obj = new SomeClass();
        assertEquals(0, obj.foo().bar());
    }
}

class SomeClass {
    public SomeClass foo() {
        return this;
    }

    public int bar() {
        return 0;
    }
}