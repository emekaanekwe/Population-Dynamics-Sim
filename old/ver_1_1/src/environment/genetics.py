from numpy import random
'''
the base pairs:
A-T
C-G

'''
class Genetics:
    def __init__(self, a, t, c ,g, base_map: dict, sequence: list):
        self.a = "A"
        self.t = "T"
        self.c = "C"
        self.g = "G"
        self.sequence = []
        self.base_map = base_map

    base_at = {
       0: "A",
       1: "T"
        }
    base_cg = {
       0, "C",
       1, "G",
        }
        
    def generate_sequence(self):
     if len(self.sequence) = 300:
         return
     else:
        nucleotide_0 = base_at[random.randint(0,1)]
        self.sequence.append(nucleotide_0) 
        if nucleotide_0 == "A":
            self.sequence.append("T")
        else:
            self.sequence.append("A")

        return generate_sequence(self.sequence)
            
         
        sequence.append(base_at[random.randint(0,1)]

        sequence.append(base_cg[random.randint(0,1)
        sequence.append(base_cg[random.randint(0,1)    
    