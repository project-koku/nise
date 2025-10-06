import calendar
from nise.util.constants import SECONDS_IN_HOUR
from nise.util.constants import BYTES_TO_GIBIBYTE


def gcp_calculate_persistent_disk_usage_amount(capacity):
    bytes_conversion = capacity * BYTES_TO_GIBIBYTE
    return bytes_conversion * SECONDS_IN_HOUR


def gcp_calculate_usage_amount_in_pricing(usage_date, usage_amount):
    hours_in_month = calendar.monthrange(usage_date.year, usage_date.month)[1] * 24
    seconds_in_month = hours_in_month * SECONDS_IN_HOUR
    usage_in_pricing = usage_amount / (BYTES_TO_GIBIBYTE * seconds_in_month)
    return round(usage_in_pricing, 8)
