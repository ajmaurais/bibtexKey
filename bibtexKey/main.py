
import argparse
import bibtexparser
import sys
import os
from shutil import copy
from collections import OrderedDict

def splitNames(name_str):
    """
    Split author field into a list of "Name, Surname".

    :param name_str: the record.
    :type name_str: str
    :returns: list -- list of author names

    ..Note::More sensible version of bibtexparser Author function
    which doesn't take record as a argument.

    """

    ret = bibtexparser.customization.getnames([i.strip() for i in name_str.replace('\n', ' ').split(" and ")])

    return ret


def fixKey(ent, verbose=False):
    try:
        names = bibtexparser.customization.splitname(splitNames(ent['author'])[0])
        key = '{}{}'.format(names['last'][0], ent['year'])
    except KeyError:
        if verbose:
            sys.stderr.write('WARN: Could not find author field for entry!')
            for k, v in ent.items():
                sys.stderr.write('\n\t{}: {}'.format(k, v))
            sys.stderr.write('\n')
        key = ent['ID']
    return key


def refEqual(rhs, lhs):
    try:
        for key in rhs.keys():
            if rhs[key] != lhs[key]:
                return False
    except KeyError:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description = 'Replace BibTex keys with author last name and year.')

    parser.add_argument('-o', '--ofname', default='',
                        help = 'Name of file to write. If this argument is left out, in_file is rewritten.')

    parser.add_argument('-a', '--alphabetize', default=False, action='store_true',
                        help='Should entries in new bib be alphabetized? Default is false.')

    parser.add_argument('-v', '--verbose', choices=[0, 1], default=0, help='Verbose output?')

    parser.add_argument('in_file', help = 'Name of file to read.')

    args = parser.parse_args()

    print('Reading bibfile:\t\t  {}'.format(os.path.basename(args.in_file)))
    copy(args.in_file, '{}.bak'.format(args.in_file))
    with open(args.in_file, 'r') as bibtex_file:
        bibDatabase = bibtexparser.load(bibtex_file)

    new_bib = OrderedDict()
    for ent in bibDatabase.entries:
        key = fixKey(ent, args.verbose)
        ent['ID'] = key
        if key in new_bib:
            if refEqual(ent, new_bib[key]):
                if args.verbose:
                    sys.stderr.write('WARN: found duplicate entries!')
                    for k, v in ent.items():
                        sys.stderr.write('\t{}: {}, {}\n'.format(k, v, new_bib[key][k]))

            else:
                for i in range(ord('a'), ord('z')):
                    new_key = '{}{}'.format(key, chr(i))
                    if new_key not in new_bib:
                        ent['ID'] = new_key
                        key = new_key
                        break
                if ent['ID'] in new_bib:
                    raise RuntimeError('Ran out of possible key postfixes:\n\t{}\n'.format(ent))
        new_bib[key] = ent

    if args.ofname == '':
        ofname = args.in_file
    else:
        ofname = args.ofname

    # make new bib db
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = list(new_bib.values())

    # write new db
    print('Writing fixed bibfile to: {}'.format(os.path.basename(ofname)))
    writer = bibtexparser.bwriter.BibTexWriter()
    if not args.alphabetize:
        writer.order_entries_by = None
    with open(ofname, 'w') as bibfile:
        bibfile.write(writer.write(db))


if __name__ == '__main__':
    main()

