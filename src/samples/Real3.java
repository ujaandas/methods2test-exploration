public class DefaultResourceTranslatorTest {
    private @Mock Router router;
    private @Mock HttpServletRequest request;
    private @Mock ResourceMethod method;
    private VRaptorRequest webRequest;
    private RequestInfo info;
    private DefaultResourceTranslator translator;

    @Test
	public void shouldAcceptCaseInsensitiveGetRequestUsingThe_methodParameter() {
		when(request.getRequestURI()).thenReturn("/url");
		when(request.getParameter("_method")).thenReturn("gEt");
		when(request.getMethod()).thenReturn("POST");
		when(router.parse("/url", HttpMethod.GET, webRequest)).thenReturn(method);

	ResourceMethod resource = translator.translate(info);
	assertThat(resource, is(equalTo(method)));

  // resource can be resolved as ResourceMethod (how? spoon is like magic)
  // but is still cannot
	}
}