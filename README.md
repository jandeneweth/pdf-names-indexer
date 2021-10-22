# PDF Names Indexer

A program to parse names from a PDF format file and output a page index.


## Usage

```
usage: pdf_names_indexer.py [-h] [--preserve_order] [--case_sensitive] [--separator SEPARATOR] [--pages_separator PAGES_SEPARATOR] [--page_prefix PAGE_PREFIX] [--page_offset PAGE_OFFSET] [--password PASSWORD] [--version]
                            pdf_file names_file [outfile]

PDF Names Indexer: parses an input PDF document for a set of names to generate a page index.

positional arguments:
  pdf_file              PDF file to be parsed
  names_file            Text document containing one name per line, UTF-8 encoding expected.
  outfile               Filepath of an output file. If blank, output will be printed to the console (UTF-8 encoding)

options:
  -h, --help            show this help message and exit
  --preserve_order      The names list is kept in parsing order when set
  --case_sensitive      The names search is case-sensitive when set
  --separator SEPARATOR
                        A string separating a name from its listing of pages
  --pages_separator PAGES_SEPARATOR
                        A string separating one page number from another
  --page_prefix PAGE_PREFIX
                        A string preceding each page number
  --page_offset PAGE_OFFSET
                        An offset to modify the output page numbers, by default the first page in the pdf will be seen as page 1
  --password PASSWORD   A password for opening the PDF file
  --version             show program's version number and exit
```


## License

PDF Names Indexer is a program to parse names from a PDF format file 
and output a page index. 
Copyright (C) 2021  Jan Deneweth

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
