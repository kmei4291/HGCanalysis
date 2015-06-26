import ROOT
import numpy as n
#import matplotlib.pyplot as plt

#load library with dictionaries for objects in tree
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

#open ROOT file (input and output)
#fIn=ROOT.TFile.Open('/afs/cern.ch/user/p/psilva/public/hgcsummer2015/HGCROIAnalyzer.root')
fIn=ROOT.TFile.Open('/afs/cern.ch/user/k/kmei/public/FastTiming/ntuples/practice_100evts.root')
fOut=ROOT.TFile.Open('simpleMuonAnalysisTree.root','RECREATE')

#read tree from file
tree=fIn.Get('analysis/HGC')
outputTree=ROOT.TTree('ct_zTree','ct_zTree')
dvector=n.zeros(1,dtype=float)
tvector=n.zeros(1,dtype=float)

outputTree.Branch('d',dvector,'d/D')
outputTree.Branch('ct',tvector,'ct/D')
LIGHTSPEED = 29.9792458 #cm/ns

print 'Preparing to analyze %d events'%tree.GetEntriesFast()

eta0 = 1.5 #will float this later

#loop over events in tree
#for i in xrange(0,tree.GetEntriesFast()) :
for i in xrange(54,55) : #debugging issues
	tree.GetEntry(i)

	#Only look at events with reconstructed vertices:
	if tree.Vertices.size() != 0 :


		#print event summary
		print '-'*50
		print '(run,event,lumi)=',tree.run,tree.event,tree.lumi
		print '%d reconstructed vertices' % tree.Vertices.size()
		print 'TRUE: (vx,vy,vz)=',tree.GenVertex.X(),tree.GenVertex.Y(),tree.GenVertex.Z()
		print 'REC: (vx,vy,vz)=',tree.Vertices[0].x_,tree.Vertices[0].y_,tree.Vertices[0].z_

		#loop over the hits
		roiInfo={}
		firstLayerHitTime = 0
		firstLayerHitX = 0
		firstLayerHitY = 0
		firstLayerHitZ = 0
		
		#for now, get the simulated hit time for one layer
		for hit in tree.RecHits:
			if hit.layerId_ != 1 : continue
			if hit.t_ < .05 : continue
			
			firstLayerHitTime =  hit.t_
			firstLayerHitX = hit.x_
			firstLayerHitY = hit.y_
			firstLayerHitZ = hit.z_

		#Formula for the pseudorapidity is -ln(tan(polar_angle)/2) - geometric, but approximate
		for d in my_range(-10,10,.01) :
			r_0 = ROOT.TMath.Sqrt(ROOT.TMath.Power(firstLayerHitX,2)+ROOT.TMath.Power(firstLayerHitY,2)+ROOT.TMath.Power(firstLayerHitZ-d,2))
			eta0 = -1*ROOT.TMath.Log(ROOT.TMath.Tan(ROOT.TMath.ACos(firstLayerHitZ/r_0)/2))
		
			epsd2=(ROOT.TMath.Power(firstLayerHitZ/(firstLayerHitZ-d),2)-1.0)/ROOT.TMath.Power(ROOT.TMath.CosH(eta0),2)
			fullShift = -(1.0/LIGHTSPEED*ROOT.TMath.TanH(eta0))*(firstLayerHitZ-(firstLayerHitZ+d)*ROOT.TMath.Sqrt(1+epsd2))
			ct = 29.9792458*(firstLayerHitTime+fullShift-1.0)
			dvector[0] = d
			tvector[0] = ct
			#print dvector[0], tvector[0]
			outputTree.Fill()
	
#save histos to file
fOut.Write()
fOut.Close()

