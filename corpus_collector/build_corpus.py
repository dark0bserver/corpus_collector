"""
Copyright (c) 2019 dark0bserver, https://medium.com/@dark0bserver

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import requests
import json
import boto3
import gzip
import io


def get_warc_indices_for_domain(
        domain,
        index='CC-MAIN-2019-39-index',
        limit=None):
    """
    Get the list of WARC indicies for a domain of interest.

    domain -- Domain of interest in the form of example.com or sub.example.com
    index -- Common crawl index to search (default CC-MAIN-2019-39-index)
    limit -- maximum number of pages to randomly pull from index
                (default 'None' meaning all of them)
    """
    api_url = f"https://index.commoncrawl.org/{index}"

    params = {
        'url': f'{domain}/*',
        'output': 'json',
        'filter': 'mime:text/html'
    }

    if limit:
        params['limit'] = limit

    response = requests.get(
        api_url,
        params
    )

    for line in response.text.split('\n'):
        if line:
            yield json.loads(line)


def get_text_for_index(index):
    """
    Given an index blob as returned from CC index,
    return a text blob representing the WET content
    (WARC Extracted Text) for the index.
    """
    warc_url = index['filename']
    wet_url = warc_url.replace(
        '/warc/', '/wet/').replace(
            'warc.gz', 'warc.wet.gz')

    results = dict()

    url = index['url']
    target_uri = f'WARC-Target-URI: {url}'

    s3 = boto3.client('s3')
    blob = s3.get_object(Bucket='commoncrawl', Key=wet_url)

    with gzip.GzipFile(fileobj=io.BytesIO(blob['Body'].read())) as f:
        for rawline in f:
            line = rawline.decode('utf-8').strip()
            if line == target_uri:
                while "Content-Length:" not in line:
                    line = f.readline().decode('utf-8')
                f.readline()
                content_length = int(line.split(' ')[1])
                results = {
                    'url': url,
                    'content': f.read(content_length).decode('utf-8')
                }

                break

    return results
