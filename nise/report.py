"""Module responsible for generating the cost and usage report."""
import csv

from faker import Faker

from nise.generators import (COLUMNS,
                             DataTransferGenerator,
                             EBSGenerator,
                             EC2Generator,
                             S3Generator)


def _write_csv(output_file, data, header=COLUMNS):
    """Output csv file data."""
    with output_file as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def create_report(output_file, options):
    """Create a cost usage report file."""
    generators = [DataTransferGenerator, EBSGenerator, EC2Generator, S3Generator]
    data = []
    start_date = options.get('start_date')
    end_date = options.get('end_date')
    fake = Faker()
    payer_account = fake.ean(length=13)  # pylint: disable=no-member
    for generator in generators:
        gen = generator(start_date, end_date, payer_account)
        data += gen.generate_data()

    _write_csv(output_file, data)
