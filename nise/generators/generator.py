"""Defines the abstract generator."""
import datetime
from abc import ABC, abstractmethod
from random import choice

from faker import Faker


IDENTITY_COLS = ('identity/LineItemId', 'identity/TimeInterval')
BILL_COLS = ('bill/InvoiceId', 'bill/BillingEntity', 'bill/BillType',
             'bill/PayerAccountId', 'bill/BillingPeriodStartDate',
             'bill/BillingPeriodEndDate')
LINE_ITEM_COLS = ('lineItem/UsageAccountId',
                  'lineItem/LineItemType', 'lineItem/UsageStartDate',
                  'lineItem/UsageEndDate', 'lineItem/ProductCode',
                  'lineItem/UsageType', 'lineItem/Operation',
                  'lineItem/AvailabilityZone', 'lineItem/ResourceId',
                  'lineItem/UsageAmount', 'lineItem/NormalizationFactor',
                  'lineItem/NormalizedUsageAmount', 'lineItem/CurrencyCode',
                  'lineItem/UnblendedRate', 'lineItem/UnblendedCost',
                  'lineItem/BlendedRate', 'lineItem/BlendedCost',
                  'lineItem/LineItemDescription', 'lineItem/TaxType')
PRODUCT_COLS = ('product/ProductName', 'product/accountAssistance',
                'product/architecturalReview', 'product/architectureSupport',
                'product/availability', 'product/bestPractices',
                'product/caseSeverityresponseTimes', 'product/clockSpeed',
                'product/comments', 'product/contentType',
                'product/currentGeneration',
                'product/customerServiceAndCommunities',
                'product/databaseEngine', 'product/dedicatedEbsThroughput',
                'product/deploymentOption', 'product/description',
                'product/directorySize', 'product/directoryType',
                'product/directoryTypeDescription', 'product/durability',
                'product/ebsOptimized', 'product/ecu', 'product/endpointType',
                'product/engineCode', 'product/enhancedNetworkingSupported',
                'product/feeCode', 'product/feeDescription',
                'product/fromLocation', 'product/fromLocationType',
                'product/group', 'product/groupDescription',
                'product/includedServices', 'product/instanceFamily',
                'product/instanceType', 'product/isshadow',
                'product/iswebsocket', 'product/launchSupport',
                'product/licenseModel', 'product/location',
                'product/locationType', 'product/maxIopsBurstPerformance',
                'product/maxIopsvolume', 'product/maxThroughputvolume',
                'product/maxVolumeSize', 'product/memory', 'product/memoryGib',
                'product/messageDeliveryFrequency',
                'product/messageDeliveryOrder', 'product/minVolumeSize',
                'product/networkPerformance', 'product/operatingSystem',
                'product/operation', 'product/operationsSupport',
                'product/origin', 'product/physicalProcessor',
                'product/preInstalledSw', 'product/proactiveGuidance',
                'product/processorArchitecture', 'product/processorFeatures',
                'product/productFamily', 'product/programmaticCaseManagement',
                'product/protocol', 'product/provisioned', 'product/queueType',
                'product/recipient', 'product/requestDescription',
                'product/requestType', 'product/resourceEndpoint',
                'product/routingTarget', 'product/routingType',
                'product/servicecode', 'product/sku', 'product/softwareType',
                'product/storage', 'product/storageClass',
                'product/storageMedia', 'product/storageType',
                'product/technicalSupport', 'product/tenancy',
                'product/thirdpartySoftwareSupport', 'product/toLocation',
                'product/toLocationType', 'product/training',
                'product/transferType', 'product/usagetype', 'product/vcpu',
                'product/version', 'product/virtualInterfaceType',
                'product/volumeType', 'product/whoCanOpenCases')
PRICING_COLS = ('pricing/LeaseContractLength', 'pricing/OfferingClass'
                'pricing/PurchaseOption', 'pricing/publicOnDemandCost',
                'pricing/publicOnDemandRate', 'pricing/term', 'pricing/unit')
RESERVE_COLS = ('reservation/AvailabilityZone',
                'reservation/NormalizedUnitsPerReservation',
                'reservation/NumberOfReservations',
                'reservation/ReservationARN',
                'reservation/TotalReservedNormalizedUnits',
                'reservation/TotalReservedUnits',
                'reservation/UnitsPerReservation')
COLUMNS = (IDENTITY_COLS + BILL_COLS + LINE_ITEM_COLS +
           PRODUCT_COLS + PRICING_COLS + RESERVE_COLS)


# pylint: disable=too-few-public-methods
class AbstractGenerator(ABC):
    """Defines a abstract class for generators."""

    REGIONS = (
        ('US East (N. Virginia)', 'us-east-1a', 'USE1-EBS'),
        ('US East (N. Virginia)', 'us-east-1b', 'USE1-EBS'),
        ('US West (N. California)', 'us-west-1a', 'USW1-EBS'),
        ('US West (N. California)', 'us-west-1b', 'USW1-EBS'),
        ('US West (Oregon)', 'us-west-2a', 'USW2-EBS'),
        ('US West (Oregon)', 'us-west-2b', 'USW2-EBS'),
    )

    def __init__(self, start_date, end_date, payer_account):
        """Initialize the generator."""
        self.start_date = start_date
        self.end_date = end_date
        self.payer_account = payer_account
        self.hours = self._set_hours()
        self.fake = Faker()
        super().__init__()

    def _set_hours(self):
        """Create a list of hours between the start and end dates."""
        hours = []
        if not self.start_date or not self.end_date:
            raise ValueError('start_date and end_date must be date objects.')
        if not isinstance(self.start_date, datetime.datetime):
            raise ValueError('start_date must be a date object.')
        if not isinstance(self.end_date, datetime.datetime):
            raise ValueError('end_date must be a date object.')
        if self.end_date < self.start_date:
            raise ValueError('start_date must be a date object less than end_date.')

        one_hour = datetime.timedelta(minutes=60)
        cur_date = self.start_date
        while (cur_date + one_hour) < self.end_date:
            cur_hours = {'start': cur_date, 'end': cur_date + one_hour}
            hours.append(cur_hours)
            cur_date = cur_date + one_hour
        return hours

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not in_date or not isinstance(in_date, datetime.datetime):
            raise ValueError('in_date must be a date object.')
        return in_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def time_interval(start, end):
        """Create a time interval string from input dates."""
        start_str = AbstractGenerator.timestamp(start)
        end_str = AbstractGenerator.timestamp(end)
        time_interval = str(start_str) + '/' + str(end_str)
        return time_interval

    @staticmethod
    def next_month(in_date):
        """Return the first of the next month from the in_date."""
        dt_first = in_date.replace(day=1)
        dt_up_month = dt_first + datetime.timedelta(days=32)
        dt_next_month = dt_up_month.replace(day=1)
        return dt_next_month

    def _init_data_row(self, start, end):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not start or not end:
            raise ValueError('start and end must be date objects.')
        if not isinstance(start, datetime.datetime):
            raise ValueError('start must be a date object.')
        if not isinstance(end, datetime.datetime):
            raise ValueError('end must be a date object.')

        bill_begin = start.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        bill_end = AbstractGenerator.next_month(bill_begin)
        row = {}
        for column in COLUMNS:
            row[column] = ''
            if column == 'identity/LineItemId':
                # pylint: disable=no-member
                row[column] = self.fake.sha1(raw_output=False)
            elif column == 'identity/TimeInterval':
                row[column] = AbstractGenerator.time_interval(start, end)
            elif column == 'bill/BillingEntity':
                row[column] = 'AWS'
            elif column == 'bill/BillType':
                row[column] = 'Anniversary'
            elif column == 'bill/PayerAccountId':
                row[column] = self.payer_account
            elif column == 'bill/BillingPeriodStartDate':
                row[column] = AbstractGenerator.timestamp(bill_begin)
            elif column == 'bill/BillingPeriodEndDate':
                row[column] = AbstractGenerator.timestamp(bill_end)
        return row

    def _get_location(self):
        """Pick instance location."""
        return choice(self.REGIONS)

    def _add_common_usage_info(self, row, start):
        """Add common usage information."""
        usage_start = start.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        usage_end = AbstractGenerator.next_month(usage_start)
        row['lineItem/UsageAccountId'] = self.payer_account
        row['lineItem/LineItemType'] = 'Usage'
        row['lineItem/UsageStartDate'] = usage_start
        row['lineItem/UsageEndDate'] = usage_end
        return row

    @abstractmethod
    def _update_data(self, row, start, end):
        """Update data with generator specific data."""
        pass

    def _generate_hourly_data(self):
        """Create houldy data."""
        data = []
        for hour in self.hours:
            start = hour.get('start')
            end = hour.get('end')
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            data.append(row)
        return data

    @abstractmethod
    def generate_data(self):
        """Responsibile for generating data."""
        pass
