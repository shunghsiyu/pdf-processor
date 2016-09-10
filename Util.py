"""Collection of Helper Functions"""
import os
from fnmatch import fnmatch

from PyPDF2 import PdfFileReader


def pdf_file(filename):
    """Test whether or the the filename ends with '.pdf'."""
    return fnmatch(filename, '*.pdf')


def all_pdf_files_in_directory(path):
    """Return a list of of PDF files in a directory."""
    return [filename for filename in os.listdir(path) if pdf_file(filename)]


def concat_pdf_pages(files):
    """A generator that yields one PDF page a time for all pages in the PDF files."""
    for input_file in files:
        for page in PdfFileReader(input_file).pages:
            yield page


def split_on_condition(iterable, predicate):
    """Split a iterable into chunks, where the first item in the chunk will be the
    evaluate to True with predicate function, and the rest of the items in the chunk
    evaluates to False."""
    it = iter(iterable)

    # Initialize the chunk list with an item
    # StopIteration will be thrown if there are no further items in the iterator
    chunk = [it.next()]

    while True:
        try:
            item = it.next()

            if predicate(item):
                # If the next item should be in a new chunk then return the current chunk
                yield chunk
                # Then rest the chunk list
                chunk = [item]
            else:
                # Simply append the item to current chunk if it doesn't match the predicate
                chunk.append(item)

        except StopIteration:
            # If the end of the iterator is reached then simply return the current chunk
            yield chunk
            break


def width_greater_than_height(page):
    box = page.mediaBox
    return box.getWidth() > box.getHeight()
