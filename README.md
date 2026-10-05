# PDF Names Indexer

A program to parse names from a PDF format file and output a page index.


## Installation

The recommended approach is to use [uv](https://docs.astral.sh/uv/getting-started/installation/).
See their website for installation instructions for your system.
It will manage Python versions and package dependencies transparently, avoiding clashes with system installations.

```
uv tool install git+https://github.com/jandeneweth/pdf-names-indexer
```

Then run the tool using either `pdf-names-indexer` directly if it was succesfully installed on your PATH, 
or `uv tool run pdf-names-indexer`.


## Usage

```
usage: pdf-names-indexer [-h] [--sort_names] [--filter_duplicates] [--filter_not_found] [--case_sensitive]
                         [--separator SEPARATOR] [--pages_separator PAGES_SEPARATOR] [--page_prefix PAGE_PREFIX]
                         [--page_offset PAGE_OFFSET] [--pages_included PAGES_INCLUDED] [--password PASSWORD] [--version]
                         pdf_file names_file [outfile]

PDF Names Indexer: parses an input PDF document for a set of names to generate a page index.

positional arguments:
  pdf_file              PDF file to be parsed
  names_file            Text document containing one name per line, UTF-8 encoding expected.
  outfile               Filepath of an output file. By default (value '-') output will be printed to the console (UTF-8 encoding)

options:
  -h, --help            show this help message and exit
  --sort_names          Output sorts the names alphabetically if set
  --filter_duplicates   Duplicate names are only emitted once in the output if set
  --filter_not_found    Names without results are not emitted in the output if set
  --case_sensitive      The names search is case-sensitive when set
  --separator SEPARATOR
                        A string separating a name from its listing of pages
  --pages_separator PAGES_SEPARATOR
                        A string separating one page number from another
  --page_prefix PAGE_PREFIX
                        A string preceding each page number
  --page_offset PAGE_OFFSET
                        An offset to modify the output page numbers, by default the first page in the pdf is page 1
  --pages_included PAGES_INCLUDED
                        A series of pages and/or page ranges to search, in the format "a,b,c..d,e..f". By default all pages are searched
  --password PASSWORD   A password for opening the PDF file
  --version             show program's version number and exit

Copyright (C) 2021 Jan Deneweth
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
