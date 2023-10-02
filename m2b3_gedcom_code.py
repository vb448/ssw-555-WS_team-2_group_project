
from prettytable import PrettyTable
import datetime

individuals = {}
families = {}

current_individual = None
current_family = None

# Process a GEDCOM line and update data structures
def process_gedcom_line(line):
    global current_individual, current_family, inBirthLine, current_individual_id, inMarriageLine, weddingDay, husband_id, wife_id, inDeathLine
    
    tokens = line.strip().split()
    if len(tokens) < 2:
        return
    
    tag = tokens[1]

    if tag.startswith('@I'):
        individual_id = tokens[1]
        current_individual_id = tokens[1]
        individuals[individual_id] = {"name": ""}
        current_individual = individuals[individual_id]
    elif tag == "NAME" and current_individual:
        name = " ".join(tokens[2:])
        current_individual["name"] = name
    elif tag.startswith('@F'):
        family_id = tokens[1]
        families[family_id] = {"husband_id": "", "wife_id": ""}
        current_family = families[family_id]
    elif tag == "HUSB" and current_family:
        husband_id = tokens[2]
        current_family["husband_id"] = husband_id
        # Populate husband's name from individuals dictionary
        husband_name = individuals.get(husband_id, {}).get("name", "")
        current_family["husband_name"] = husband_name        
    elif tag == "WIFE" and current_family:
        wife_id = tokens[2]
        current_family["wife_id"] = wife_id
        # Populate wife's name from individuals dictionary
        wife_name = individuals.get(wife_id, {}).get("name", "")
        current_family["wife_name"] = wife_name
    #save indicator of if previous line was 'BIRT' for the date line
    elif tag == 'BIRT' and current_individual:
        inBirthLine = True
    #assign birthday to current individual
    elif tag == 'DATE' and inBirthLine:
        month = assignMonth(tokens[3])
        
        bDay = datetime.datetime(int(tokens[4]), month, int(tokens[2]))
        individuals[current_individual_id].update({"Birthday": bDay})
        inBirthLine = False
    #save indicator of being within the marriage section
    elif tag == 'MARR':
        inMarriageLine = True
    #add date of first marriage to husband and wife 
    elif tag == 'DATE' and inMarriageLine:
        month = assignMonth(tokens[3])

        weddingDay = datetime.datetime(int(tokens[4]), month, int(tokens[2]))
        #add check if need to add marriage date to the individual and that it is the first marriage
        if not "Wedding Day" in individuals[husband_id]:
            individuals[husband_id].update({"Wedding Day": weddingDay})

        if not "Wedding Day" in individuals[wife_id]:
            individuals[wife_id].update({"Wedding Day": weddingDay})
        
        inMarriageLine = False
    #save indicator of if in death section
    elif tag == 'DEAT':
        inDeathLine = True
    #add date of death to individual
    elif tag == 'DATE' and inDeathLine:
        month = assignMonth(tokens[3])

        deathDay = datetime.datetime(int(tokens[4]), month, int(tokens[2]))
       
        individuals[current_individual_id].update({"Death Date": deathDay})
        inDeathLine = False

def assignMonth(abbreviation):
    
    if abbreviation == 'JAN':
            month = 1
    elif  abbreviation == 'FEB':
            month = 2
    elif abbreviation == 'MAR':
            month = 3
    elif  abbreviation == 'APR':
            month = 4
    elif  abbreviation == 'MAY':
            month = 5
    elif  abbreviation == 'JUN':
            month = 6
    elif  abbreviation == 'JUL':
            month = 7
    elif  abbreviation == 'AUG':
            month = 8
    elif  abbreviation == 'SEP':
            month = 9
    elif  abbreviation == 'OCT':
            month = 10
    elif  abbreviation == 'NOV':
            month = 11
    elif  abbreviation == 'DEC':
            month = 12
    
    return month


# Read the GEDCOM file line by line and process each line
with open('My-Family.ged', 'r') as file:
    inBirthLine = False #for storing birthday
    inMarriageLine = False #for storing marriage date
    inDeathLine = False #for storing marriage date

    for line in file:
        process_gedcom_line(line)

def birthBeforeMarriage(individual):
    if individual["Birthday"] > individual["Wedding Day"]:
        return False
    
def birthBeforeDeath(individual):
    if individual["Birthday"] > individual["Death Date"]:    
        return False

# Create PrettyTable for individuals
individual_table = PrettyTable()
individual_table.field_names = ["ID", "Name", "Birthday", "Wedding Day", "Death Date"]

# Create PrettyTable for families
family_table = PrettyTable()
family_table.field_names = ["ID", "Husband", "Wife"]

# Populate PrettyTables
for individual_id, individual in individuals.items():
    if not "Wedding Day" in individual:
        individual["Wedding Day"] = "NA"
    
    if not "Death Date" in individual:
        individual["Death Date"] = "NA"
        
    individual_table.add_row([individual_id, individual["name"], individual["Birthday"], individual["Wedding Day"], individual["Death Date"]])

for family_id, family in families.items():
    husband_name = individuals.get(family["husband_id"], {}).get("name", "")
    wife_name = individuals.get(family["wife_id"], {}).get("name", "")
    
    family_table.add_row([family_id, husband_name, wife_name])


print("Individuals:")
print(individual_table)

print("\nFamilies:")
print(family_table)

for individual_id, individual in individuals.items():     
    if individual["Wedding Day"] != "NA":
        if not birthBeforeMarriage(individual):
            print("ERROR: INDIVIDUAL: US02: " + individual_id + ": Birthday " + individuals[individual_id]["Birthday"] + " occurs after their wedding date of " + individuals[individual_id]["Wedding Day"])

    if individual["Death Date"] != "NA":
        if not birthBeforeDeath(individual):
            print("ERROR: INDIVIDUAL: US03: " + individual_id + ": Birthday " + individuals[individual_id]["Birthday"] + " occurs after their death date of " + individuals[individual_id]["Death Date"])

