import unittest
import datetime
import dateutil.relativedelta

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


    