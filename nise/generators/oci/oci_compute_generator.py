from datetime import datetime
from nise.generators.oci.oci_generator import OCIGenerator
from nise.generators.oci.oci_generator import OCI_COST_REPORT
from nise.generators.oci.oci_generator import OCI_USAGE_REPORT
from nise.generators.oci.oci_generator import OCI_COST_COLUMNS
from nise.generators.oci.oci_generator import OCI_USAGE_COLUMNS
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS


class OCIComputeGenerator(OCIGenerator):
    """Generator for OCI Compute data."""

    def __init__(self, start_date, end_date, currency, report_type, attributes=None):
        """Initialize the compute generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.report_type = report_type
        self.service = "COMPUTE"
        self.resource_id = f"ocid1.instance.oci.{self.product_region}.{self.fake.pystr(min_chars=25, max_chars=35)}"
        self.product_sku = f"B{self.fake.random_number(fix_len=True, digits=5)}"
        self.product_description  = "Virtual Machine Standard - E2 Micro - Free"
        self.billing_unit = "ONE HOURS OCPUS"
        self.cost_sku_unit = "OCPU Hours"


    def _add_cost_data(self, row, start, end, **kwargs):
        """Add cost information to report."""
        for column in OCI_COST_COLUMNS:
            _data = self._get_compute_cost_data(**kwargs)
            row[column] = _data[column]
        return row

    def _get_compute_cost_data(self, **kwargs):
        _data = {
            "usage/billedQuantity": 1,
            "usage/billedQuantityOverage":"",
            "cost/subscriptionId": self.subscription_id,
            "cost/productSku": self.product_sku,
            "product/Description": self.product_description,
            "cost/unitPrice":"",
            "cost/unitPriceOverage":"",
            "cost/myCost": 0,
            "cost/myCostOverage":"",
            "cost/currencyCode": self.currency,
            "cost/billingUnitReadable": self.billing_unit,
            "cost/skuUnitDescription": self.cost_sku_unit,
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
        row["product/resourceId"] = self.resource_id
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
