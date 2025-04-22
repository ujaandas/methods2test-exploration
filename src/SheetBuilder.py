import csv


class SheetBuilder:
    def __init__(self):
        self.file_loc = "results"
        self.file_name = "results.csv"
        self.csvfile = open(f"../{self.file_loc}/{self.file_name}", "a+", newline="")
        self.writer = csv.DictWriter(
            self.csvfile,
            fieldnames=[
                "repo_name",
                "module_name",
                "focal_class",
                "test_class",
            ],
        )

        # self.writer.writeheader()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.csvfile.close()

    def write_tm(
        self,
        repo_name: str,
        module_name: str,
        fc_name: str,
        fc_content: str,
        tc_name: str,
        tc_content: str,
    ):
        self.writer.writerow(
            {
                "repo_name": repo_name,
                "module_name": module_name,
                "focal_class": fc_content,
                "test_class": tc_content,
            }
        )
