"""Main Module of PDF Splitter"""
import argparse
import logging
import os

from PyPDF2 import PdfFileWriter

from Util import all_pdf_files_in_directory, split_on, concat_pdf_pages, is_landscape, write_pdf_file

parser = \
    argparse.ArgumentParser(
        description='Split all the pages of multiple PDF files in a directory by document number'
    )
parser.add_argument(
    'directory',
    metavar='PATH',
    type=str,
    help='path to a directory'
)
parser.add_argument(
    '--verbose',
    action='store_true',
    help='increase output verbosity'
)

# Get default logger
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


def main():
    # Get to directory with PDF files to work on
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    directory = args.directory
    pdf_split(directory)


def pdf_split(directory):
    log.info('Working on PDF files in %s', directory)

    # Open the PDF files
    all_pdf_files = [os.path.join(directory, filename) for filename in all_pdf_files_in_directory(directory)]
    log.info('Found the following PDF files\n    %s', '\n    '.join(all_pdf_files))
    opened_files = [open(path, 'rb') for path in all_pdf_files]

    # Take all the pages in all the PDF files into a generator
    all_pages = concat_pdf_pages(opened_files)

    def make_pagenum_even(pdf_writer):
        """Helper function that append a blank page if the number of page is an odd number, in order to make the
        page number even."""
        if pdf_writer.getNumPages() % 2 == 1:
            log.debug('    Adding a blank page')
            pdf_writer.addBlankPage()

    # For all pages that belongs to the same document ID
    for idx, pages_to_write in enumerate(split_on(all_pages, predicate=is_landscape), start=1):
        # Create a PDF writer instance
        pdf_writer = PdfFileWriter()

        # Put those pages into a writer
        log.info('Adding %d pages to PDFWriter', len(pages_to_write))
        for page in pages_to_write:
            log.debug('    Adding page %s', repr(page))
            pdf_writer.addPage(page)

        # Make sure the output PDF will have an even number of pages
        # which makes printing the PDF file easier
        make_pagenum_even(pdf_writer)

        output_filename = '{0:05}.pdf'.format(idx)
        # And write those pages to a single PDF file
        log.info('Writing PDF pages to %s', output_filename)
        write_pdf_file(output_filename, pdf_writer)

    # Make sure to close all the files that were opened
    log.debug('Closing all opened files')
    for file in opened_files:
        file.close()


if __name__ == '__main__':
    main()
