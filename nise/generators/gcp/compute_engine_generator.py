"""Module for gcp compute engine data generation."""
from random import choice
from random import uniform

from nise.generators.gcp.gcp_generator import GCPGenerator


class ComputeEngineGenerator(GCPGenerator):
    """Generator for GCP Compute Engine data."""

    SERVICE = ("Compute Engine", "6F81-5844-456A") # Service Description and Service ID

    SKU = ( # (ID, Description, Usage Unit, Pricing Unit)
        ("D973-5D65-BAB2", "Storage PD Capacity", "byte-seconds", "gibibyte month" ),
        ("D0CC-50DF-59D2", "Network Inter Zone Ingress", "bytes", "gibibyte"),
        ("F449-33EC-A5EF", "E2 Instance Ram running in Americas", "byte-seconds", "gibibyte hour"),
        ("C054-7F72-A02E", "External IP Charge on a Standard VM", "seconds", "hour"),
        ("CF4E-A0C7-E3BF", "E2 Instances Core running in Americas", "seconds", "hour"),
        ("C0CF-3E3B-57FB", "Licensing Fee for Debian 10 Buster (CPU cost)", "seconds", "hour"),
        ("0C5C-D8E4-38C1", "Licensing Fee for Debian 10 Buster (CPU cost)", "seconds", "hour"),
        ("CD20-B4CA-0F7C", "Licensing Fee for Debian 10 Buster (RAM cost)","byte-seconds","gibiyte hour"),
        ("6B8F-E63D-832B", "Network Internet Egress from Americas to APAC", "bytes", "gibibyte"),
        ("DFA5-B5C6-36D6", "Network Internet Egress from Americas to EMEA", "bytes", "gibibyte"),
        ("9DE9-9092-B3BC", "Network Internet Egress from Americas to China", "bytes", "gibibyte"),
        ("7151-106A-2684", "Network Internet Ingress from APAC to Americas", "bytes", "gibibyte"),
        ("2F99-3A90-373B", "Network Internet Ingress from EMEA to Americas", "bytes", "gibibyte"),
        ("92CB-C25F-B1D1", "Network Google Egress from Americas to Americas", "bytes", "gibibyte"),
        ("227B-5B2B-A75A", "Network Internet Ingress from China to Americas", "bytes", "gibibyte"),
        ("123C-0EFC-B7C8", "Network Google Ingress from Americas to Americas", "bytes", "gibibyte"),
        ("F274-1692-F213", "Network Internet Engress from Americas to Americas", "bytes", "gibibyte"),
        ("92CB-C25F-B1D1", "Network Google Egress from Americas to Americas", "bytes", "gibibyte"), # Left off at 125
    )

    LABELS = (
        ("[{'key': 'vm_key_proj2', 'value': 'vm_label_proj2'}]"),
        ("[]"),
    )

    SYSTEM_LABELS = (
        ("[{'key': 'compute.googleapis.com/cores', 'value': '2'}, {'key': 'compute.googleapis.com/machine_spec', 'value': 'e2-medium'}, {'key': 'compute.googleapis.com/memory', 'value': '4096'}]"),
        ("[]"),
    )

    def _update_data(self, row):
        """Update a data row with compute values."""
        if self.attributes:
            row["Cost"] = self.attributes["Cost"]
            row["Currency"] = self.attributes["Currency"]

        else:
            sku = choice(self.SKU)
            row["Service Description"] = self.SERVICE[0]
            row["Service ID"] = self.SERVICE[1]
            row["SKU ID"] = sku[0]
            row["SKU Description"]= sku[1]
            row["Cost"] = round(uniform(0,0.01),7) #self.fake.pydecimal(right_digits=6,positive=True,max_value = 1)
            usage_unit = sku[2]
            pricing_unit = sku[3]
            row["Usage Unit"] = usage_unit
            row["Pricing Unit"] = pricing_unit
            row["Labels"] = choice(self.LABELS)
            row["System Labels"] = choice(self.SYSTEM_LABELS)

            # All upper and lower bound values were estimated for each unit
            if usage_unit == "byte-seconds":
                amount = self.fake.pyint(min_value=10000000000, max_value=10000000000000)
                row["Usage Amount"] = amount
                if pricing_unit == "gibibyte month":
                    row["Usage Amount in Pricing Units"] = amount * 0.00244752
                elif pricing_unit == "gibibyte hour":
                    row["Usage Amount in Pricing Units"] = amount * (3.3528*10**-6)
            elif usage_unit == "bytes": 
                amount = self.fake.pyint(min_value=1000, max_value=10000000)
                row["Usage Amount"] = amount
                if pricing_unit == "gibibyte":
                    row["Usage Amount in Pricing Units"] = amount * (9.31323*10**-0)
            elif usage_unit == "seconds":
                amount = self.fake.pyfloat(max_value=3600, positive=True) 
                row["Usage Amount"] = amount
                if pricing_unit == "hour":
                    row["Usage Amount in Pricing Units"] = amount / 3600.00
            else:
                row["Usage Amount"] = 0
            row["Credits"] = "[]"
            row["Cost Type"] = "regular"
            row["Currency"] = "USD" #self.fake.currency()[0] 
            row["Currency Conversion Rate"] = 1
            row["Invoice Month"] = "{}{}".format(self.start_date.year, self.start_date.month)
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        days = self._create_days_list(self.start_date, self.end_date)
        data = {}
        for day in days:
            rows = []
            for _ in range(self.num_instances):
                row = self._init_data_row(day["start"], day["end"])
                row = self._update_data(row)
                rows.append(row)
            data[day["start"]] = rows
        return data
