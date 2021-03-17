from tqdm import tqdm
from operator import attrgetter
import numpy as np
import copy

class Pizza():
    
    def __init__(self, pizza_id, num_ingredients, list_ingredients):
        self.pizza_id = pizza_id
        self.num_ingredients = num_ingredients
        self.list_ingredients = list_ingredients
        
    def __repr__(self):
        representation = "Pizza:" 
        representation += "\n  id : \t"+str(self.pizza_id)
        representation += "\n  num : \t"+str(self.num_ingredients)
        representation += "\n  ing : \t"+str(self.list_ingredients)
        return representation
    
    @classmethod
    def from_line(cls, line, line_id):
        line_data = line.split()
        num_ingredients = int(line_data[0])
        list_ingredients = line_data[1:]
        return cls(line_id, num_ingredients, list_ingredients)

class PizzaProblem():
    def __init__(self, num_pizzas, num_t2, num_t3, num_t4):
        self.num_pizzas = int(num_pizzas)
        self.num_t2 = int(num_t2)
        self.num_t3 = int(num_t3)
        self.num_t4 = int(num_t4)
    
    def __repr__(self):
        representation = "Problem:"
        representation += "\npizzas:\t"+str(self.num_pizzas)
        representation += "\nnum T2:\t"+str(self.num_t2)
        representation += "\nnum T3:\t"+str(self.num_t3)
        representation += "\nnum T4:\t"+str(self.num_t4)
        return representation

def get_data(input_file):
    frigo = []
    with open(input_file, "r") as file:

        problem_data = file.readline()

        pizza_gate = PizzaProblem(*problem_data.split())

        for idx, line in enumerate(file):
            pizza_eclatax = Pizza.from_line(line, idx)
            frigo.append(pizza_eclatax)
    return frigo, pizza_gate

def sort_by_max_ingredients(pizza_list):
    from operator import  attrgetter

    pizza_list.sort(reverse=True, key=attrgetter("num_ingredients") )

    return pizza_list

def sort_by_max_compat(chosen_pizzas, pizza_list):
    pizza_list.sort(reverse=True, key=lambda x: pizza_compatibility(chosen_pizzas, x) )
    
    return pizza_list

def pizza_list_compatibility(pizza_set, challenger_pizza):
    challenger_ingr = set(challenger_pizza.list_ingredients)

    improvement = (len(challenger_ingr) - len(challenger_ingr.intersection(pizza_set)))/len(challenger_ingr)


def pizza_compatibility(pizza_list, challenger_pizza, limit_ingredients):

    # Get ingredient of challenger_pizza
    challenger_ingr = challenger_pizza.list_ingredients
    
    # Check if already existing pizza is list or Pizza
    if type(pizza_list) == list :
        existing_ingr = []
        for piz in pizza_list:
            existing_ingr += piz.list_ingredients[:limit_ingredients]
    elif isinstance(pizza_list,Pizza):
        existing_ingr = pizza_list.list_ingredients[:limit_ingredients]

    # Remove duplicates 
    existing_ingr = set(existing_ingr)
    challenger_ingr = set(challenger_ingr)
    
    improvement = (len(challenger_ingr) - len(challenger_ingr.intersection(existing_ingr)))/len(challenger_ingr)
    return improvement
    
def mon_heuristique_eclatee(pizza_list, problem_class, limit_ingredients=None, limit_pizzas = None):

    if not limit_pizzas:
        limit_pizzas = problem_class.num_pizzas
    if not limit_ingredients:
        limit_ingredients = int(1e10)
    
    print("la magie opère ici")
    solution = [] 
    sorted_pizza = sort_by_max_ingredients(pizza_list)

    for num_team, team_size in zip([problem_class.num_t4, problem_class.num_t3, problem_class.num_t2],[4,3,2]):
        print("===== team of",team_size)
        print("===== ",num_team,"to process")

        for team in tqdm(range(num_team)):

            tempo_pizza_sol = []
            if len(sorted_pizza) == 0: break
            best_pizza = sorted_pizza.pop(0)
            tempo_pizza_sol.append(best_pizza)
            tempo_ingredient_set = best_pizza.list_ingredients
            tempo_ingredient_set = set(tempo_ingredient_set)
            for remaning_pizza in range(team_size-1):
                # Get best pizza
                if len(sorted_pizza) == 0: break

                best_pizza = max(sorted_pizza[:limit_pizzas], key=lambda x: pizza_compatibility(tempo_ingredient_set,x, limit_ingredients))
                # remove best pizza from list
                sorted_pizza.pop(sorted_pizza.index(best_pizza))
                tempo_pizza_sol.append(best_pizza)
                tempo_ingredient_set = tempo_ingredient_set.union(best_pizza.list_ingredients)
                
            solution.append(str(team_size)+' '+' '.join([str(x.pizza_id) for x in tempo_pizza_sol]))
    return solution

def consolidate_results(solution):
    definitive_solution = []
    shipped_pizzas = 0
    for idx, sol in enumerate(solution):
        data = sol.split()
        if int(data[0]) == len(data[1:]):
            definitive_solution.append(sol)
            shipped_pizzas += int(data[0])
            
    return definitive_solution, shipped_pizzas     

def format_resutlts(solution, input_file):
    with open('./outputs/'+input_file.split('/')[-1]+'.out','w') as file:
        file.write(str(len(solution)))
        for sol in solution:
            file.write('\n'+sol)
        file.write('\n')


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str)
    args = parser.parse_args()
    print(args.input_file)

    print(args.input_file.split('/')[2])
    frigo, pizza_gate = get_data(args.input_file)

    pizza_solution = mon_heuristique_eclatee(
        frigo, 
        pizza_gate, 
        limit_ingredients=None, 
        limit_pizzas=10000)
    
    definitive_pizza_solution, shipped_piz = consolidate_results(pizza_solution)
    print(shipped_piz,"pizzas shipped over",pizza_gate.num_pizzas)
    format_resutlts(definitive_pizza_solution, args.input_file)

    from source_ts import *
    filename_best = f"./outputs/{args.input_file.split('/')[2]}.out"
    solution = load_best_to_start(filename_best)
    frigo, pizza_gate = get_data(args.input_file)
    best_score = get_score(solution, frigo)
    print(f'> best score : {best_score}')
