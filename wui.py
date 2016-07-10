import csv
import helper
import unittest
import argparse
from sys import argv
import os

# Usage: python wui.py <csv file in correct format>

######### TESTS ########

class TestProgram(unittest.TestCase):
    def test_program(self):
        test_file = "/home/wentron/Documents/coding/python/scripts/website_user_importer_test/test.csv"
        test_output_file = "/home/wentron/Documents/coding/python/scripts/website_user_importer_test/test_output.csv"
        remove_list = ['wbli@altera.com']

        create_importable_csv_from_website_csv(test_file, test_output_file, remove_list)

        #test_input = read_csv(test_file) # for more automated testing.
        test_output = helper.read_csv(test_output_file)

        print test_output

        userN = 3
        self.assertEqual(userN, len(test_output))
        self.assertEqual(test_output[0][0], "tonywli@hotmail.com")
        self.assertEqual(test_output[0][1], "Wen")
        self.assertEqual(test_output[0][2], "Li")
        self.assertEqual(test_output[1][0], "alan.daniels@mail.utoronto.ca")
        self.assertEqual(test_output[1][1].strip(), "Alan")
        self.assertEqual(test_output[1][2], "Daniels")
        self.assertEqual(test_output[2][0], "tony.wenbo.li@gmail.com")
        self.assertEqual(test_output[2][1], "Wen Bo")
        self.assertEqual(test_output[2][2], "Li")

#########################

# Make name lower case except leading letters.
def normalize_name(name):
    name_split = name.split()
    name_split = [part[0].upper() + part[1:].lower() for part in name_split]
    return " ".join(name_split)

def separate_names(names):
    separated_names = list()
    for name in names:
        name = normalize_name(name)

        full_name = name.strip().rsplit(' ', 1)
        separated_names.append(full_name)
    return separated_names

def remove_special_users(user_info, remove_list):
    for email in remove_list:
        try:
            user_info.pop(email)
        except KeyError:
            print "%s user not found!" % email
            exit()
    return user_info

def create_importable_csv_from_website_csv(input_file, output_file, remove_list=[]):
    table = helper.read_csv(input_file)

    names = helper.get_array_col(table, 0)
    emails = helper.get_array_col(table, 1)

    # The first row is the title.
    names = names[1:]
    emails = emails[1:]

    names = separate_names(names)

    user_info = dict()
    for i in xrange(min(len(names), len(emails))):
        # If user has a name and email, then store its info inside the array.
        if emails[i] and names[i][0]:
            user_info[emails[i]] = names[i]

    user_info = remove_special_users(user_info, remove_list)

    with open(output_file, 'wb') as users_file:
        import_file_writer = csv.writer(users_file, delimiter=",", quotechar='"')
        for email, name in user_info.iteritems():
            import_file_writer.writerow([email] + name)

def main(args, argv):
    if not args.csv_file:
        print "Skipping execution. csv file input not given."
    elif not os.path.isfile(args.csv_file):
        print "Skipping execution. Given path is not a file or does not exist."
    elif not args.test:
        # Hard coded to a particular file
        output_file = "import_file.csv"
        special_emails_list = ["sa2.hackeracademy@gmail.com", "sa3.hackeracademy@gmail.com", "sa1.hackeracademy@openmailbox.org", "tonywli@hotmail.com", "ainsleigh@thenext36.ca", "bijan@eventmobi.com", "bitalino@plux.info", "skaiser@microsoft.com"]

        create_importable_csv_from_website_csv(args.csv_file, output_file, special_emails_list)
        print "import_file.csv created"

    # Always run the test, but run at the end because the test always ends the program?
    del argv[1:]
    unittest.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn input file csv to an output csv in the current"
            "folder. This works for turning hackeracademy.org's downloadable list of members in CSV to a CSV file"
            "acceptable for direct import into MailChimp.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("csv_file", nargs = '?', help="input csv file.")
    group.add_argument('-t', "--test", help="Only run the test", action="store_true")
    args = parser.parse_args()

    main(args, argv)
