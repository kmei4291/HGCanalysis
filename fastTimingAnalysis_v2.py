import ROOT

#load library with dictionaries for objects in tree
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

#open ROOT file
#fIn=ROOT.TFile.Open('/afs/cern.ch/user/p/psilva/public/hgcsummer2015/HGCROIAnalyzer.root')
fIn=ROOT.TFile.Open('/afs/cern.ch/user/k/kmei/public/FastTiming/ntuples/practice_100evts.root')

#read tree from file
tree=fIn.Get('analysis/HGC')
print 'Preparing to analyze %d events'%tree.GetEntriesFast()

#prepare some control histogram
recoVSsimH = ROOT.TH2F('recoVsim',';Collision time (ct) [cm];Reconstructed Vertex Z-Coordinate[cm]',100,20,20,100,-20,20)
ctMinusZH  = ROOT.TH1F('ctMinusZ',';ct - Z[cm];Number of Events',10,-10,10)

eta0 = 1.5 #will float this later
d = 0.0 #default

#loop over events in tree
#for i in xrange(0,tree.GetEntriesFast()) :
for i in xrange(0,4) : #debugging issues
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
			
			firstLayerHitTime =  hit.simT_[0]
			firstLayerHitX = hit.x_
			firstLayerHitY = hit.y_
			firstLayerHitZ = hit.z_

		#Formula for the pseudorapidity is -ln(tan(polar_angle)/2) - geometric, but approximate
		r_0 = ROOT.TMath.Sqrt(ROOT.TMath.Power(firstLayerHitX,2)+ROOT.TMath.Power(firstLayerHitY,2)+ROOT.TMath.Power(firstLayerHitZ-d,2))
		eta0 = -1*ROOT.TMath.Log(ROOT.TMath.Tan(ROOT.TMath.ACos(firstLayerHitZ/r_0)/2))
		print eta0
		ct = 29.9792458*firstLayerHitTime
		LIGHTSPEED = 29.9792458 #cm/ns
		
		#simpleShift = d/(LIGHTSPEED*ROOT.TMath.TanH(eta0))
		#collTimeH.Fill(avgT+simpleShift-1.0)
	
		epsd2=(ROOT.TMath.Power(firstLayerHitZ/(firstLayerHitZ-d),2)-1.0)/ROOT.TMath.Power(ROOT.TMath.CosH(eta0),2)
		fullShift = -(1.0/LIGHTSPEED*ROOT.TMath.TanH(eta0))*(firstLayerHitZ-(firstLayerHitZ+d)*ROOT.TMath.Sqrt(1+epsd2))
		print (firstLayerHitTime+fullShift-1.0)
		#collTimeFullH.Fill(avgT+fullShift-1.0)
	
#save histos to file
#fOut=ROOT.TFile.Open('simpleMuonAnalysis.root','RECREATE')
#ctMinusZH.Write()
#recoVSsimH.Write()
#fOut.Close()
