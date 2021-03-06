"""
PDF Names Indexer tests
"""

import os
import io
import pytest

import pdf_names_indexer


# -- Tests --


class TestAux:

    def test_pages_included(self):
        all_included = pdf_names_indexer.PagesIncludedSpecs(None)
        assert all(x in all_included for x in (1, 10, 80, 404, ))
        exact_included = pdf_names_indexer.PagesIncludedSpecs('1,80')
        assert all(x in exact_included for x in (1, 80, ))
        assert all(x not in exact_included for x in (10, 404, ))
        range_included = pdf_names_indexer.PagesIncludedSpecs('1..80')
        assert all(x in range_included for x in (1, 10, 80, ))
        assert all(x not in range_included for x in (404, ))
        mixed_included = pdf_names_indexer.PagesIncludedSpecs('1,11..79,400..450')
        assert all(x in mixed_included for x in (1, 404, ))
        assert all(x not in mixed_included for x in (10, 80, ))


class TestArgParser:

    def test_parser_minimal(self):
        pdf_fp, names_fp, _ = _get_files(testdir='Odyssey')
        argv = [pdf_fp, names_fp]
        args = pdf_names_indexer._parse_args(argv=argv)
        if not args.pdf_file.readable():
            pytest.fail("PDF file not readable")
        if not args.names_file.readable():
            pytest.fail("Names file not readable")
        if not args.outfile.writable():
            pytest.fail("Outfile not writeable")
        assert args.preserve_order is False
        assert args.case_sensitive is False
        assert args.separator == ' : '
        assert args.pages_separator == ', '
        assert args.page_prefix == ''
        assert args.page_offset == 0
        assert args.password is None


class TestIndexer:

    def test_odyssey_minimal(self):
        pdf_fp, names_fp, expected_sorted_fp = _get_files(testdir='Odyssey')
        outfile = io.StringIO()
        with open(pdf_fp, 'rb') as pdf_file, open(names_fp, 'r') as names_file:
            pdf_names_indexer.index_names(
                pdf_file=pdf_file,
                names_file=names_file,
                outfile=outfile,
            )
        with open(expected_sorted_fp, 'r') as fh:
            expected_output = fh.read()
            assert expected_output == outfile.getvalue()


# -- Private Functions --

def _get_files(testdir: str):
    pdf_fp = _testdata_fp(testdir, 'pdf_file.pdf')
    names_fp = _testdata_fp(testdir, 'names_file.txt')
    expected_sorted_fp = _testdata_fp(testdir, 'expected_sorted.txt')
    return pdf_fp, names_fp, expected_sorted_fp


def _testdata_fp(*parts):
    testdir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(testdir, 'TestData', *parts)


#
#
# END OF FILE
