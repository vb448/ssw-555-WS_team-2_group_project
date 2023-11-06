from prettytable import PrettyTable
from datetime import datetime
import dateutil.relativedelta

individuals = {}
families = {}

error_messages = []

current_individual = None
current_family = None

individual_ids = set()
family_ids = set()


# Process a GEDCOM line and update data structures
def process_gedcom_line(line):
    global current_individual, current_family
    
    tokens = line.strip().split()
    #print(tokens)
    if len(tokens) < 2:
        return
    
    tag = tokens[1]

    if tag.startswith('@I'):
        individual_id = tokens[1]
        if individual_id in individual_ids:
            error_msg = f"ERROR: INDIVIDUAL: US22: {individual_id}: Individual ID is not unique"
            error_messages.append(error_msg)
        else:
            individual_ids.add(individual_id)
        individuals[individual_id] = {"name": "", "birth_date": None, "death_date": None}
        current_individual = individuals[individual_id]
    elif tag == "NAME" and current_individual:
        name = " ".join(tokens[2:])
        current_individual["name"] = name

    elif tag == "BIRT" and current_individual:
        birth_date = None
        for line in file:
            inner_tokens = line.strip().split()
            if len(inner_tokens) < 2:
                break
            inner_tag = inner_tokens[1]
            if inner_tag == "DATE":
                birth_date = " ".join(inner_tokens[2:])
                break
        current_individual["birth_date"] = birth_date

    elif tag == "DEAT" and current_individual:
        death_date = None
        for line in file:
            tokens = line.strip().split()
            if len(tokens) < 2:
                break
            tag = tokens[1]
            if tag == "DATE":
                death_date = " ".join(tokens[2:])
                break
        current_individual["death_date"] = death_date
    
    elif tag.startswith('@F'):
        family_id = tokens[1]
        if family_id in family_ids:
            error_msg = f"ERROR: FAMILY: US22: {family_id}: Family ID is not unique"
            error_messages.append(error_msg)
        else:
            family_ids.add(family_id)
        families[family_id] = {"husband_id": "", "wife_id": "", "marriage_date": None, "divorce_date": None}
        current_family = families[family_id]

    elif tag == "CHIL" and current_family:
        childId = tokens[2]
        if "Children" not in current_family:
            current_family.update({"Children": [childId]})
        else:
            current_family["Children"].append(childId)

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

    elif tag == "MARR" and current_family:
        # Check if there is a DATE tag on the next line to get the marriage date
        marriage_date = None
        for line in file:
            inner_tokens = line.strip().split()
            if len(inner_tokens) < 2:
                break
            inner_tag = inner_tokens[1]
            if inner_tag == "DATE":
                marriage_date = " ".join(inner_tokens[2:])
                break
        current_family["marriage_date"] = marriage_date

    elif tag == "DIV" and current_family:
        # Check if there is a DATE tag on the next line to get the divorce date
        divorce_date = None
        for line in file:
            inner_tokens = line.strip().split()
            if len(inner_tokens) < 2:
                break
            inner_tag = inner_tokens[1]
            if inner_tag == "DATE":
                divorce_date = " ".join(inner_tokens[2:])
                break
        current_family["divorce_date"] = divorce_date

# Read the GEDCOM file line by line and process each line
with open('My-Family.ged', 'r') as file:
    for line in file:
        process_gedcom_line(line)


# Create PrettyTable for individuals
individual_table = PrettyTable()
individual_table.field_names = ["ID", "Name", "Birth Date", "Death Date", "Current Age"] #included current age for US27

# Create PrettyTable for families
family_table = PrettyTable()
family_table.field_names = ["ID", "Husband ID", "Husband", "Wife ID", "Wife", "Marriage Date", "Divorce Date", "Children"]

# Create PrettyTable for deceased individuals US29
deceased_individuals_table = PrettyTable()
deceased_individuals_table.field_names = ["ID", "Name", "Birth Date", "Death Date", "Age at Death"]

# Populate PrettyTable for deceased individuals
for individual_id, individual in individuals.items():
    name = individual["name"]
    birth_date = individual["birth_date"]
    death_date = individual["death_date"]
    
    if death_date:
        birth_date_obj = datetime.strptime(birth_date, "%d %b %Y")
        death_date_obj = datetime.strptime(death_date, "%d %b %Y")
        age_at_death = death_date_obj.year - birth_date_obj.year - ((death_date_obj.month, death_date_obj.day) < (birth_date_obj.month, birth_date_obj.day))
        
        deceased_individuals_table.add_row([individual_id, name, birth_date, death_date, age_at_death])


# a dictionary to track individuals with the same name and birth date
name_birth_dict = {}

# Populate PrettyTables
for individual_id, individual in individuals.items():
    name = individual["name"]
    birth_date = individual["birth_date"]
    death_date = individual["death_date"]

    name_birth_key = (name, birth_date)

    current_age = "N/A"

    if name_birth_key in name_birth_dict:
        name_birth_dict[name_birth_key].append(individual_id)
    else:
        name_birth_dict[name_birth_key] = [individual_id]

    if death_date:
        death_date_obj = datetime.strptime(death_date, "%d %b %Y")
        for family_id, family in families.items():
            husband_id = family["husband_id"]
            wife_id = family["wife_id"]
            if individual_id == husband_id or individual_id == wife_id:
                marriage_date = family["marriage_date"]
                if marriage_date:
                    marriage_date_obj = datetime.strptime(marriage_date, "%d %b %Y")
                    if death_date_obj < marriage_date_obj:
                        error_msg = f"ERROR: INDIVIDUAL: US05: {individual_id}: Died {death_date} before marriage {marriage_date}"
                        error_messages.append(error_msg)

    if birth_date:
        for same_name_birth_id in name_birth_dict[name_birth_key]:
            if same_name_birth_id != individual_id:
                error_msg = f"ERROR: INDIVIDUAL: US23: {individual_id} and {same_name_birth_id}: Have the same name and birth date {name} - {birth_date}"
                error_messages.append(error_msg)

        #below logic is to list individuals current age for US27
        birth_date_obj = datetime.strptime(birth_date, "%d %b %Y")
        today = datetime.now()
        current_age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

        for family_id, family in families.items():
            husband_id = family.get("husband_id")
            wife_id = family.get("wife_id")
            marriage_date = family.get("marriage_date")

            if individual_id == husband_id or individual_id == wife_id:
                if marriage_date:
                    marriage_date_obj = datetime.strptime(marriage_date, "%d %b %Y")
                    if marriage_date_obj < birth_date_obj:
                        error_msg = f"ERROR: INDIVIDUAL: US02: {individual_id}: Birth date {birth_date} occurs after marriage date {marriage_date}"
                        error_messages.append(error_msg)

                if death_date:
                    death_date_obj = datetime.strptime(death_date, "%d %b %Y")
                    if death_date_obj < birth_date_obj:
                        error_msg = f"ERROR: INDIVIDUAL: US03: {individual_id}: Birth date {birth_date} occurs after death date {death_date}"
                        error_messages.append(error_msg)

    individual_table.add_row([individual_id, individual["name"], individual["birth_date"], individual["death_date"], current_age])

for family_id, family in families.items():
    husband_id = family["husband_id"]
    wife_id = family["wife_id"]
    husband_name = individuals.get(family["husband_id"], {}).get("name", "")
    wife_name = individuals.get(family["wife_id"], {}).get("name", "")

    marriage_date = family["marriage_date"]
    divorce_date = family["divorce_date"]

    #user story 08 and 09
    if "Children" in family:
        for child in family["Children"]:
            marriage_date_obj = datetime.strptime(marriage_date, "%d %b %Y")
            birth_date_obj = datetime.strptime(individuals[child]["birth_date"], "%d %b %Y")

            if individuals[wife_id]["death_date"]:
                mom_death_date_obj = datetime.strptime(individuals[wife_id]["death_date"], "%d %b %Y")

            if individuals[husband_id]["death_date"]:
                dad_death_date_obj = datetime.strptime(individuals[husband_id]["death_date"], "%d %b %Y")


            #08
            if birth_date_obj < marriage_date_obj:
                error_msg = f"ERROR: FAMILY: US08: {child}: Born on {birth_date_obj} before the marriage of their parents on {marriage_date_obj}"
                error_messages.append(error_msg)   

            if divorce_date:
                divorce_date_obj = datetime.strptime(divorce_date, "%d %b %Y") 
                difference = dateutil.relativedelta.relativedelta(birth_date_obj, divorce_date_obj)

                if difference.months > 9:
                    error_msg = f"ERROR: FAMILY: US08: {child}: Born on {birth_date_obj} more than 9 months after the divorce of their parents on {divorce_date_obj}"
                    error_messages.append(error_msg) 

            #09
            if individuals[wife_id]["death_date"]:
                if mom_death_date_obj < birth_date_obj:
                    error_msg = f"ERROR: FAMILY: US09: {child}: Born on {birth_date_obj} after the death of their mom on {mom_death_date_obj}"
                    error_messages.append(error_msg)   

            if individuals[husband_id]["death_date"]:
                difference = dateutil.relativedelta.relativedelta(birth_date_obj, dad_death_date_obj)

                if difference.months > 9:
                    error_msg = f"ERROR: FAMILY: US09: {child}: Born on {birth_date_obj} more than 9 months after the death of their dad on {dad_death_date_obj}"
                    error_messages.append(error_msg) 

    if "Children" in family:
        children = family["Children"]
    else:
        children = []

    if marriage_date and divorce_date:
        marriage_date_obj = datetime.strptime(marriage_date, "%d %b %Y")
        divorce_date_obj = datetime.strptime(divorce_date, "%d %b %Y")
        if marriage_date_obj > divorce_date_obj:
            error_msg = f"ERROR: FAMILY: US04: {family_id}: {husband_id} ({husband_name}) and {wife_id} ({wife_name}) Married {marriage_date} after divorce on {divorce_date}"
            error_messages.append(error_msg)    
    
    family_table.add_row([family_id, husband_id, husband_name, wife_id, wife_name, marriage_date, divorce_date, children])

#User Story: 01 - Dates before current date
def US1_dates_before_current_date(individuals, family):
    Error01_individuals = []
    Error01_family = []
    for id in individuals:
        if individuals[id]['death_date']!='NA' and individuals[id]['death_date']!=None:
            deathday = datetime.strptime(individuals[id]["death_date"], "%d %b %Y")
            birthday = datetime.strptime(individuals[id]["birth_date"], "%d %b %Y")
            if deathday > datetime.now():
                Error01_individuals.append(individuals[id])
            if birthday > datetime.now():
                Error01_individuals.append(individuals[id])

    for id in family:
        if family[id]["divorce_date"] != 'NA' and family[id]["divorce_date"] != None:
            divorceday = datetime.strptime(family[id]["divorce_date"], "%d %b %Y")
            marriageday = datetime.strptime(family[id]["marriage_date"], "%d %b %Y")
            if divorceday > datetime.now():
                Error01_family.append(family[id])
            if marriageday > datetime.now():
                Error01_family.append(family[id])

    return Error01_individuals, Error01_family


def US6_divorce_before_death(individuals, family):
    Error06 = []
    for id in family:
        if family[id]['divorce_date'] != 'NA' and family[id]['divorce_date'] != None:
            divorced_date = datetime.strptime(family[id]['divorce_date'], "%d %b %Y")
            husband_id = family[id]['husband_id']
            wife_id = family[id]['wife_id']
            if individuals[husband_id]['death_date'] != 'NA' and individuals[husband_id]['death_date'] != None:
                husband_dday = datetime.strptime(individuals[husband_id]['death_date'], "%d %b %Y")
                if husband_dday < divorced_date:
                    Error06.append(individuals[husband_id])
            if individuals[wife_id]['death_date'] != 'NA' and individuals[wife_id]['death_date'] != None:
                wife_dday = datetime.strptime(individuals[wife_id]['death_date'], "%d %b %Y")
                if wife_dday < divorced_date:
                    Error06.append(individuals[wife_id])
    return Error06


output = ""
#User Story: 01 - Dates before current date
us1_errors = US1_dates_before_current_date(individuals, families)
us6_errors = US6_divorce_before_death(individuals, families)
output += "User Story: 01 - Dates before current date\n\nErrors related to Dates before current date (US01)\n: " + str(us1_errors) + "\n\n" + "These are the details for either of the birthdates, deathdates, marriagedates and divorcedates that have occured after the current date." + "\n"
output+= "------------------------------------------------------------------------------\n\n"

# User Story 06: Divorce before death
output += "User Story 06: Divorce before death\n\nErrors related to divorce date not being before death date (US06)\n: " + str(us6_errors) + "\n\n" + "These are the details for divorce dates that have occured after the death date of an individual." + "\n"
output+= "------------------------------------------------------------------------------\n\n"
error_messages.append(output)

print("Individuals:")
print(individual_table)
print()
print("Deceased Individuals:")
print(deceased_individuals_table)

print("\nFamilies:")
print(family_table)

print("\n" * 2)

for error_msg in error_messages:
    print(error_msg)