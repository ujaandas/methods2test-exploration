public class VRaptorConvertersAdapterTest {
    private @Mock Converters converters;
    private @Mock Converter converter;
    private VRaptorConvertersAdapter adapter;
    private Cat myCat;
    private ResourceBundle bundle;

    @Test
	@SuppressWarnings("unchecked")
	public void shouldInvokePrimitiveConverter() throws OgnlException {
		when(converters.to(int.class)).thenReturn(converter);
		when(converter.convert("2", int.class, bundle)).thenReturn(2);
	
	Map<?,?> context = Ognl.createDefaultContext(myCat);
	Ognl.setTypeConverter(context, adapter);
	Ognl.setValue("length", context, myCat, "2");
	assertThat(myCat.length, is(equalTo(2)));
	}
}