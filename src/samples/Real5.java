public class SetExportFormatTaskTest {
    @Mock
	private ReportProps reportProps;
    @Mock
	private JRDataSource datasource;
    private SetExportFormatTask sut;

    @Test
	public void testConfigure_PDF() {
		// Arrange
		final ReportFormat reportFormat = ReportFormat.PDF;

		// Act
		final Map<String, Object> configure = sut.configure(reportProps,
				reportFormat, datasource);

		// Assert
		assertEquals(1, configure.size());
		assertEquals(reportFormat.getFormat(),
				configure.get(JasperReportsMultiFormatView.DEFAULT_FORMAT_KEY));
	}
}