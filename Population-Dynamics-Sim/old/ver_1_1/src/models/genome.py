import numpy as np
import random

# Define agent genome and fitness function
def initialize_population(pop_size, genome_length):
    return [np.random.uniform(-1, 1, genome_length) for _ in range(pop_size)]

def fitness_function(agent, grid):
    """
    Evaluate agent performance on the grid.
    Example: Reward for finding food, penalty for hitting obstacles.
    """
    fitness = 0
    # Example: Implement a simulation of agent behavior
    # Example logic: fitness += 10 for each food found, -5 for collisions
    return fitness

def mutate(genome, mutation_rate):
    for i in range(len(genome)):
        if random.random() < mutation_rate:
            genome[i] += np.random.normal(0, 0.1)  # Small Gaussian mutation
    return genome

def crossover(parent1, parent2):
    cut = random.randint(0, len(parent1) - 1)
    child = np.concatenate((parent1[:cut], parent2[cut:]))
    return child

def genetic_algorithm(pop_size, genome_length, generations, mutation_rate, grid):
    population = initialize_population(pop_size, genome_length)
    for generation in range(generations):
        # Evaluate fitness
        fitness_scores = [fitness_function(agent, grid) for agent in population]
        # Select top-performing agents
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
        next_gen = sorted_population[:pop_size // 2]  # Top 50%
        # Reproduce
        children = [mutate(crossover(random.choice(next_gen), random.choice(next_gen)), mutation_rate)
                    for _ in range(pop_size - len(next_gen))]
        population = next_gen + children
        print(f"Generation {generation}, Best Fitness: {max(fitness_scores)}")
    return population