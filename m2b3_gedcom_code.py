def is_valid_tag(tag):
    valid_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]  # Add more valid tags as needed
    return tag in valid_tags

# process a GEDCOM line and print the desired output
def process_gedcom_line(line):
    tokens = line.strip().split()
    if len(tokens) < 2:
        return
    
    level = tokens[0]
    tag = tokens[1]

    valid = 'Y' if is_valid_tag(tag) else 'N'
    arguments = ' '.join(tokens[2:])

    print(f"--> {line}")
    print(f"<-- {level}|{tag}|{valid}|{arguments}")

# Read the GEDCOM file line by line and process each line
with open('My-Family.ged', 'r') as file:
    for line in file:
        process_gedcom_line(line)