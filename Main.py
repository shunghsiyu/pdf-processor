"""Main Module of PDF Splitter"""
import argparse

from PyPDF2 import PdfFileWriter

from Util import all_pages_in_directory, split_on_condition


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


def width_greater_than_height(page):
    box = page.mediaBox
    return box.getWidth() > box.getHeight()


if __name__ == '__main__':
    args = parser.parse_args()
    all_pages = all_pages_in_directory(args.directory)

    for idx, pages in enumerate(split_on_condition(all_pages, predicate=width_greater_than_height)):
        pdf_writer = PdfFileWriter()
        map(pdf_writer.addPage, pages)

        output_filename = '{0:05}.pdf'.format(idx)
        with open(output_filename, 'wb') as output_file:
            pdf_writer.write(output_file)
