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
        self.service_name = "COMPUTE"
        self.resource_id = f"ocid1.instance.oci.{self.product_region}.{self.fake.pystr(min_chars=25, max_chars=35)}"
        self.product_sku = f"B{self.fake.random_number(fix_len=True, digits=5)}"
        self.product_description  = "Virtual Machine Standard - E2 Micro - Free"
        self.billing_unit = "ONE HOURS OCPUS"
        self.cost_sku_unit = "OCPU Hours"
        self.consumed_quantity = self.fake.random_number(digits=9, fix_len=True)
        self.billed_quantity = self.fake.random_number(digits=9, fix_len=True)
        self.consumed_quant_units = "GB_MS"
        self.consumed_quant_measure = "STORAGE_SIZE"


    def _add_cost_data(self, row, start, end, **kwargs):
        """Add cost information to report."""
        _data = self._get_cost_data(**kwargs)
        for column in OCI_COST_COLUMNS:
            row[column] = _data[column]
        return row

    def _get_cost_data(self, **kwargs):
        """Get compute cost data"""

        _cost_data = {
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
        return _cost_data
    
    def _add_usage_data(self, row, start, end, **kwargs):
        """Add cost information to report."""
        row['product/resource'] = "PIC_COMPUTE_VM_STANDARD_E2_MICRO_FREE"
        _data = self._get_usage_data(**kwargs)
        for column in OCI_USAGE_COLUMNS:
            row[column] = _data[column]
        return row
    
    def _get_usage_data(self, **kwargs):
        """Get compute usage data"""
        _usage_data = {
            'usage/consumedQuantity': self.consumed_quantity, 
            'usage/billedQuantity': self.billed_quantity, 
            'usage/consumedQuantityUnits': self.consumed_quant_units, 
            'usage/consumedQuantityMeasure': self.consumed_quant_measure
        }
        return _usage_data

    def _update_data(self, row, start, end, **kwargs):
        """Update a data row with compute values."""
        row["product/service"] = self.service_name
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
