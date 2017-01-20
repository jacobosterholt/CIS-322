import csv

print("INSERT INTO facilities (facility_pk, fcode, common_name, location) VALUES (1, 'DC', 'Washington, D.C.', 'Washington, D.C.');")
print("INSERT INTO facilities (facility_pk, fcode, common_name) VALUES (2, 'HQ', 'Headquarters');")
print("INSERT INTO facilities (facility_pk, fcode, common_name) VALUES (3, 'MB005', 'MB005');")
print("INSERT INTO facilities (facility_pk, fcode, common_name, location) VALUES (4, 'NC', 'National City', 'National City');")
print("INSERT INTO facilities (facility_pk, fcode, common_name, location) VALUES (5, 'SPNV', 'Sparks', 'Sparks, NV');")
print("INSERT INTO facilities (facility_pk, common_name) VALUES (6, 'Site 300');")
print("INSERT INTO facilities (facility_pk, common_name) VALUES (7, 'Groom Lake');")
print("INSERT INTO facilities (facility_pk, common_name) VALUES (8, 'Los Alamos, NM');")

facilities = [['Washington, D.C.', 1], ['Headquarters', 2], ['MB 005', 3], ['National City', 4], ['Sparks, NV', 5], ['Site 300', 6], ['Groom Lake', 7], ['Los Alamos, NM', 8]]

with open('osnap_legacy/transit.csv', 'r') as f:
    reader = csv.reader(f)
    transit = list(reader)

for each in transit:
    if each[1][0] == 'L':
        each[1] = 'Los Alamos, NM'

# Adding product_list to products
with open('osnap_legacy/product_list.csv', 'r') as f:
    reader = csv.reader(f)
    product_list = list(reader)

for i in range(1, len(product_list)):
    print("INSERT INTO products (product_pk, vendor, description, alt_description) VALUES ({0}, '{1}', '{2}', '{3}');".format(i, product_list[i][4], product_list[i][0], product_list[i][2]))
    product_list[i].append(i)

# Adding all facility inventories to assets	
with open('osnap_legacy/DC_inventory.csv', 'r') as f:
    reader = csv.reader(f)
    DC_inventory = list(reader)

counter = 0

for i in range(1, len(DC_inventory)):
    product_key = 0
    for each in product_list:
        if each[0] == DC_inventory[i][1]:
            product_key = each[-1]
    print("INSERT INTO assets (asset_pk, product_fk, asset_tag, description) VALUES ({0}, {1}, '{2}', '{3}');".format(i, product_key, DC_inventory[i][0], DC_inventory[i][1]))
    print("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}');".format(i, 1, DC_inventory[i][4]))
    for each in transit:
        for tag in each[0].split(", "):
            if tag == DC_inventory[i][0]:
                for fac in facilities:
                    if fac[0] == each[1]:
                        print("INSERT INTO asset_at (asset_fk, facility_fk, depart_dt) VALUES ({0}, {1}, '{2}');".format(i, fac[1], each[3]))
    counter += 1

with open('osnap_legacy/HQ_inventory.csv', 'r') as f:
    reader = csv.reader(f)
    HQ_inventory = list(reader)

for i in range(1, len(HQ_inventory)):
    product_key = 0
    counter += 1
    for each in product_list:
        if each[0] == HQ_inventory[i][1]:
            product_key = each[-1]
    print("INSERT INTO assets (asset_pk, product_fk, asset_tag, description) VALUES ({0}, {1}, '{2}', '{3}');".format(counter, product_key, HQ_inventory[i][0], HQ_inventory[i][1]))
    print("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}');".format(counter, 2, HQ_inventory[i][4]))
    for each in transit:
        for tag in each[0].split(", "):
            if tag == HQ_inventory[i][0]:
                for fac in facilities:
                    if fac[0] == each[1]:
                        print("INSERT INTO asset_at (asset_fk, facility_fk, depart_dt) VALUES ({0}, {1}, '{2}');".format(counter, fac[1], each[3]))
	
with open('osnap_legacy/MB005_inventory.csv', 'r') as f:
    reader = csv.reader(f)
    MB005_inventory = list(reader)

for i in range(1, len(MB005_inventory)):
    product_key = 0
    counter += 1
    for each in product_list:
        if each[0] == MB005_inventory[i][1]:
            product_key = each[-1]
    print("INSERT INTO assets (asset_pk, product_fk, asset_tag, description) VALUES ({0}, {1}, '{2}', '{3}');".format(counter, product_key, MB005_inventory[i][0], MB005_inventory[i][1]))
    print("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}');".format(counter, 3, '12/15/17'))
    for each in transit:
        for tag in each[0].split(", "):
            if tag == MB005_inventory[i][0]:
                for fac in facilities:
                    if fac[0] == each[1]:
                        print("INSERT INTO asset_at (asset_fk, facility_fk, depart_dt) VALUES ({0}, {1}, '{2}');".format(counter, fac[1], each[3]))

with open('osnap_legacy/NC_inventory.csv', 'r') as f:
    reader = csv.reader(f)
    NC_inventory = list(reader)

for i in range(1, len(NC_inventory)):
    product_key = 0
    counter += 1
    for each in product_list:
        if each[0] == NC_inventory[i][1]:
            product_key = each[-1]
    print("INSERT INTO assets (asset_pk, product_fk, asset_tag, description) VALUES ({0}, {1}, '{2}', '{3}');".format(counter, product_key, NC_inventory[i][0], NC_inventory[i][1]))
    print("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}');".format(counter, 4, NC_inventory[i][4]))
    for each in transit:
        for tag in each[0].split(", "):
            if tag == NC_inventory[i][0]:
                for fac in facilities:
                    if fac[0] == each[1]:
                        print("INSERT INTO asset_at (asset_fk, facility_fk, depart_dt) VALUES ({0}, {1}, '{2}');".format(counter, fac[1], each[3]))

with open('osnap_legacy/SPNV_inventory.csv', 'r') as f:
    reader = csv.reader(f)
    SPNV_inventory = list(reader)

for i in range(1, len(SPNV_inventory)):
    product_key = 0
    counter += 1
    for each in product_list:
        if each[0] == SPNV_inventory[i][1]:
            product_key = each[-1]
    print("INSERT INTO assets (asset_pk, product_fk, asset_tag, description) VALUES ({0}, {1}, '{2}', '{3}');".format(counter, product_key, SPNV_inventory[i][0], SPNV_inventory[i][1]))
    print("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}');".format(counter, 5, SPNV_inventory[i][4]))
    for each in transit:
        for tag in each[0].split(", "):
            if tag == SPNV_inventory[i][0]:
                for fac in facilities:
                    if fac[0] == each[1]:
                        print("INSERT INTO asset_at (asset_fk, facility_fk, depart_dt) VALUES ({0}, {1}, '{2}');".format(counter, fac[1], each[3]))

# Adding the vehicles to assets and vehicles tables
vehicles = ['Prometheus', 'C152', 'T34', 'T35', 'H6', 'C214', 'C95', 'B50', 'C17', 'B32', 'B14', 'B10', 'B2', 'C25', 'C1', 'C110', 'C113', 'H7', 'H1']

for i in range(1, len(vehicles) + 1):
    product_key = 0
    counter += 1
    print("INSERT INTO assets (asset_pk, product_fk, description) VALUES ({0}, {1}, '{2}');".format(counter, product_key, vehicles[i - 1]))
    print("INSERT INTO vehicles (vehicle_pk, asset_fk) VALUES ({0}, {1});".format(i, counter))
    name = vehicles[i - 1]
    vehicles[i - 1] = [name, i]

# Adding convoys to convoys and used_by
with open('osnap_legacy/convoy.csv', 'r') as f:
    reader = csv.reader(f)
    convoys = list(reader)

for i in range(1, len(convoys)):
    for each in transit:
        if convoys[i][0] == each[5]:
            arr = 0
            dep = 0
            adate = '???'
            ddate = '???'
            for fac in facilities:
                if fac[0] == each[1]:
                    dep = fac[1]
                    ddate = each[3]
                if fac[0] == each[2]:
                    arr = fac[1]
                    adate = each[4]
            print("INSERT INTO convoys (convoy_pk, request, source_fk, dest_fk, depart_dt, arrive_dt) VALUES ({0}, '{1}', {2}, {3}, '{4}', '{5}');".format(i, convoys[i][0], dep, arr, ddate, adate))
            break
    for vehicle in convoys[i][7].split(", "):
        for each in vehicles:
            if each[0] == vehicle:
                print("INSERT INTO used_by (vehicle_fk, convoy_fk) VALUES ({0}, {1});".format(each[1], i))
				
# Adding security levels to levels
with open('osnap_legacy/security_levels.csv', 'r') as f:
    reader = csv.reader(f)
    levels = list(reader)
	
for i in range(1, len(levels)):
    print("INSERT INTO levels (level_pk, abbrv, comment) VALUES ({0}, '{1}', '{2}');".format(i, levels[i][0], levels[i][1]))

# Adding security compartments to compartments
with open('osnap_legacy/security_compartments.csv', 'r') as f:
    reader = csv.reader(f)
    compartments = list(reader)
	
for i in range(1, len(compartments)):
    print("INSERT INTO compartments (compartment_pk, abbrv, comment) VALUES ({0}, '{1}', '{2}');".format(i, compartments[i][0], compartments[i][1]))