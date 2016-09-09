"""Main Module of PDF Splitter"""
import argparse
import os

from PyPDF2 import PdfFileWriter

from Util import all_pdf_files_in_directory, split_on_condition, concat_pdf_pages

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
    opened_files = map(lambda path: open(path, 'rb'), all_pdf_files)

    all_pages = concat_pdf_pages(opened_files)

    # For all pages that belongs to the same document ID
    for idx, pages in enumerate(split_on_condition(all_pages, predicate=width_greater_than_height), start=1):
        # Put those pages into a writer
        pdf_writer = PdfFileWriter()
        map(pdf_writer.addPage, pages)

        # And write those pages to a single PDF file
        output_filename = '{0:05}.pdf'.format(idx)
        with open(output_filename, 'wb') as output_file:
            pdf_writer.write(output_file)

            # Extra measures to make sure data is written to disk
            output_file.flush()
            os.fsync(output_file.fileno())

    # Make sure to close all the files that were opened
    map(lambda f: f.close, opened_files)


def width_greater_than_height(page):
    box = page.mediaBox
    return box.getWidth() > box.getHeight()


if __name__ == '__main__':
    main()
