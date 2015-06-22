import ROOT
import numpy as n

print "Writing a tree"

f = ROOT.TFile("tree.root", "recreate")
t = ROOT.TTree("name_of_tree", "tree title")


# create 1 dimensional float arrays (python's float datatype corresponds to c++ doubles)
# as fill variables
a = n.zeros(1, dtype=float)
b = n.zeros(1, dtype=float)

# create the branches and assign the fill-variables to them
t.Branch('normal', a, 'normal/D')
t.Branch('uniform', b, 'uniform/D')

# create some random numbers, fill them into the fill varibles and call Fill()
for i in xrange(100000):
	a[0] = ROOT.gRandom.Gaus()
	b[0] = ROOT.gRandom.Uniform()
	t.Fill()

# write the tree into the output file and close the file
f.Write()
f.Close()
