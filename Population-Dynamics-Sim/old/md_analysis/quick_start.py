import MDAnalysis as mda
from MDAnalysis.tests.datafiles import PSF, DCD, GRO, XTC
import warnings # to suppress MDA warnings about psf files
warnings.filterwarnings('ignore')

from matplotlib import pyplot as plt

print(mda.Universe(PSF, DCD))
print("Using MDA ver ", mda.__version__)

# IS A STRUCTURE OR TRAJECTORY LOADED?
psf = mda.Universe(PSF)
print(psf)
# ceck for coordinate info
print(hasattr(psf, 'trajectory'))

# SIMULATION OF ENZYME ADENYLATE KINASE SAMPLES A TRANSITION FROM A CLOSED TO AN OPEN CONFORMATION
u = mda.Universe(PSF, DCD)
print(u)
print(len(u.trajectory))

# WORK WITH A GROUP OF ATOMS
print("residues", u.residues)

# ACCESS AN ATOM
print(u.atoms)

# ADDITIONAL OPIONS FOR MANIPULATION AND ANALYSIS
## select atoms wihin the gorup by accessing the list or slicing
## selected atoms can be combined with boolean operations
u.select_atoms("(resname GLU or resname HS*) and name CA and (resid 1:100)")
