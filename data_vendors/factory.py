from sharadar.sharadar import Sharadar

def get_vendor_instance(vendor_name):
    """[summary]

    Args:
        vendor_name (str): vendor name

    Returns:
        [Vendor concrete instance]: instance of the abstract vendor class
    """

    if vendor_name == 'sharadar':
        return Sharadar()