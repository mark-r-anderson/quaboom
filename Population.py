import numpy as np
import Person
import json

json_file = open('dataK.json')
disease_params = json.load(json_file)


AGE_OPTIONS = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
JOB_OPTIONS = ['Health', 'Sales', 'Neither']
HOUSE_OPTIONS = [1,2,3,4,5]
ISOLATION_OPTIONS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
SEVERITY_OPTIONS = ['Mild', 'Hospitalization', 'ICU', 'Death']

# isolation #
ISOLATION_WEIGHTS = np.ones(len(ISOLATION_OPTIONS))
# Normalize the probability
ISOLATION_WEIGHTS /= float(sum(ISOLATION_WEIGHTS)) #this is the one we don't have data on yet

# PULL DATA FROM THE JSON FILE #
# age #
AGE_WEIGHTS = np.zeros(len(AGE_OPTIONS))
for iage in range (len(AGE_WEIGHTS)):
    string = str(iage*10)+'-'+str(iage*10+9)
    AGE_WEIGHTS[iage]= disease_params['age_weights'][0][string]

# job #
JOB_WEIGHTS = np.zeros(len(JOB_OPTIONS))
for ijob in range (len(JOB_WEIGHTS)):
    string = JOB_OPTIONS[ijob].upper()
    JOB_WEIGHTS[ijob]= disease_params['job_weights'][0][string]

# house#
HOUSE_WEIGHTS = np.zeros(len(HOUSE_OPTIONS))
for ihouse in range (len(HOUSE_WEIGHTS)):
    string = str(ihouse+1)
    HOUSE_WEIGHTS[ihouse]= disease_params['house_weights'][0][string]

# case severity #
SEVERITY_WEIGHTS = np.zeros(len(SEVERITY_OPTIONS))
for iseverity in range (len(SEVERITY_WEIGHTS)):
    string = SEVERITY_OPTIONS[iseverity]
    SEVERITY_WEIGHTS[iseverity]= disease_params['case_severity'][0][string]

json_file.close()

PROB_OF_TEST = 0.5 #probability that the person will get tested


class Population:
    '''creates a population of people based on the total population
     uses and age distrubution to weight the assignment of ages

     suscept list has negative values for infected, and positive indicies for susept
     infected list has negative values for healthy, and positive indicies for infected
     recovered list has negative values for not recovered, and postitive indicies for recovered
     '''

    def __init__(self, nPop, n0):

        self.population = [0]*nPop  # The list of all people
        self.household = [0]*nPop #list of all houses (list that contains all lists of the people in the house)
        self.nPop = nPop #total population

        houseSize = np.random.choice(a=HOUSE_OPTIONS, p=HOUSE_WEIGHTS)
        houseIndex = 0
        self.household[houseIndex] = houseSize

        for i in range(0, nPop):
            # MAKE A PERSON
            age = np.random.choice(a=AGE_OPTIONS, p=AGE_WEIGHTS)
            job = np.random.choice(a=JOB_OPTIONS, p=JOB_WEIGHTS)
            isolation_tend = np.random.choice(a=ISOLATION_OPTIONS, p=ISOLATION_WEIGHTS)
            case_severity = np.random.choice(a=SEVERITY_OPTIONS, p=SEVERITY_WEIGHTS)

            newPerson = Person.Person(index=i, infected=False, recovered=False, dead=False, quarantined=False, quarantined_day=None,
                               infected_day=None, recovered_day=None, death_day=None,
                               others_infected=None, cure_days=None, recent_infections=None, age=age,
                               job=job, house_index=0,isolation_tendencies=isolation_tend,case_severity=case_severity)

            # ADD A PERSON
            self.population[i] = newPerson

            # Increment house info
            houseSize -= 1
            if houseSize == 0:
                houseSize = np.random.choice(HOUSE_OPTIONS)
                houseIndex += 1
                self.household[houseIndex] = houseSize

        # Make sure last household number is right (when it runs out of people to fill
        if houseSize != self.household[houseIndex]:
            self.household[houseIndex] = houseSize

        # Slice household list to the right size
        self.household = self.household[:houseIndex]

        # Create person status arrays
        self.susceptible = np.array(range(nPop+1), dtype=int) #list of all susceptible individuals
        self.infected = np.zeros(nPop+1, dtype=int) - 1  # list of all infected people (all healthy (negative) to start)
        self.recovered = np.zeros(nPop+1, dtype=int) - 1 # list of recovered people (all not recovered (negative) to start)
        self.dead = np.zeros(nPop+1, dtype=int) - 1 # list of recovered people
        self.testing = []# list of people waiting to be others_infected
        self.have_been_tested = [] # list of people who have been tested
        self.knows_infected = np.zeros(nPop+1,dtype=int) - 1 # list of people who have a positive test and are still infected
        self.quarantined = np.zeros(nPop+1,dtype=int) - 1 #list of people who are currently in quarantine

        # Infect first n0 people
        for i in range(1, n0+1):
            self.population[i].infect(day=0)
            self.infected[i] = i
            self.susceptible[i] = -1

    #returns the population
    def get_population_size(self):
        return self.nPop

    def get_population(self):
        return self.population

    # Properly return the actual indices of each bin of people
    def get_susceptible(self):
        return self.susceptible[self.susceptible > 0]

    def get_infected(self):
        return self.infected[self.infected > 0]

    def get_recovered(self):
        return self.recovered[self.recovered > 0]

    def get_dead(self):
        return self.dead[self.dead > 0]

    # Count the number of people in each bin
    def count_susceptible(self):
        return np.count_nonzero(self.susceptible > 0)

    def count_infected(self):
        return np.count_nonzero(self.infected > 0)

    def count_recovered(self):
        return np.count_nonzero(self.recovered > 0)

    def count_dead(self):
        return np.count_nonzero(self.dead > 0)

    #returns an individual based on their index
    def get_person(self, index):
        return self.population[index]

    # Infect a person
    def infect(self, index, day):
        didWork = self.population[index].infect(day=day)
        if didWork:
            self.infected[index] = index
            self.susceptible[index] = -1

        return didWork

    # Update lists for already infected people
    def update_infected(self, index):

        if self.infected[index] == index or self.susceptible[index]==-1 or self.population[index].is_infected()==False:
            # Already infected, or cant be infected
            return False
        self.infected[index] = index
        self.susceptible[index] = -1
        return True

    # Cure a person
    def cure(self, index, day):
        didWork = self.population[index].check_cured(day)
        if didWork:
            self.infected[index] = -1
            self.recovered[index] = index
        return didWork

    # Updates lists for already cured people
    def update_cured(self, index):
        if self.recovered[index]==index or self.population[index].is_recovered()==False:
            # Already recovered in pop obj or person obj is not actually recovered
            return False
        self.infected[index] = -1
        self.recovered[index] = index
        return True

    def die(self, index, day):
        didWork = self.population[index].check_dead(day)
        if didWork:
            self.infected[index] = -1
            self.recovered[index] = -1
            self.dead[index] = index
        return didWork

    def update_dead(self, index):
        if self.dead[index]==index or self.population[index].is_dead()==False:
            return False
        self.infected[index] = -1
        self.recovered[index] = -1
        self.dead[index] = index
        return True

    def count_tested(self):
        return len(self.have_been_tested)

    def update_quarantine(self, day):
        for i in range (len(self.population)):
            if self.quarantined[i] == 1:
                if self.population[i].check_quarantine(day) == False:
                    self.quarantined[i] = 0
        return True

    def count_quarantined(self):
        return np.count_nonzero(self.quarantined > 0)

    def count_tested(self):
        return len(self.have_been_tested)

    # updates the list of symptomatic people and adds the people who are symtomatic to the testing array
    def update_symptomatic (self,day):

        #updates everyone's symptoms
        for i in range (len(self.population)):
            self.population[i].check_symptoms(day)

            if (i not in self.testing and i not in self.have_been_tested): # if person is not already in testing function
                if random.random() < PROB_OF_TEST:
                    infected_person = self.population[i] #gets the infected person from the population list

                    if infected_person.show_symptoms == True and infected_person.knows_infected == False:

                        self.testing.append(i)#adds the person to the testing list

            elif (i in self.knows_infected and self.population[i].knows_infected == False):
                self.knows_infected[i] = 0


    def get_tested (self,tests_per_day,day):
        #if less people are in the list than testing capacity test everyone in the list
        if len(self.testing) < tests_per_day:
            tests_per_day = len(self.testing)

        for i in range (tests_per_day):

            person_index = self.testing[0] #gets first person waiting for test
            self.testing.pop(0) # removes first person waiting for test
            person = self.population[person_index]
            self.have_been_tested.append(person_index)

            if (person.infected == True):
                person.knows_infected = True
                self.knows_infected[i] = 1
                #quarantines the person
                person.quarantine = True
                person.quarantined_day = day
                self.quarantined[i] = 1

            elif (person.infected == False):
                person.knows_infected = False
