public class PathAnnotationRoutesParserTest {
    private Proxifier proxifier;
    private @Mock Converters converters;
    private NoTypeFinder typeFinder;
    private @Mock Router router;
    private @Mock ParameterNameProvider nameProvider;
    private PathAnnotationRoutesParser parser;

    @Test
	public void dontRegisterRouteIfMethodIsStatic() {
		List<Route> routes = parser.rulesFor(new DefaultResourceClass(ClientsController.class));
		Route route = getRouteMatching(routes, "/staticMe");
		assertNull(route);
	}
}