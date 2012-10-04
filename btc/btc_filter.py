import argparse
import fnmatch
import sys
import re
from btc import encoder, decoder, error

_description = 'filter elements of a list'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nth', metavar='N',
                        help='select the Nth entry (1-based)',
                        type=int, default=None)
    parser.add_argument('-f', '--first', metavar='N',
                        help='select the N first entires',
                        type=int, default=None)
    parser.add_argument('-v', '--invert-match', default=False, action='store_true',
                        help='select all entries but the ones that match')
    parser.add_argument('-k', '--key', default='name',
                        help='change the key used for the match (default is name)')
    parser.add_argument('-s', '--case-sensitive', default=False, action='store_true')

    parser.add_argument('value', metavar='VALUE', nargs='?', default=None,
                        help='string to match if no numeric or boolean operator is used')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-e', '--numeric-equals', default=False, action='store_true')
    group.add_argument('-d', '--numeric-differs', default=False, action='store_true')
    group.add_argument('-G', '--greater', default=False, action='store_true')
    group.add_argument('-g', '--greater-or-equal', default=False, action='store_true')
    group.add_argument('-l', '--less-or-equal', default=False, action='store_true')
    group.add_argument('-L', '--less', default=False, action='store_true')
    group.add_argument('-T', '--true', default=False, action='store_true')
    group.add_argument('-F', '--false', default=False, action='store_true')

    args = parser.parse_args()

    if (args.value is not None) and (args.false or args.true):
        parser.error('cannot specify value for boolean matching')

    if sys.stdin.isatty():
        error('no input')
    l = sys.stdin.read()

    if len(l.strip()) == 0:
        exit(0)

    try:
        l = decoder.decode(l)
    except ValueError:
        error('unexpected input: %s' % l)

    new = list()
    for o in l:
        try:
            if args.numeric_equals:
                if float(o[args.key]) == float(args.value):
                    new.append(o)
            elif args.numeric_differs:
                if float(o[args.key]) != float(args.value):
                    new.append(o)
            elif args.greater:
                if float(o[args.key]) > float(args.value):
                    new.append(o)
            elif args.greater_or_equal:
                if float(o[args.key]) >= float(args.value):
                    new.append(o)
            elif args.less_or_equal:
                if float(o[args.key]) <= float(args.value):
                    new.append(o)
            elif args.less:
                if float(o[args.key]) < float(args.value):
                    new.append(o)
            elif args.true:
                if bool(o[args.key]):
                    new.append(o)
            elif args.false:
                if not bool(o[args.key]):
                    new.append(o)
            elif args.value is not None:
                def case(x):
                    if args.case_sensitive:
                        return x
                    return x.lower()
                if fnmatch.fnmatch(case(str(o[args.key])), case(args.value)):
                    new.append(o)
            else:
                new.append(o)
        except KeyError:
            pass
        except ValueError as e:
            error(e.message)

    if args.first is not None:
        new = new[0:min(args.first,len(new))]

    if args.nth is not None:
        new = [new[args.nth - 1]]

    if args.invert_match:
        new = [o for o in l if o not in new]

    print encoder.encode(new)

if __name__ == '__main__':
    main()
