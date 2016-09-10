"""Main Module of PDF Splitter"""
import argparse
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


def main():
    # Get to directory with PDF files to work on
    args = parser.parse_args()
    directory = args.directory

    # Open the PDF files
    all_pdf_files = [os.path.join(directory, filename) for filename in all_pdf_files_in_directory(directory)]
    opened_files = [open(path, 'rb') for path in all_pdf_files]

    all_pages = concat_pdf_pages(opened_files)

    def make_pagenum_even(pdf_writer):
        """Helper function that append a blank page if the number of page is an odd number, in order to make the
        page number even."""
        if pdf_writer.getNumPages() % 2 == 1:
            pdf_writer.addBlankPage()

    # For all pages that belongs to the same document ID
    for idx, pages in enumerate(split_on(all_pages, predicate=is_landscape), start=1):
        # Put those pages into a writer
        pdf_writer = PdfFileWriter()
        map(pdf_writer.addPage, pages)

        # Make sure the output PDF will have an even number of pages
        # which makes printing the PDF file easier
        make_pagenum_even(pdf_writer)

        output_filename = '{0:05}.pdf'.format(idx)
        # And write those pages to a single PDF file
        write_pdf_file(output_filename, pdf_writer)

    # Make sure to close all the files that were opened
    for file in opened_files:
        file.close()


if __name__ == '__main__':
    main()
