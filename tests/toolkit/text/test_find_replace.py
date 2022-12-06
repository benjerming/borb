import re
import typing
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from borb.pdf import HexColor
from borb.pdf.canvas.font.simple_font.font_type_1 import StandardType1Font
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_find_replace import SimpleFindReplace
from tests.test_util import check_pdf_using_validator, compare_visually_to_ground_truth

unittest.TestLoader.sortTestMethodsUsing = None


class TestFindReplace(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        # find output dir
        p: Path = Path(__file__).parent
        while "output" not in [x.stem for x in p.iterdir() if x.is_dir()]:
            p = p.parent
        p = p / "output"
        self.output_dir = Path(p, Path(__file__).stem.replace(".py", ""))
        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def test_write_document_001(self):

        # create document
        pdf = Document()

        # add page
        page = Page()
        pdf.add_page(page)

        # add test information
        layout = SingleColumnLayout(page)
        layout.add(
            Table(number_of_columns=2, number_of_rows=3)
            .add(Paragraph("Date", font="Helvetica-Bold"))
            .add(
                Paragraph(
                    datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                    font_color=HexColor("00ff00"),
                )
            )
            .add(Paragraph("Test", font="Helvetica-Bold"))
            .add(Paragraph(Path(__file__).stem))
            .add(Paragraph("Description", font="Helvetica-Bold"))
            .add(
                Paragraph(
                    "This test creates a PDF with an empty Page, and a Paragraph of text. "
                    "A subsequent test will attempt to extract all the text from this PDF."
                )
            )
            .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        )

        layout.add(
            Paragraph(
                """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
            Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
            Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            """,
                font_size=Decimal(10),
                vertical_alignment=Alignment.TOP,
                horizontal_alignment=Alignment.LEFT,
                padding_top=Decimal(5),
                padding_right=Decimal(5),
                padding_bottom=Decimal(5),
                padding_left=Decimal(5),
            )
        )

        # attempt to store PDF
        out_file: Path = self.output_dir / "output_001.pdf"
        with open(out_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, pdf)
        check_pdf_using_validator(out_file)

    def test_find_replace_near_match(self):

        doc: typing.Optional[Document] = None
        with open(self.output_dir / "output_001.pdf", "rb") as pdf_file_handle:
            doc = PDF.loads(pdf_file_handle)

        assert doc is not None

        # find/replace
        doc = SimpleFindReplace.sub("elit", "oled", doc)

        # attempt to store PDF
        out_file: Path = self.output_dir / "output_002.pdf"
        with open(out_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        check_pdf_using_validator(out_file)
        compare_visually_to_ground_truth(out_file)

    def test_find_replace_identical(self):

        doc: typing.Optional[Document] = None
        with open(self.output_dir / "output_001.pdf", "rb") as pdf_file_handle:
            doc = PDF.loads(pdf_file_handle)

        assert doc is not None

        # find/replace
        doc = SimpleFindReplace.sub("elit", "elit", doc)

        # attempt to store PDF
        out_file: Path = self.output_dir / "output_003.pdf"
        with open(out_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        check_pdf_using_validator(out_file)
        compare_visually_to_ground_truth(out_file)

    def test_find_replace_near_match_different_color(self):

        doc: typing.Optional[Document] = None
        with open(self.output_dir / "output_001.pdf", "rb") as pdf_file_handle:
            doc = PDF.loads(pdf_file_handle)

        assert doc is not None

        # find/replace
        doc = SimpleFindReplace.sub(
            "elit", "oled", doc, repl_font_color=HexColor("ff0000")
        )

        # attempt to store PDF
        out_file: Path = self.output_dir / "output_004.pdf"
        with open(out_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        check_pdf_using_validator(out_file)
        compare_visually_to_ground_truth(out_file)

    def test_find_replace_near_match_different_font(self):

        doc: typing.Optional[Document] = None
        with open(self.output_dir / "output_001.pdf", "rb") as pdf_file_handle:
            doc = PDF.loads(pdf_file_handle)

        assert doc is not None

        # find/replace
        doc = SimpleFindReplace.sub(
            "elit",
            "oled",
            doc,
            repl_font=StandardType1Font("Courier"),
            repl_font_size=Decimal(9),
        )

        # attempt to store PDF
        out_file: Path = self.output_dir / "output_005.pdf"
        with open(out_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        check_pdf_using_validator(out_file)
        compare_visually_to_ground_truth(out_file)
