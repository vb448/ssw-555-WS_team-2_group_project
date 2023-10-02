from prettytable import PrettyTable

individuals = {}
families = {}

current_individual = None
current_family = None

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
        individuals[individual_id] = {"name": "", "death_date": None}
        current_individual = individuals[individual_id]
    elif tag == "NAME" and current_individual:
        name = " ".join(tokens[2:])
        current_individual["name"] = name

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
        families[family_id] = {"husband_id": "", "wife_id": "", "marriage_date": None, "divorce_date": None}
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
individual_table.field_names = ["ID", "Name", "Death Date"]

# Create PrettyTable for families
family_table = PrettyTable()
family_table.field_names = ["ID", "Husband ID", "Husband", "Wife ID", "Wife", "Marriage Date", "Divorce Date"]

# Populate PrettyTables
for individual_id, individual in individuals.items():
    individual_table.add_row([individual_id, individual["name"], individual["death_date"]])

for family_id, family in families.items():
    husband_id = family["husband_id"]
    wife_id = family["wife_id"]
    husband_name = individuals.get(family["husband_id"], {}).get("name", "")
    wife_name = individuals.get(family["wife_id"], {}).get("name", "")

    marriage_date = family["marriage_date"]
    divorce_date = family["divorce_date"]
    
    family_table.add_row([family_id, husband_id, husband_name, wife_id, wife_name, marriage_date, divorce_date])


print("Individuals:")
print(individual_table)

print("\nFamilies:")
print(family_table)
