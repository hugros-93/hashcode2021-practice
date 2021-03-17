from copy import deepcopy
import random
import numpy as np

from source import sort_by_max_ingredients, pizza_compatibility

def load_best_to_start(filename_best):
    with open(filename_best, "r") as f:
        best = f.read().split('\n')[1:]
    dico_best = {'2':[], '3':[], '4':[]}
    for k in dico_best:
        dico_best[k] = [set(x.split(' ')[1:]) for x in best if x.split(' ')[0] == k]
    pizza_solution = [dico_best[k] for k in dico_best]
    return pizza_solution

def get_score(solution, frigo):
    score = 0
    for deliveries in solution:
        for delivery in deliveries:
            ingredients = set().union(*[frigo[int(x)].list_ingredients for x in delivery])
            score += len(ingredients) * len(ingredients)
    return score

class Voisin():
    def __init__(self, actual_solution, frigo, pizza_gate, perturbation=1):
        
        # budgets 
        self.num_available_t2 = pizza_gate.num_t2 - len(actual_solution[0])
        self.num_available_t3 = pizza_gate.num_t3 - len(actual_solution[1])
        self.num_available_t4 = pizza_gate.num_t4 - len(actual_solution[2])

        # pizzas dispo
        set_pizza_used = set().union(*[set().union(*x) for x in actual_solution])
        set_pizza_all = set([str(i) for i in range(pizza_gate.num_pizzas)])
        self.set_pizza_dispo = set_pizza_all - set_pizza_used
        
        # frigo
        self.nouveau_frigo = [x for x in frigo if str(x.pizza_id) in self.set_pizza_dispo]
        
        # create
        self.solution = deepcopy(actual_solution)
        self.frigo = frigo
        self.create(perturbation=perturbation)
        
        # score
        self.score = get_score(self.solution, self.frigo)
    
    def create(self, perturbation):
        for _ in range(perturbation):
            if sum([len(x) for x in self.solution]) == 0: break
            # deteriorate solution
            j = random.choice([i for i,k in enumerate(self.solution) if k])
            if j == 0:
                self.num_available_t2 += 1
            elif j == 1:
                self.num_available_t3 += 1
            elif j == 2:
                self.num_available_t4 += 1

            s = [get_score([[i]], self.frigo) for i in self.solution[j]]
            p = self.solution[j][np.argmin(s)]
            # p = random.choice(self.solution[j])

            self.solution[j].remove(p)
            self.set_pizza_dispo = self.set_pizza_dispo.union(p)
            
            # maj frigo
            self.nouveau_frigo = [x for x in self.frigo if str(x.pizza_id) in self.set_pizza_dispo]

        # reconstruct new solution
        new_deliveries = self.mon_heuristique_eclatee_2_rue()
        for d in new_deliveries:
            self.solution[d[0]-2].append(d[1])
            if d[0] == 2:
                self.num_available_t2 -= 1
            elif d[0] == 3:
                self.num_available_t3 -= 1
            elif d[0] == 4:
                self.num_available_t4 -= 1

    def mon_heuristique_eclatee_2_rue(self):
        out = []
        sorted_pizza = sort_by_max_ingredients(self.nouveau_frigo)

        list_teams_available = [self.num_available_t4, 
                                self.num_available_t3, 
                                self.num_available_t2]
        list_teams_size = [4,3,2]
        
        c = list(zip(list_teams_available, list_teams_size))
        random.shuffle(c)
        list_teams_available, list_teams_size = zip(*c)
        
        for num_team, team_size in zip(list_teams_available, list_teams_size):
            if len(self.nouveau_frigo) >= team_size:
                for _ in range(num_team):
                    tempo_pizza_sol = []
                    if len(sorted_pizza) == 0: break
                    best_pizza = sorted_pizza.pop(0)
                    tempo_pizza_sol.append(best_pizza)

                    for _ in range(team_size-1):
                        # Get best pizza
                        if len(sorted_pizza) == 0: break
                        best_pizza = max(sorted_pizza, key=lambda x: pizza_compatibility(tempo_pizza_sol,x))

                        # remove best pizza from list
                        sorted_pizza.pop(sorted_pizza.index(best_pizza))
                        tempo_pizza_sol.append(best_pizza)

                    out.append([team_size, set([str(x.pizza_id) for x in tempo_pizza_sol])])
        return out