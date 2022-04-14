#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A script that downloads show archives from https://archives.nsbradio.co.uk/.
"""

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
import argparse
import os
import threading
import urllib.request


class ShowInfo:
    """Object that stores main show information."""

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return 'name : {}, url : {};'.format(self.name, self.url)


def create_directory_if_not_exists(directory):
    """
    

    Parameters
    ----------
    directory : str
        The script's output directory.

    Returns
    -------
    None.

    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_html_content(url):
    """
    

    Parameters
    ----------
    url : str
        Show archive URL.

    Returns
    -------
    result : str
        Show archive HTML page.

    """
    stream = urllib.request.urlopen(url)
    binary_content = stream.read()
    result = binary_content.decode('utf8')
    stream.close()
    return result


def get_show_info(html, url):
    """
    

    Parameters
    ----------
    html : str
        Show archive HTML page.
    url : str
        Show archive URL.

    Returns
    -------
    result : list of ShowInfo
        List of ShowInfo objects.

    """
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    base_url = urljoin(url, urlparse(url).path)

    for i in soup.find_all('a', {'class': 'noBreak'}):
        show_url = urljoin(base_url, i['href'])
        name = parse_qs(urlparse(show_url).query)['file'][0]
        show_info = ShowInfo(name, show_url)
        result.append(show_info)

    return result


def get_chunks(lst, chunk_size):
    """
    

    Parameters
    ----------
    lst : list
        Any list.
    chunk_size : int
        Chunk size.

    Returns
    -------
    list
        List divided by chunks of equal length. 
        Last chunk will be shrinked down to the number of remaining elements.

    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst),
            chunk_size)]


def process_shows(shows, path, threads):
    """
    

    Parameters
    ----------
    shows : list of ShowInfo
        List of shows.
    path : str
        The script's output directory.
    threads : int
        number of simultaneous threads.

    Returns
    -------
    None.

    """
    for chunk in get_chunks(shows, threads):
        threads = []
        for item in range(len(chunk)):
            thread = threading.Thread(
                target=download_show,
                args=(chunk[item], path)
            )
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


def download_show(show, path):
    """
    

    Parameters
    ----------
    show : ShowInfo
        Show to be downloaded.
    path : str
        The script's output directory.

    Returns
    -------
    None.

    """
    file = Path(path, show.name)

    if file.is_file():
        print ('file {} already exists'.format(show.name))
        return

    print ('downloading {} ...'.format(show.name))

    urllib.request.urlretrieve(show.url, file.absolute())

    print ('{} has been downloaded'.format(show.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        type=str,
        help="show archive URL, i.e. https://archives.nsbradio.co.uk/index.php?dir=The%20JJPinkman%20Show/",
    )
    parser.add_argument("-o", type=str, help="output directory, i.e. C:\\music")
    parser.add_argument("-d", type=int, help="number of simultaneous downloads")

    args = parser.parse_args()
    create_directory_if_not_exists(args.o)
    html = get_html_content(args.u)
    shows = get_show_info(html, args.u)
    process_shows(shows, args.o, args.d)
