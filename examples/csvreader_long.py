import numpy as np
import hepfile as hep

people = np.loadtxt('sheet1.csv', unpack=True, dtype=str,
                     delimiter=",")

#with open('sheet2.csv') as input:
#        cols = input.read().split('\n')
#        for col in cols:
#            print(len(col.split(',')))

vehicles = np.loadtxt('sheet2.csv', unpack=True, dtype=str,
                     delimiter=",", comments = '$')

houses = np.loadtxt('sheet3.csv', unpack=True, dtype=str,
                     delimiter=",", comments = '$')

people_ID = people[0][1:].astype(np.int32)
vehicles_ID = vehicles[0][1:].astype(np.int32)
houses_ID = houses[0][1:].astype(np.int32)

town = hep.initialize()

hep.create_group(town, 'people', counter ='ID')
hep.create_group(town, 'vehicles', counter='ID')
#hep.create_group(town, 'houses')

hep.create_dataset(town, ['First name','Last name','Gender ID',
                        'Highest degree/grade'], group = 'people', dtype = str)
hep.create_dataset(town, ['Age', 'Height', 'Yearly Income'], group = 'people', dtype = int)

hep.create_dataset(town, ['Type of vehicle','Gas/electric/human powered'], group = 'vehicles', dtype = str)
hep.create_dataset(town, ['# of riders', 'Year', 'Cost'], group = 'vehicles', dtype = int)

hep.create_dataset(town, ['houses/House/apartment/condo'], dtype = str)
hep.create_dataset(town, ['houses/# of bedrooms', 'houses/Square footage','houses/Year built',
                            'houses/Estimate'], dtype = int)
hep.create_dataset(town, 'houses/# of bathrooms', dtype = float)

bucket = hep.create_single_bucket(town)

for i in range(0,4):
    for j in range(len(people_ID)):
        if people_ID[j] == i:
            bucket['people/First name'] = people[1, j+1]
            bucket['people/Last name'] = people[2, j+1]
            bucket['people/Gender ID'] = people[3, j+1]
            bucket['people/Age'] = people[4, j+1].astype(np.int32)
            bucket['people/Height'] = people[5, j+1].astype(np.int32)
            bucket['people/Yearly Income'] = people[6, j+1].astype(np.int32)
            bucket['people/Highest degree/grade'] = people[6, j+1]
            bucket['people/ID'] += 1
    
    for j in range(len(vehicles_ID)):
        if vehicles_ID[j] == i:
            bucket['vehicles/Type of vehicle'] = vehicles[1, j+1]
            bucket['vehicles/# of riders'] = vehicles[2, j+1].astype(np.int32)
            bucket['vehicles/Gas/electric/human powered'] = vehicles[3, j+1]
            bucket['vehicles/Year'] = vehicles[4, j+1].astype(np.int32)
            bucket['vehicles/Cost'] = vehicles[5, j+1].astype(np.int32)
            bucket['vehicles/ID'] += 1
    
    bucket['houses/House/apartment/condo'] = houses[1, i+1]
    bucket['houses/# of bedrooms'] = houses[2, i+1].astype(np.int32)
    bucket['houses/# of bathrooms'] = houses[3, i+1].astype(np.float32)
    bucket['houses/Square footage'] = houses[4, i+1].astype(np.int32)
    bucket['houses/Year built'] = houses[5, i+1].astype(np.int32)
    bucket['houses/Estimate'] = houses[6, i+1].astype(np.int32)
                        
    hep.pack(town, bucket)

hep.write_to_file('town_hep_long.hdf5', town,force_single_precision=False)

