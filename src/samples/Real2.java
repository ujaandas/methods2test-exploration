public class DefaultParametersControlTest {
    private @Mock MutableRequest request;
    private @Mock Converters converters;
    private @Mock TwoWayConverter converter;
    private final Evaluator evaluator = new JavaEvaluator();

    @Test
	public void shouldBeGreedyWhenIPutAnAsteriskOnExpression() throws Exception {
		DefaultParametersControl control = new DefaultParametersControl("/clients/{pathToFile*}", converters, evaluator);

		assertThat(control.matches("/clients/my/path/to/file/"), is(true)); 
    // wont work, since while "/clients..." is a string, the method might not return one
    // same for "is(xyz)" - true is obv. a boolean, but is isnt
	}
}