from data_vendors.sharadar.sharadar import Sharadar
from data_vendors.mock_vendor.mock_vendor import MockVendor

def get_vendor_instance(vendor_name, **kwargs):
    """[summary]

    Args:
        vendor_name (str): vendor name

    Returns:
        [Vendor concrete instance]: instance of the abstract vendor class
    """

    if vendor_name == 'sharadar':
        return Sharadar(**kwargs)
    elif vendor_name == 'mock_vendor':
        return MockVendor(**kwargs)