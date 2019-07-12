

class WriteOnceDict(dict):
    def __init__(self):
        super(WriteOnceDict, self).__init__()

    def __setitem__(self, key, value):
        # key already set
        if key in super(WriteOnceDict, self).keys():
            pass
        # New key, set it:
        else:
            super(WriteOnceDict, self).__setitem__(key, value)

if __name__ == "__main__":
    d = WriteOnceDict()
    d["key"] = '1'
    d["key"] = '2'
    d["key2"] = '2'
    print(d)