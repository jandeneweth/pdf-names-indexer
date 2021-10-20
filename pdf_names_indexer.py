'''
Created on 5 Feb 2017
Current version 1 August 2017
@author: 'Jan Deneweth'
Created at request of 'Wim Deneweth'

This script is intended for usage in finding names in a pdf file and creating an index of occurrences
Uses pdfminer, should support pdf's with cmap (in contrast to current PyPDF2)
'''



# Imports
import sys
import argparse
import re



# PDF page parser
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextContainer
def parse_pdf_pages(path):
    '''
    Using info from http://denis.papathanasiou.org/posts/2010.08.04.post.html
    But bloody hell, this package has no documentation whatsoever
    '''
    # Open a PDF file.
    fp = open(path, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    for page in PDFPage.create_pages(document):
        # Process the page
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_total = ""
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextContainer): # text
                text_total += lt_obj.get_text()
        yield text_total



# Read command line arguments
parser = argparse.ArgumentParser(prog="Name Indexer", description="Parses an input PDF document for a set of names, generates a page index", epilog="Created by 'Jan Deneweth'")
parser.add_argument('pdf_file', help='Filepath of the input PDF file')
parser.add_argument('names_file', help="Filepath of a text document containing one name per line")
parser.add_argument('--output', '-o', default="", help="Filepath of an output file. If blank, output will be printed to the console")
parser.add_argument('--case_sensitive', '-c', default='N', choices=['Y','N'], help="Sets whether searching for names should be case-sensitive")
parser.add_argument('--trim_search', '-tr', default='Y', choices=['Y','N'], help="Sets whether the search strings should be trimmed of whitespace")
parser.add_argument('--separator', '-s', default=' : ', help="A string separating a name from its listing of pages")
parser.add_argument('--pages_separator', '-ps', default=', ', help="A string separating one page number from another")
parser.add_argument('--pages_prefix', '-pf', default='', help="A string preceding each page number")
parser.add_argument('--page_offset', '-po', type=int, default=0, help="An offset to modify the output page numbers, by default the first page in the pdf will be seen as page 1")
parser.add_argument('--print_unfound', '-pu', default='N', choices=['Y','N'], help="Sets whether to print names of which no occurrence was found")
args = parser.parse_args()



def eprint(*args, **kwargs):
    '''Print to the error log'''
    print(*args, file=sys.stderr, **kwargs)
def clean_exit(error=""):
    '''Cleanly exit the program'''
    if error:
        eprint(error)
        eprint("")
    parser.print_help(file=sys.stderr)
    sys.exit()



# Open files to ensure their existence/to reserve them
pdf_file = None
names_file = None
output_file = None
try:
    pdf_file = open(args.pdf_file, 'rb')
except FileNotFoundError:
    clean_exit("Error: PDF file not found: {}".format(args.pdf_file))
try:
    names_file = open(args.names_file, 'r') # the cp1252 encoding should cover expected characters (Western Europe)
except FileNotFoundError:
    clean_exit("Error: names file not found: {}".format(args.names_file))
try:
    if args.output:
        output_file = open(args.output, 'w')
    else:
        output_file = sys.stdout
except OSError:
    clean_exit("Error: problem when opening file for writing: {}".format(args.output))



# Read names
names_dict = dict()
names_list = []
names = set()
doubles = []
for line in names_file:
    # Get new name
    name = line.rstrip("\n")
    if args.trim_search == "Y":
        name = name.strip() # Original input name is also stripped with this option
    name = name.replace("’", "'")
    # If name already occurred => add to doubles for reporting
    if name in names:
        doubles.append(name)
    else:
        # Create regular expression for the name
        name_str = name
        if args.case_sensitive == 'N':
            name_str = name_str.lower()
        name_re_str = r"\b{}\b".format(name_str) # Add word boundary character; must find words, not just substrings!
        name_re = re.compile(name_re_str)
        # Remember which name uses which regular expression and initialise a results dictionary
        names_list.append( (name, name_re) )
        names_dict[name_re] = []
eprint("Found {} names".format(len(names_list)))
if doubles:
    eprint("Warning: some names are not unique:")
    eprint(', '.join(doubles))



# Parse pdf
count = 0
for index, text in enumerate(parse_pdf_pages(args.pdf_file)):
    eprint("\tParsing page {}...".format(index+1))
    # Adapt case sensitivity
    if args.case_sensitive == 'N':
        text = text.lower()
    # Flatten text
    text = text.replace("’", "'")
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    # Search names
    for name in names_dict.keys():
        if name.search(text): # Regex search, statement will be True if match is found
            names_dict[name].append(index+1)
            count += 1
eprint("Found a total of {} name occurrences (multiple occurrences of a name on the same page are ignored)".format(count))



# Print results
eprint("Outputting results...")
unfound = []
for name_str, re_str in names_list:
    if names_dict[re_str]: # Has solutions
        pages = args.pages_separator.join( [ args.pages_prefix+str(page+args.page_offset) for page in names_dict[re_str] ] )
        output_file.write( "{0}{1}{2}\n".format(name_str, args.separator, pages) )
    else:
        if args.print_unfound == "Y":
            output_file.write( "{0}{1}\n".format(name_str, args.separator) )
        unfound.append(name_str)
# Print unfound names if option is set
if args.print_unfound == "N" and unfound:
    eprint("Did not find any occurrences of the following names:")
    eprint(', '.join(unfound))



# Close filehandles
pdf_file.close()
names_file.close()
if args.output:
    output_file.close()



#
#
## END OF FILE
