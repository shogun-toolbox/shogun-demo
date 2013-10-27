def read_description(filename):
    return file(filename[:filename.rindex('.')] + '.desc').read()
