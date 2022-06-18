import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np

# RGB tuples to represent colors to encode health status
GREY = (0.78, 0.78, 0.78)   # uninfected
RED = (0.96, 0.15, 0.15)    # infected
GREEN = (0, 0.86, 0.03)     # recovered
BLACK = (0, 0, 0)           # dead

COVID19_Params = {
    "r0": 2.28,
    "incubation": 5,
    "percent_mild": 0.8,
    "mild_recovery": (7, 14),
    "percent_severe":  0.2,
    "severe_recovery": (21, 42),
    "severe_death": (14, 56),
    "fatality_rate": 0.034,
    "serial_interval": 7
}

# Virus Class that contains all of our functions -- dictionary with our basic numbers


class Virus():
    def __init__(self, params):
        # polar plot (visualization with virus spreading from the center)
        self.fig = plt.figure()  # initializing an empty plot

        # 111: 1x1 subplot using the first graph
        self.axes = self.fig.add_subplot(111, projection="polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_ylim(0, 1)

        # Creating annotations
        self.day_text = self.axes.annotate(
            # centered at the top of the plot, r
            "Day 0", xy=[np.pi/2, 1], ha="center", va="bottom"
        )

        self.infected_text = self.axes.annotate(
            # texts are in the bottom
            "Infected: 0", xy=[3*np.pi/2, 1], ha="center", va="top", color=RED
        )

        self.deaths_text = self.axes.annotate(
            "\nDeaths: 0", xy=[3*np.pi/2, 1], ha="center", va="top", color=BLACK
        )

        self.recovered_text = self.axes.annotate(
            "\n\nRecovered: 0", xy=[3*np.pi/2, 1], ha="center", va="top", color=GREEN
        )

        # Creating member variables
        self.day = 0
        self.total_num_infected = 0
        self.num_currently_infected = 0
        self.num_recovered = 0
        self.num_deaths = 0
        # contagiousness of disease, reproduction
        self.r0 = COVID19_Params["r0"]
        self.percent_mild = COVID19_Params["percent_mild"]
        self.percent_severe = COVID19_Params["percent_severe"]
        self.fatality_rate = COVID19_Params["fatality_rate"]
        # average time between successive cases
        self.serial_interval = COVID19_Params["serial_interval"]

        self.mild_fast = COVID19_Params["incubation"] + \
            COVID19_Params["mild_recovery"][0]
        self.mild_slow = COVID19_Params["incubation"] + \
            COVID19_Params["mild_recovery"][1]
        self.severe_fast = COVID19_Params["incubation"] + \
            COVID19_Params["severe_recovery"][0]
        self.severe_slow = COVID19_Params["incubation"] + \
            COVID19_Params["severe_recovery"][1]
        self.death_fast = COVID19_Params["incubation"] + \
            COVID19_Params["severe_death"][0]
        self.death_slow = COVID19_Params["incubation"] + \
            COVID19_Params["severe_death"][1]

        self.mild = {i: {"thetas": [], "rs": []}
                     for i in range(self.mild_fast, 365)}
        self.severe = {
            "recovery": {i: {"thetas": [], "rs": []} for i in range(self.severe_fast, 365)},
            "death": {i: {"thetas": [], "rs": []} for i in range(self.death_fast, 365)}
        }

        # Amount of people who have been exposed to the virus already
        self.exposed_before = 0
        # Amount of people who will be exposed after the end of the current wave
        self.exposed_after = 1

        self.initial_population

    def initial_population(self):
        population = 4500
        self.num_currently_infected = 1
        self.total_num_infected = 1
        indices = np.arange(0, population) + 0.5
        self.thetas = np.pi*(1+5**0.5) * indices
        self.rs = np.sqrt(indices/population)
        self.plot = self.axes.scatter(self.thetas, self.rs, s=5, color=GREY)

        # patient zero
        self.axes.scatter(self.thetas[0], self.rs[0], s=5, color=RED)
        self.mild[self.mild_fast]["thetas"].append(self.thetas[0])
        self.mild[self.mild_fast]["rs"].append(self.rs[0])

    def spread_virus(self, i):
        self.exposed_before = self.exposed_after
        if self.day % self.serial_interval == 0 and self.exposed_before < 4500:
            self.num_new_infected = round(self.r0*self.total_num_infected)
            self.exposed_after += round(self.num_new_infected*1.1)
            if self.exposed_after > 4500:
                self.num_new_infected = round((4500-self.exposed_before)*0.9)
                self.exposed_after = 4500
            self.num_currently_infected += self.num_new_infected
            self.total_num_infected += self.num_new_infected
            self.new_infected_indices = list(
                np.random.choice(
                    range(self.exposed_before, self.exposed_after),
                    self.num_new_infected,
                    replace=False
                )
            )
            thetas = [self.thetas[i] for i in self.new_infected_indices]
            rs = [self.rs[i] for i in self.new_infected_indices]

            self.assign_symptoms()

        self.day += 1

    # Assigning symptoms
    def assign_symptoms(self):
        num_mild = round(self.percent_mild * self.num_new_infected)
        num_severe = round(self.percent_severe * self.num_new_infected)

        # Choose a random subset of newly infected to have mild symptoms
        self.mild_indices = np.random.choice(
            self.new_infected_indices, num_mild, replace=False
        )

        # Assign the rest severe symptoms, either ersulting in recovery or death
        remaining_indices = [
            i for i in self.new_infected_indices if i not in self.mild_indices
        ]

        percent_severe_recovery = 1-(self.fatality_rate/self.percent_severe)
        num_severe_recovery = round(percent_severe_recovery * num_severe)
        self.severe_indices = []
        self.death_indices = []
        if remaining_indices:
            self.severe_indices = np.random.choice(
                remaining_indices, num_severe_recovery, replace=False
            )
            self.death_indices = [
                i for i in remaining_indices if i not in self.severe_indices
            ]

        # Assign recovery/death day
        low = self.day + self.mild_fast
        high = self.day + self.mild_slow
        for mild in self.mild_indices:
            recovery_day = np.random.randint(low, high)
            mild_theta = self.thetas[mild]
            mild_r = self.rs[mild]
            self.mild[recovery_day]["thetas"].append(mild_theta)
            self.mild[recovery_day]["rs"].append(mild_r)

        low = self.day + self.severe_fast
        high = self.day + self.severe_slow
        for recovery in self.severe_indices:
            recovery_day = np.random.randint(low, high)
            mild_theta = self.thetas[recovery]
            mild_r = self.rs[recovery]
            self.severe["recovery"][recovery_day]["thetas"].append(mild_theta)
            self.severe["recovery"][recovery_day]["rs"].append(mild_r)

        low = self.day + self.death_fast
        high = self.day + self.death_slow
        for death in self.death_indices:
            death_day = np.random.randint(low, high)
            death_theta = self.thetas[death]
            death_r = self.rs[death]
            self.severe["death"][death_day]["thetas"].append(death_theta)
            self.severe["death"][death_day]["rs"].append(death_r)


Virus(COVID19_Params)
plt.show()
