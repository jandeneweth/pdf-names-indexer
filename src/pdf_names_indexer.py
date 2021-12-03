"""
PDF Names Indexer

This script is intended for usage in finding names in a pdf file and creating an index of occurrences.
"""

__author__ = "Jan Deneweth"
__copyright__ = "Copyright 2021, Jan Deneweth"
__license__ = "GPLv3+"
__version__ = "2021.10.22a1"
__maintainer__ = "Jan Deneweth"
__email__ = "jandeneweth@hotmail.com"


import re
import sys
import argparse
import collections
import typing as t

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextContainer


# -- Public Functions --

def index_names(
        pdf_file: t.BinaryIO,
        names_file: t.TextIO,
        outfile: t.TextIO,
        sort: bool = True,
        case_insensitive: bool = True,
        separator: str = ' : ',
        pages_separator: str = ', ',
        page_prefix: str = '',
        page_offset: int = 0,
        password: str | None = None,
):
    # Get the input names
    names, duplicates = _get_names(fh=names_file, sort=sort, case_insensitive=case_insensitive)
    print(f"Found {len(names)} names", file=sys.stderr)
    if duplicates:
        print(f"Warning: some names are not unique: \n{', '.join(duplicates)}", file=sys.stderr)
    # Get page occurence of each name
    name2pages = _parse_names(fh=pdf_file, names=names, password=password, case_insensitive=case_insensitive)
    if page_offset:
        # Offset the page numbers if needed
        name2pages = {
            name: [p + page_offset for p in pages]
            for name, pages in name2pages.items()
        }
    # Output results
    print("Outputting results...", file=sys.stderr)
    _write_output(outfh=outfile, names=names, name2pages=name2pages, separator=separator, pages_separator=pages_separator, page_prefix=page_prefix)


# -- Private Functions --

def _get_names(fh: t.TextIO, sort: bool = True, case_insensitive: bool = True) -> t.Tuple[t.List[str], t.List[str]]:
    """Read names from a file, removing duplicates."""
    names = list()
    unique_names = set()
    duplicates = set()
    for line in fh:
        # Strip and simplify input
        name = _simplify_text(line.strip())
        if not name:
            continue
        # Check for duplicate name entries and skip them
        unique_name = name.lower() if case_insensitive else name
        if unique_name in unique_names:
            duplicates.add(name)
            continue
        # Add the name
        names.append(name)
    if sort:
        names.sort()
    return names, sorted(duplicates)


def _parse_names(fh: t.BinaryIO, names: t.Iterable[str], password: str | None = None, case_insensitive: bool = True) -> t.Mapping[str, t.List[int]]:
    # Create the regex patterns
    re_flags = 0
    if case_insensitive:
        re_flags += re.IGNORECASE
    name2pattern = dict()
    for name in names:
        name_re = re.compile(rf"\b{re.escape(name)}\b", flags=re_flags)
        name2pattern[name] = name_re
    # Parse the PDF
    count = 0
    name2pages = collections.defaultdict(list)
    page_nr_prev = -1
    text_prev = ''
    for page_nr, text in enumerate(_parse_pdf_pages(fh=fh, password=password), start=1):
        print("\tParsing page {}...".format(page_nr), file=sys.stderr)
        # Flatten and simplify text
        text = _simplify_text(text=_flatten_text(text=text))
        # Search names
        for name, pattern in name2pattern.items():
            # In this page's text...
            if pattern.search(text):
                name2pages[name].append(page_nr)
                count += 1
            # In this and previous page text combined...
            #  Only if wasn't found in this nor previous page. In this case it's counted as present in the previous page.
            elif page_nr_prev not in name2pages.get(name, []):
                if pattern.search(text_prev+text):
                    name2pages[name].append(page_nr_prev)
        page_nr_prev = page_nr
        text_prev = text
    print(f"Found a total of {count} name occurrences (multiple occurrences of a name on the same page are ignored)", file=sys.stderr)
    return name2pages


def _parse_pdf_pages(fh: t.BinaryIO, password: str | None = None) -> t.Iterator[str]:
    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    for page in PDFPage.get_pages(fp=fh, password=password, check_extractable=True):
        # Process the page to a layed-out page
        interpreter.process_page(page)
        ltpage = device.get_result()
        # Retrieve all text from the page
        page_text = ""
        for lt_obj in ltpage:
            if isinstance(lt_obj, LTTextContainer):
                page_text += lt_obj.get_text()
        yield page_text


def _write_output(outfh, names: t.Iterable[str], name2pages: t.Mapping[str, t.Iterable[int]], separator: str, pages_separator: str, page_prefix: str, warn_not_found=True) -> None:
    """Write name page occurences to the output."""
    not_found = []
    for name in names:
        pages = name2pages[name]
        if not pages:
            not_found.append(name)
            continue
        outfh.write(f"{name}{separator}{pages_separator.join(page_prefix+str(p) for p in pages)}\n")
    if warn_not_found and not_found:
        print(f"Did not find any occurrences of the following names: \n{', '.join(not_found)}", file=sys.stderr)


def _simplify_text(text: str) -> str:
    """Replace some special characters by ASCII counterparts."""
    text = text.replace("’", "'")
    return text


def _flatten_text(text: str) -> str:
    """Reduce whitespace according to common conventions."""
    text = text.replace("-\n", "")  # hyphen indicates a word was broken up => join together again
    text = text.replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text


# -- Run as Script --

def main(argv=None):
    # Parse command line arguments
    argv = argv if argv is not None else sys.argv[1:]
    args = _parse_args(argv=argv)
    case_insensitive = not args.case_sensitive
    sort = not args.preserve_order
    # Run the processing
    try:
        index_names(
            pdf_file=args.pdf_file,
            names_file=args.names_file,
            outfile=args.outfile,
            sort=sort,
            case_insensitive=case_insensitive,
            separator=args.separator,
            pages_separator=args.pages_separator,
            page_prefix=args.page_prefix,
            page_offset=args.page_offset,
            password=args.password,
        )
    finally:
        args.pdf_file.close()
        args.names_file.close()
        args.outfile.close()


def _parse_args(argv: t.List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PDF Names Indexer: parses an input PDF document for a set of names to generate a page index.",
        epilog="Copyright (C) 2021  Jan Deneweth",
        allow_abbrev=False
    )
    parser.add_argument('pdf_file', help='PDF file to be parsed', type=argparse.FileType(mode='rb'))
    parser.add_argument('names_file', help="Text document containing one name per line, UTF-8 encoding expected.", type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('outfile', nargs='?', default=sys.stdout, help="Filepath of an output file. If blank, output will be printed to the console (UTF-8 encoding)", type=argparse.FileType(mode='w', encoding='utf-8'))
    parser.add_argument('--preserve_order', action='store_true', help="The names list is kept in parsing order when set")
    parser.add_argument('--case_sensitive', action='store_true', help="The names search is case-sensitive when set")
    parser.add_argument('--separator', default=' : ', help="A string separating a name from its listing of pages")
    parser.add_argument('--pages_separator', default=', ', help="A string separating one page number from another")
    parser.add_argument('--page_prefix', default='', help="A string preceding each page number")
    parser.add_argument('--page_offset', type=int, default=0, help="An offset to modify the output page numbers, by default the first page in the pdf will be seen as page 1")
    parser.add_argument('--password', default=None, help="A password for opening the PDF file")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args(args=argv)
    return args


if __name__ == '__main__':
    main()


#
#
# END OF FILE
