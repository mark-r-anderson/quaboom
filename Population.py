import Person
import random

class Population:
    '''creates a population of people based on the total population
     uses and age distrubution to weight the assignment of ages'''
    def __init__(self,nPop):
        self.list = [] #The list of all people
        self.infected = []
        self.pop = nPop
        for i in range (self.pop)
            NewPerson = Person(i+1,False,False,None,None,None,None,None)
            self.list.append(NewPerson)  #adds new person to list
        for i in range(n0):
            self.list[i].infect(day=0)
            self.infected.append(self.list[i])

    #counts the total number of infected individuals
    def count_infected(self):
        infected_population = sum(obj.infected == True for obj in self.list)
        return infected_population

    def check_infected(self):
        return self.infected

    #counts the total number of recovered individuals
    def check_recovered(self):
        recovered_population = sum(obj.recovered == True for obj in self.list)
        return recovered_population
