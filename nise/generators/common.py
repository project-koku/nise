from collections import UserDict

class SameLengthDict(UserDict):
    """
    SameLengthDict is used to build dictionaries where the length of the values
    much match for each key. All values must be an iterable.

    This class can be used when the indexes of the values correspond to the same index
    in the value for a diffent key.

    Example:
        SameLengthDict(
            {
                'key1': ('v1', 'v2', 'v3'),
                'key2': (
                    'corresponds to index 0 of key1 and key3',
                    'corresponds to index 1 of key1 and key2',
                    'corresponds to index 2 of key1 and key2',
                ),
                'key3': ('corresponds to index 0 of key1 and key2', etc...),
                etc...
            }
    """

    def __init__(self, val=None):
        self.length = 0
        if val is None:
            val = {}
        super().__init__(val)

    def __setitem__(self, item, value):
        if self.length == 0 and len(value) > 0:
            self.length = len(value)
        super().__setitem__(item, value)
        assert len(value) == self.length