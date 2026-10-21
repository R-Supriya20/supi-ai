from pypdf import PdfReader


class DocumentExtractor:

    def extract_text(self, file_path: str) -> str:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text