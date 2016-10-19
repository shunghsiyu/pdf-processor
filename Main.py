"""Main Module of PDF Splitter"""
import argparse
import logging
import os
import sys
from functools import partial
from itertools import ifilter, ifilterfalse

from PyPDF2 import PdfFileWriter

from Util import all_pdf_files_in_directory, split_on, concat_pdf_pages, merge_with_next, is_landscape, \
    write_pdf_file, add_pages, make_pagenum_even, detect_blank_page

# Get default logger
log = logging.getLogger(__name__)

# TODO: Add GUI Interface
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
    '-d',
    '--double-sided',
    action='store_true',
    default=False,
    help='the input PDF files are double sided scans'
)
parser.add_argument(
    '-f',
    '--filter-density',
    dest='min_density',
    type=float,
    default=0.0,
    help='Append blank page to make page number an even number'
)
parser.add_argument(
    '-e',
    '--even-pages',
    dest='even_pages',
    action='store_true',
    default=False,
    help='Append blank page to make page number an even number'
)
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='increase output verbosity'
)

# A dictionary that contains function that corrects the rotation of a PDF page
rotation_correctors = {
    'cw': lambda page: page.rotateClockwise(90),
    'ccw': lambda page: page.rotateCounterClockwise(90),
    'no-op': lambda page: page  # Do nothing
}

# A dictionary that contains tuple of two functions, the first detect whether a chunk needs to be merged
# with the next chunk, the second function decides how chunks should be merged
merge_configs = {
    # Merge when there is only one page in the chunk (happens with double-side scan) and
    # merge the two chunks leaving out only the back-side of the header page
    'double_sided': (lambda pages: len(pages) == 1, lambda chunk1, chunk2: chunk1 + chunk2[1:]),
    'single_sided': (lambda pages: False, None)  # Never merge page
}


def main(argv=sys.argv[1:]):
    # Get to directory with PDF files to work on
    args = parser.parse_args(argv)

    if args.verbose:
        log.parent.setLevel(logging.DEBUG)

    directory = args.directory
    merge_config = 'double_sided' if args.double_sided else 'single_sided'
    output_files = pdf_split(
        directory,
        rotation_correctors[args.rotate_back],
        args.even_pages,
        merge_configs[merge_config],
        args.min_density
    )

    if args.merge:
        merge_output(output_files)


def pdf_split(directory, correct_rotation, even_pages, merge_config, min_image_data_density):
    """Split all the PDF files in a certain directory.
    Optionally correct the rotation of the header page, make page chunks have even number of pages and
    merge page chunks before writing to output files."""

    log.info('Working on PDF files in %s', directory)

    output_filenames = []

    # Open the PDF files
    all_pdf_files = [os.path.join(directory, filename) for filename in all_pdf_files_in_directory(directory)]
    log.info('Found the following PDF files\n    %s', '\n    '.join(all_pdf_files))
    opened_files = [open(path, 'rb') for path in all_pdf_files]

    # Take all the pages in all the PDF files into a generator
    all_pages = concat_pdf_pages(opened_files)

    # First split pages into chunks when a page in landscape orientation is detected
    page_chunks1 = split_on(all_pages, predicate=is_landscape)
    # Next merge adjacent chunks that meets certain condition with a merger function
    # this is used to handle situation where the scan is double sided
    page_chunks2 = merge_with_next(page_chunks1, predicate=merge_config[0], merger=merge_config[1])

    ignored_pdf_writer = PdfFileWriter()
    # For all pages that belongs to the same document ID
    for idx, pages_to_write in enumerate(page_chunks2, start=1):
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
        detect_blank_page_under_threshold = partial(detect_blank_page, min_density=min_image_data_density)
        non_blank_pages_to_write = ifilter(detect_blank_page_under_threshold, pages_to_write)
        add_pages(pdf_writer, non_blank_pages_to_write)
        blank_pages_to_ignore = ifilterfalse(detect_blank_page_under_threshold, pages_to_write)
        add_pages(ignored_pdf_writer, blank_pages_to_ignore, to_log=False)

        # Conditionally make the output PDF file have an even number of pages, which makes printing the PDF file easier
        if even_pages:
            make_pagenum_even(pdf_writer)

        output_filename = '{0:05}.pdf'.format(idx)
        output_filenames.append(output_filename)
        # And write those pages to a single PDF file
        log.info('Writing PDF pages to %s', output_filename)
        write_pdf_file(output_filename, pdf_writer)

    if ignored_pdf_writer.getNumPages() > 0:
        write_pdf_file('ignored.pdf', ignored_pdf_writer)

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
    add_pages(pdf_writer, concat_pdf_pages(opened_files))

    # And write those pages to a single PDF file
    log.info('Writing PDF pages to %s', output_filename)
    write_pdf_file(output_filename, pdf_writer)

    # Make sure to close all the files that were opened
    log.debug('Closing all opened files')
    for opened_file in opened_files:
        opened_file.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
    logging.shutdown()
