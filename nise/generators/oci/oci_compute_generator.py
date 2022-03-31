from random import choice
from datetime import datetime
from nise.generators.oci.oci_generator import OCIGenerator
from nise.generators.oci.oci_generator import OCI_COST_REPORT
from nise.generators.oci.oci_generator import OCI_USAGE_REPORT
from nise.generators.oci.oci_generator import OCI_COST_COLUMNS
from nise.generators.oci.oci_generator import OCI_USAGE_COLUMNS
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS


SERVICE = "COMPUTE"

class OCIComputeGenerator(OCIGenerator):
    """Generator for OCI Compute data."""

    SKU = (
        "B91445",
        "B91444",
        "B88327",
        "B91627"
        "B90926"    
    )

    def __init__(self, start_date, end_date, currency, report_type, attributes=None):
        """Initialize the compute generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.report_type = report_type
        self.service = SERVICE

    def _add_cost_data(self, row, start, end, **kwargs):
        """Add cost information to report."""
        for column in OCI_COST_COLUMNS:
            _data = self._get_compute_cost_data(**kwargs)
            row[column] = _data[column]
        return row

    def _get_compute_cost_data(self, **kwargs):
        _data = {
            "usage/billedQuantity":"",
            "usage/billedQuantityOverage":"",
            "cost/subscriptionId":"",
            "cost/productSku":"",
            "product/Description":"",
            "cost/unitPrice":"",
            "cost/unitPriceOverage":"",
            "cost/myCost":"",
            "cost/myCostOverage":"",
            "cost/currencyCode": self.currency,
            "cost/billingUnitReadable":"",
            "cost/skuUnitDescription":"",
            "cost/overageFlag":"",
        }
        return _data
    
    def _add_usage_data(self, row, start, end, **kwargs):
        """Add cost information to report."""
        for column in OCI_USAGE_COLUMNS:
            row[column] = ""
        return row

    def _update_data(self, row, start, end, **kwargs):
        """Update a data row with compute values."""
        row["product/service"] = self.service
        if self.report_type == OCI_COST_REPORT:
            row = self._add_cost_data(row, start, end, **kwargs)
        if self.report_type == OCI_USAGE_REPORT:
            row = self._add_usage_data(row, start, end, **kwargs)
        return row

    def generate_data(self, report_type=None, **kwargs):
        """Generate OCI compute data."""
        if report_type:
            kwargs.update({"report_type":report_type})
        return self._generate_hourly_data(**kwargs)
