# Primordial-Soup-Simulation:
## Creating hypothetical micro-organisms that simulate, in the most rudimentary sense, the earliest life on Earth.

### Project Goals

I am interested in creating a simple simulation of the evolution by natural selection of very basic organisms (such as cyanobacteria.) In a simplistic view of natural selection, organisms are the vehicles of genetic selection  <reference>. , and there are a variety of machine learning models and algorithms that attempt at capturing such processes <ref>. 

My project takes a slightly different (and perhaps too ambitious) approach to evolutionary algorithms in machine learning by flipping the concept of natural selection on its head: rather than the agents being of the nexus of learning (i.e., selection), learning is conducted by the enviroment and grid where the agents reside. 

## Project Progress

### 12/14/24

#### created the folder structure
After some research, I considered how I wanted to structure this project.

### 12/16/24

#### devising the learning model for the grid

### 12/16/25

#### rudimentary animations
I created basic animations of 3d dots floating around in a 10x10x10 space
My first attempt will to implement a tabular q-learning agent 

### 20/12/25

#### change in project direction and trying MDA
While using matplotlib, I found a severe limitation of creating separate objects for the 3d space. The reason was obvious: matplotlib is for graphical representation; and I needed something more dynamic. So I went back to redefine more clearly the *desiterata* of the project. After some deliberation, I came up with:
1. Make a 3 dismensional simulated environment that models the collated observations of dynamic movement for a single prebiotic chemical (RNA)  parsimoniously
2. only properties outside of the chemical that *allow* the chemical to function for some step interval t0...tN where N >= 5 (the chemical must at least persist for a short period of time)

Based on the desiderata, I find it silly to attempt any kind of X-learning behavior to the object of interest at the moment.

I wanted to get a feel for other simulators. So, I played around with MDAnalysis and learned how to produce an atom group, i.e., a python list with a couple of extra features that are MDA-specific. 