with open('bodmas_metadata.csv', 'r') as f:
    lines = f.readlines()
    j = []
    Id = 0
    families = {}
    for i in lines:
        if i.split(',')[2] == '\n':
            continue
        else:
            family = i.split(',')[2].replace('\n', '')
            if family not in families.values() and family != 'family':
                Id += 1
                families[str(Id)] = family
            i = i.split(',')[0] + ',' + str(Id) + '\n'
            j.append(i)
with open('bodmas_metadata_new.csv', 'w+') as f:
    for lines in j:
        f.writelines(lines)
print(families)