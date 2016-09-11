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
    '-r',
    '--rotate-back',
    choices=['ccw', 'cw', 'no-op'],
    default='no-op',
    help='how to correct the rotation of the first PDF page'
)
parser.add_argument(
    '-m',
    '--merge',
    action='store_true',
    help='merge all the output files into another PDF file'
)
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='increase output verbosity'
)

# Get default logger
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

# A dictionary that contains function that corrects the rotation of a PDF page
rotation_correctors = {
    'cw': lambda page: page.rotateClockwise(90),
    'ccw': lambda page: page.rotateCounterClockwise(90),
    'no-op': lambda page: page  # Do nothing
}


def main():
    # Get to directory with PDF files to work on
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    directory = args.directory
    output_files = pdf_split(directory, rotation_correctors[args.rotate_back])

    if args.merge:
        merge_output(output_files)


def pdf_split(directory, correct_rotation):
    log.info('Working on PDF files in %s', directory)

    output_filenames = []

    # Open the PDF files
    all_pdf_files = [os.path.join(directory, filename) for filename in all_pdf_files_in_directory(directory)]
    log.info('Found the following PDF files\n    %s', '\n    '.join(all_pdf_files))
    opened_files = [open(path, 'rb') for path in all_pdf_files]

    # Take all the pages in all the PDF files into a generator
    all_pages = concat_pdf_pages(opened_files)

    def make_pagenum_even(writer):
        """Helper function that append a blank page if the number of page is an odd number, in order to make the
        page number even."""
        if writer.getNumPages() % 2 == 1:
            log.info('    Adding a blank page')
            writer.addBlankPage()

    # For all pages that belongs to the same document ID
    for idx, pages_to_write in enumerate(split_on(all_pages, predicate=is_landscape), start=1):
        # Create a PDF writer instance
        pdf_writer = PdfFileWriter()

        # Correct the rotation of the first page in file
        first_page = pages_to_write[0]
        # If this is the first page of the first PDF file, it might not be in landscape view
        # so we check for that
        if is_landscape(first_page):
            log.debug('Correction rotation on the first page=%s', repr(first_page))
            # Correct the rotation the way the user specifies
            correct_rotation(first_page)

        # Put those pages into a writer
        log.info('Adding %d PDF pages to PDFWriter', len(pages_to_write))
        for page in pages_to_write:
            log.debug('    Adding page %s', repr(page))
            pdf_writer.addPage(page)

        # Make sure the output PDF will have an even number of pages
        # which makes printing the PDF file easier
        make_pagenum_even(pdf_writer)

        output_filename = '{0:05}.pdf'.format(idx)
        output_filenames.append(output_filename)
        # And write those pages to a single PDF file
        log.info('Writing PDF pages to %s', output_filename)
        write_pdf_file(output_filename, pdf_writer)

    # Make sure to close all the files that were opened
    log.debug('Closing all opened files')
    for opened_file in opened_files:
        opened_file.close()

    return output_filenames


def merge_output(pdf_files, output_filename='all.pdf'):
    """Merge all the output PDF files into a single PDF files to make printing easier.
    The output filename defaults to 'all.pdf'."""
    log.info('Merging output files\n    %s', '\n    '.join(pdf_files))

    opened_files = [open(path, 'rb') for path in pdf_files]

    pdf_writer = PdfFileWriter()
    # Write all the pages in all the output PDF files into PDFWriter
    for page in concat_pdf_pages(opened_files):
        pdf_writer.addPage(page)
    log.info('Added %d pages to PDFWriter', pdf_writer.getNumPages())

    # And write those pages to a single PDF file
    log.info('Writing PDF pages to %s', output_filename)
    write_pdf_file(output_filename, pdf_writer)

    # Make sure to close all the files that were opened
    log.debug('Closing all opened files')
    for opened_file in opened_files:
        opened_file.close()


if __name__ == '__main__':
    main()
