
import argparse
import bibtexparser
import os

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


def fixKey(ent):
    names = bibtexparser.customization.splitname(splitNames(ent['author'])[0])
    return '{}{}'.format(names['last'][0], ent['year'])


def main():
    parser = argparse.ArgumentParser(description = 'Replace BibTex keys with author last name and year.')

    parser.add_argument('-o', '--ofname', default='',
                        help = 'Name of file to write. If this argument is left out, in_file is rewritten.')

    parser.add_argument('in_file', help = 'Name of file to read.')

    args = parser.parse_args()

    print('Reading bibfile:\t\t  {}'.format(os.path.basename(args.in_file)))
    with open(args.in_file, 'r') as bibtex_file:
        bibDatabase = bibtexparser.load(bibtex_file)

    for ent in bibDatabase.entries:
        ent['ID'] = fixKey(ent)

    if args.ofname == '':
        ofname = args.in_file
    else:
        ofname = args.ofname

    print('Writing fixed bibfile to: {}'.format(os.path.basename(ofname)))
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(ofname, 'w') as bibfile:
        bibfile.write(writer.write(bibDatabase))


if __name__ == '__main__':
    main()
