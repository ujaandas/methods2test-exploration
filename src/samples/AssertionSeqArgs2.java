public class MyClass {
    public static void main(String[] args) {
        SomeClass obj = new SomeClass();
        assertEquals(0, obj.foo(0).bar(1));
    }
}

class SomeClass {
    public SomeOtherClass foo(int input) {
        SomeOtherClass obj = new SomeOtherClass();
        return obj;
    }
}

class SomeOtherClass {
    public int bar(int input) {
        return input - input;
    }
}