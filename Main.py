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


def width_greater_than_height(page):
    box = page.mediaBox
    return box.getWidth() > box.getHeight()


if __name__ == '__main__':
    args = parser.parse_args()
    all_pdf_files = all_pdf_files_in_directory(args.directory)
    opened_files = map(lambda path: open(path, 'rb'), all_pdf_files)
    all_pages = concat_pdf_pages(opened_files)

    for idx, pages in enumerate(split_on_condition(all_pages, predicate=width_greater_than_height), start=1):
        pdf_writer = PdfFileWriter()
        map(pdf_writer.addPage, pages)

        output_filename = '{0:05}.pdf'.format(idx)
        with open(output_filename, 'wb') as output_file:
            pdf_writer.write(output_file)
            output_file.flush()
            os.fsync(output_file.fileno())

    map(lambda f: f.close, opened_files)
