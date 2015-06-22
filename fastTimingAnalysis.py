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

eta0 = 1.5

#loop over events in tree
#for i in xrange(0,tree.GetEntriesFast()) :
for i in xrange(0,4) : #debugging issues
	tree.GetEntry(i)

	#Only look at events with reconstructed vertices:
	if tree.Vertices.size() != 0 :#or tree.Vertices.size() == 0: 


		#print event summary
		print '-'*50
		print '(run,event,lumi)=',tree.run,tree.event,tree.lumi
		print '%d reconstructed vertices' % tree.Vertices.size()
		print 'TRUE: (vx,vy,vz)=',tree.GenVertex.X(),tree.GenVertex.Y(),tree.GenVertex.Z()
		print 'REC: (vx,vy,vz)=',tree.Vertices[0].x_,tree.Vertices[0].y_,tree.Vertices[0].z_

		#loop over the hits
		roiInfo={}
		firstHitFound = 0
		hitFirstLayer = 0
		hitT = 0
		hitX = 0
		hitY = 0
		hitZ = 0
		
		for hit in tree.RecHits:
			
			#select hits with timing information
			if hit.t_<0: continue
	
			#if first layer with a hit has already been found, skip the following layers
			elif firstHitFound == 1: continue

			#fill histogram with the hits
			else:
				firstHitFound = 1
				hitFirstLayer = hit.layerId_
				hitT = hit.t_ - 1
				hitX = hit.x_
				hitY = hit.y_
				hitZ = hit.z_

		#print firstHitFound,hitT,hitX,hitY,hitZ,hitFirstLayer
		layerH.Fill(hitFirstLayer)
		ct = 29.9792458*hitT
		if ct != 0:
			recoVSsimH.Fill(ct, tree.Vertices[0].z_)
		distance=ROOT.TMath.Sqrt(ROOT.TMath.Power(hitX-tree.Vertices[0].x_,2)+ROOT.TMath.Power(hitY-tree.Vertices[0].y_,2)+ROOT.TMath.Power(hitZ-tree.Vertices[0].z_,2))
		print ct,distance,tree.Vertices[0].z_
		ctMinusZH.Fill(ct - tree.Vertices[0].z_)
		
		d=tree.GenVertex.z() 		#true vertex position
		#z=tree.ROIs[roiId].stablez_ 	#true interaction in the detector
		#eta0=tree.ROIs[roiId].eta_ 	#pseudo-rapidity (geometric)
		#LIGHTSPEED=29.9792458 #cm/ns
		
		#simpleShift = d/(LIGHTSPEED*ROOT.TMath.TanH(eta0))
		#collTimeH.Fill(avgT+simpleShift-1.0)
	
		#epsd2=(ROOT.TMath.Power(hitZ/(hitZ-d),2)-1.0)/ROOT.TMath.Power(ROOT.TMath.CosH(eta0),2)
		#fullShift = -(1.0/LIGHTSPEED*ROOT.TMath.TanH(eta0))*(z-(z+d)*ROOT.TMath.Sqrt(1+epsd2))
		#collTimeFullH.Fill(avgT+fullShift-1.0)
	
#save histos to file
fOut=ROOT.TFile.Open('simpleMuonAnalysis.root','RECREATE')
layerH.Write()
ctMinusZH.Write()
recoVSsimH.Write()
fOut.Close()

