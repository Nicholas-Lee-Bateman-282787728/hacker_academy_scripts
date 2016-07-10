# Returns a table of the contents of the csv file.
def read_csv(fileName, delimiter=',', quotechar='"'):
    import csv

    if not fileName.endswith('.csv'):
        raise Exception("Error: File name does not end with csv.")

    table = list()
    with open(fileName, 'rb') as infoFile:
        reader = csv.reader(infoFile, delimiter=',', quotechar='"')
        for row in reader:
            table.append(row)
    return table

# Returns the ith column of the multidimensional array "array"
def get_array_col(array, col):
    return [row[col] for row in array]

def mean(iterable):
    count = 0
    for it in iterable:
	count += 1
    return reduce(lambda x, y: x + y, iterable) / float(count)

month = {
    1   : "January",
    2   : "February",
    3   : "March",
    4   : "April",
    5   : "May",
    6   : "June",
    7   : "July",
    8   : "August",
    9   : "September",
    10  : "October",
    11  : "November",
    12  : "December"
}

days_in_month = {
    1   : 31,
    2   : 28,
    3   : 31,
    4   : 30,
    5   : 31,
    6   : 30,
    7   : 31,
    8   : 31,
    9   : 30,
    10  : 31,
    11  : 30,
    12  : 31
}
