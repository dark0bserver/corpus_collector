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

import os
import json
import argparse
import random
import botocore
from corpus_collector.build_corpus import get_warc_indices_for_domain
from corpus_collector.build_corpus import get_text_for_index


def main():
    """
    Basic commandline handler
    """

    parser = argparse.ArgumentParser(
        description="Tool for sampling domain text from Common Crawl dataset.")
    parser.add_argument('domain',
                        help='domain of interest')
    parser.add_argument('--outfile',
                        default=None,
                        help='.jsonl file to write results to, \
                            default <domain>_corpus.jsonl')
    parser.add_argument('--indexfile',
                        default=None,
                        help='intermediate file for CC \
                            indices (uncached by default)')
    parser.add_argument('--limit', type=int,
                        default=10,
                        help='number of pages to extract (default 10)')
    args = parser.parse_args()

    # populate dynamic default args
    if args.outfile is None:
        args.outfile = f'{args.domain}_corpus.jsonl'

    # check to load indices from local file (cached)
    # if not (but index file was specified), store retrieved indices
    indices = list()
    if args.indexfile:
        if os.path.exists(args.indexfile):
            with open(args.indexfile, 'r') as infile:
                indices = json.loads(infile.read())
        else:
            indices = list(get_warc_indices_for_domain(args.domain))
            with open(args.indexfile, 'w') as outfile:
                outfile.write(json.dumps(indices))
    else:
        indices = list(get_warc_indices_for_domain(args.domain))

    # select random 'limit' number of indices
    # Retrieve their text and write
    # these out to corpus jsonl file
    with open(args.outfile, 'w') as outfile:

        # sample returned indices to 'limit' (where they exceed 'limit')
        sampled_indices = indices
        if args.limit < len(indices):
            sampled_indices = random.sample(indices, args.limit)

        # for each sampled index, get stored page text by URL
        for index in sampled_indices:
            try:
                outfile.write(json.dumps(
                    get_text_for_index(index)) + '\n')
            except botocore.exceptions.ClientError as e:
                print(f'Error retrieving: {index} | {e}')


if __name__ == "__main__":
    main()
