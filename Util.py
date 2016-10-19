"""Collection of Helper Functions"""
import logging
import operator as op
import os
from fnmatch import fnmatch

from PyPDF2 import PdfFileReader

# Get default logger
log = logging.getLogger(__name__)


def pdf_file(filename):
    """Test whether or the the filename ends with '.pdf'."""
    return fnmatch(filename, '*.pdf')


def all_pdf_files_in_directory(path):
    """Return a list of of PDF files in a directory."""
    return sorted([filename for filename in os.listdir(path) if pdf_file(filename)])


def concat_pdf_pages(files):
    """A generator that yields one PDF page a time for all pages in the PDF files."""
    for input_file in files:
        for page in PdfFileReader(input_file).pages:
            yield page


def merge_with_next(iterable, predicate, merger=op.add):
    """Merge an item with the next in the iterable if the item evaluates to True with
    the predicate function. Will merge at most once for an item."""
    it = iter(iterable)

    while True:
        item = it.next()

        if predicate(item):
            try:
                next_item = it.next()
                item = merger(item, next_item)
            except StopIteration:
                yield item
                break

        yield item


def split_on(iterable, predicate):
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


def is_landscape(page):
    """Check whether or not a page is in landscape orientation."""
    box = page.mediaBox
    return box.getWidth() > box.getHeight()


def write_pdf_file(output_filename, pdf_writer):
    """Helper function for writing all the pages in PDFWriter to a file on disk."""
    with open(output_filename, 'wb') as output_file:
        pdf_writer.write(output_file)

        # Extra measures to make sure data is written to disk
        output_file.flush()
        os.fsync(output_file.fileno())


def add_pages(pdf_writer, pages_to_write, to_log=True):
    """Add the PDF pages in a iterable into the specified PDFWriter."""
    for page in pages_to_write:
        if to_log:
            log.debug('    Adding page %s', repr(page))
            log.debug('                Image: %s', image_data_info(page))
        pdf_writer.addPage(page)

    if to_log:
        log.info('Added %d pages to PDFWriter', pdf_writer.getNumPages())


def make_pagenum_even(writer):
    """Helper function that append a blank page if the number of page is an odd number, in order to make the
    page number even."""
    if writer.getNumPages() % 2 == 1:
        log.info('    Adding a blank page')
        writer.addBlankPage()
        # TODO: Fix blank page orientation bug
        # Problem: if the only page in this writer was originally in landscape orientation, a new blank page will
        # be in landscape orientation too.
        # But it should be rare that a writer has only one page in it, thus not a big problem.
        # Solution: takes the rotation of the only page in the PDF writer into account, or have a predefined page
        # width &


def image_data_info(page):
    """Return the dimension and file size of the first image encountered in the specified PDF page."""
    try:
        xObject = page['/Resources']['/XObject'].getObject()
    except KeyError:
        return None

    for obj_key in xObject:
        obj = xObject[obj_key]
        if obj['/Subtype'] == '/Image':
            width, height = (obj['/Width'], obj['/Height'])
            num_bytes = len(obj._data)
            density = num_bytes * 1.0 / (width * height)
            return {'width': width, 'height': height, 'size': num_bytes, 'density': density}


def detect_blank_page(page, min_density):
    """Return True if the specified PDF page's first image have a density (size/dimension) lower than the specified
    threshold, as image with that property is considered to be a blank page."""
    info = image_data_info(page)
    if info and info['density'] < min_density:
        log.debug('    Skipping page %s', repr(page))
        log.debug('             because image density is %F, lower than threshold of %F', info['density'], min_density)
        return False
    return True
