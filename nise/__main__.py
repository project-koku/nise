"""Cost and Usage Generator CLI."""

import argparse
import datetime

from nise.report import create_report


def valid_date(date_string):
    """Create date from date string."""
    try:
        valid = datetime.datetime.strptime(date_string, '%m-%d-%Y')
    except ValueError:
        msg = '{} is an unsupported date format.'.format(date_string)
        raise argparse.ArgumentTypeError(msg)
    return valid


def today():
    """Create the date of today."""
    return datetime.datetime.now().replace(microsecond=0, second=0, minute=0)


def create_parser():
    """Create the parser for incoming data."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date',
                        metavar='DATE',
                        dest='start_date',
                        required=True,
                        type=valid_date,
                        help='Date to start generating data (MM-DD-YYYY)')
    parser.add_argument('--end-date',
                        metavar='DATE',
                        dest='end_date',
                        required=False,
                        type=valid_date,
                        default=today(),
                        help='Date to end generating data (MM-DD-YYYY). Default is today.')
    parser.add_argument('--output-file',
                        metavar='FILE',
                        dest='output_file',
                        required=True,
                        type=argparse.FileType('w'),
                        help='Generated output file')
    return parser


def main():
    """Run data generation program."""
    parser = create_parser()
    args = parser.parse_args()
    options = vars(args)
    create_report(args.output_file, options)


if __name__ == '__main__':
    main()
