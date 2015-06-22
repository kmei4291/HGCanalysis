import ROOT

#load library with dictionaries for objects in tree
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

#open ROOT file
#fIn=ROOT.TFile.Open('/afs/cern.ch/user/p/psilva/public/hgcsummer2015/HGCROIAnalyzer.root')
fIn=ROOT.TFile.Open('/afs/cern.ch/user/k/kmei/public/FastTiming/ntuples/practice_1evt.root')

#read tree from file
tree=fIn.Get('analysis/HGC')
print 'Preparing to analyze %d events'%tree.GetEntriesFast()

#prepare some control histogram
collTimeH = ROOT.TH1F('colltime_simple',';Collision time[ns];Regions of interest',100,-0.2,0.2)
collTimeFullH = ROOT.TH1F('colltime_full',';Collision time[ns];Regions of interest',100,-0.2,0.2)

#loop over events in tree
for i in xrange(0,tree.GetEntriesFast()) :
	tree.GetEntry(i)

	#print event summary
	print '-'*50
	print '(run,event,lumi)=',tree.run,tree.event,tree.lumi
	print '(vx,vy,vz)=',tree.GenVertex.X(),tree.GenVertex.Y(),tree.GenVertex.Z()
	print '%d reconstructed vertices' % tree.Vertices.size()
	print '%d rec hits, in %d clusters, in %d ROIs' % (tree.RecHits.size(),tree.Clusters.size(),tree.ROIs.size())

	#loop over the hits
	roiInfo={}
	for hit in tree.RecHits:

		#select hits with time
		if hit.t_<0: continue
		
		#get the region of interest
		roiId= tree.Clusters[ hit.clustId_ ].roiidx_
	
		#init hit, energy and timing counters
		if not roiId in roiInfo : roiInfo[roiId]=[0.,0.,0.,0.]
		roiInfo[roiId][0] += 1
		roiInfo[roiId][1] += hit.en_
		roiInfo[roiId][2] += hit.t_
		roiInfo[roiId][3] += hit.t_*hit.en_
	
	#now finish the averages and print information on ROI
	for roiId in roiInfo:
	
		#id of the matched particle
		particleMatchId=tree.ROIs[roiId].stableid_
		
		#place of interaction of the matched particle (if>317 cm then it happened in HGC)
		zinter=ROOT.TMath.Abs(tree.ROIs[roiId].stablez_)
	
		#at least one hit found must be required
		if roiInfo[roiId][0]==0 : continue
	
		#finish averages
		avgT		= roiInfo[roiId][2]/roiInfo[roiId][0]
		avgT_weightedE 	= roiInfo[roiId][3]/roiInfo[roiId][1]
	
		#print information
		print 'ROI #%d matched to %d (z_{inter}=%fcm) avgT=%fns avgT_weightedE=%fns' %(roiId,particleMatchId,zinter,avgT,avgT_weightedE)

		d=tree.GenVertex.z() 		#true vertex position
		z=tree.ROIs[roiId].stablez_ 	#true interaction in the detector
		eta0=tree.ROIs[roiId].eta_ 	#pseudo-rapidity (geometric)
		print d,z,eta0
		LIGHTSPEED=29.9792458 #cm/ns
	
		simpleShift = d/(LIGHTSPEED*ROOT.TMath.TanH(eta0))
		collTimeH.Fill(avgT+simpleShift-1.0)

		epsd2=(ROOT.TMath.Power(z/(z+d),2)-1.0)/ROOT.TMath.Power(ROOT.TMath.CosH(eta0),2)
		fullShift = -(1.0/LIGHTSPEED*ROOT.TMath.TanH(eta0))*(z-(z+d)*ROOT.TMath.Sqrt(1+epsd2))
		collTimeFullH.Fill(avgT+fullShift-1.0)

#save histos to file
fOut=ROOT.TFile.Open('SimpleHitAnalysis.root','RECREATE')
collTimeH.Write()
collTimeFullH.Write()
fOut.Close()


