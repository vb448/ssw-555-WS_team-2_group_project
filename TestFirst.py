import unittest
import datetime
import dateutil.relativedelta
from m2b3_gedcom_code import process_gedcom_line, individual_ids, error_messages, individuals, name_birth_dict

#US03
def birthBeforeDeath(individual):
    if individual["Birthday"] > individual["Death Date"]:    
        return False
    else:
        return True

#US02
def birthBeforeMarriage(individual):
    if individual["Birthday"] > individual["Wedding Day"]:
        return False
    else:
        return True
    
#US08
def birthBeforeMarriageofParents(individual, parents):
    if individual["Birthday"] < parents["Marriage Day"]:
        return False
    else:
        return True


#US09
def birthAfterDeathOfMom(individual, mom):
    if individual["Birthday"] > mom["Death Day"]:
        return False
    else:
        return True
    

class TestUserStories(unittest.TestCase):

    def setUp(self):
        individual_ids.clear()
        error_messages.clear()
        individuals.clear()
        name_birth_dict.clear()
    
    def test_us22_uniqueID(self):
        line1 = "0 @I123 INDI"
        line2 = "0 @I123 INDI"
        process_gedcom_line(line1)
        process_gedcom_line(line2)

        self.assertIn("ERROR: INDIVIDUAL: US22: @I123: Individual ID is not unique", error_messages)

    def test_us23_same_name_and_birthdate(self):
        name_birth_dict = {('Raj /Palival/', '21 FEB 1998'): ['@I1@', '@I13@']}

        individuals['@I1@'] = {"name": "Raj /Palival/", "birth_date": "21 FEB 1998"}
        individuals['@I13@'] = {"name": "Raj /Palival/", "birth_date": "21 FEB 1998", "death_date": None}

        processed_pairs = set()

        for name_birth_key, individual_ids in name_birth_dict.items():
            name, birth_date = name_birth_key
            for i in range(len(individual_ids)):
                for j in range(i + 1, len(individual_ids)):
                    pair = (individual_ids[i], individual_ids[j])
                    if pair not in processed_pairs:
                        error_msg = f"ERROR: INDIVIDUAL: US23: {individual_ids[i]} and {individual_ids[j]}: Have the same name and birth date {name} - {birth_date}"
                        error_messages.append(error_msg)
                        processed_pairs.add(pair)

        self.assertIn("ERROR: INDIVIDUAL: US23: @I1@ and @I13@: Have the same name and birth date Raj /Palival/ - 21 FEB 1998", error_messages)
    
    def test_us02True(self):
        test1 = {"Birthday": datetime.datetime(1998, 6, 12), "Wedding Day": datetime.datetime(1999, 6, 12)}
        self.assertTrue(birthBeforeMarriage(test1))

    def test_us03True(self):
        test2 = {"Birthday": datetime.datetime(1998, 6, 12), "Death Date": datetime.datetime(1998, 6, 13)}
        self.assertTrue(birthBeforeDeath(test2))

    def test_us08True(self):
        test3Individual = {"Birthday": datetime.datetime(1998, 6, 12)}
        test3Parents = {"Marriage Day": datetime.datetime(1997, 6, 13)}
        self.assertTrue(birthBeforeMarriageofParents(test3Individual, test3Parents))

    def test_us09True(self):
        test4Individual = {"Birthday": datetime.datetime(1998, 6, 12)}
        test4Mom = {"Death Day": datetime.datetime(1999, 6, 13)}
        self.assertTrue(birthAfterDeathOfMom(test4Individual, test4Mom))


if __name__ == '__main__':
    unittest.main()


    