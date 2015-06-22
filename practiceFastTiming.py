import ROOT

#load library with dictionaries for objects in tree
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

#open ROOT file
#fIn=ROOT.TFile.Open('/afs/cern.ch/user/p/psilva/public/hgcsummer2015/HGCROIAnalyzer.root')
fIn=ROOT.TFile.Open('/afs/cern.ch/user/k/kmei/public/FastTiming/ntuples/practice_50evts.root')

#read tree from file
tree=fIn.Get('analysis/HGC')
print 'Preparing to analyze %d events'%tree.GetEntriesFast()

#prepare some control histogram
#collTimeH = ROOT.TH1F('colltime_simple',';Collision time[ns];Regions of interest',100,-0.2,0.2)
#collTimeFullH = ROOT.TH1F('colltime_full',';Collision time[ns];Regions of interest',100,-0.2,0.2)
hitTimeH = ROOT.TH2F('hitTime_simple',';Hit Time[ns];Distance along Beam Axis[cm]',10,1.06,1.1,20,300,380)
maxHitTimeH = ROOT.TH2F('maxHitTime_simple',';Hit Time[ns];Distance along Beam Axis[cm]',10,0.7,1.3,10,300,380)
#hitEtaH = ROOT.TH1F('hitEta_simple',';Hit Eta',10,-3,3)

#loop over events in tree
for i in xrange(0,tree.GetEntriesFast()) :
	tree.GetEntry(i)

	#print event summary
	print '-'*50
	print '(run,event,lumi)=',tree.run,tree.event,tree.lumi
	print '(vx,vy,vz)=',tree.GenVertex.X(),tree.GenVertex.Y(),tree.GenVertex.Z()
	print '%d reconstructed vertices' % tree.Vertices.size()
	if tree.Vertices.size() != 0 : print 'REC: (vx,vy,vz)=',tree.Vertices[0].x_,tree.Vertices[0].y_,tree.Vertices[0].z_
	#print '%d rec hits, in %d clusters, in %d ROIs' % (tree.RecHits.size(),tree.Clusters.size(),tree.ROIs.size())

	#loop over the hits
	roiInfo={}
	maxTimeHit = 0
	maxTimeZ = 0
	for hit in tree.RecHits:
		#select hits with time
		#if hit.t_<0: continue
		#if hit.z_<0: continue

		#fill histogram with the hits
		hitTimeH.Fill(hit.t_,hit.z_)
		if hit.layerId_ == 1 : print(hit.z_, hit.t_, hit.layerId_) 
		
		if hit.t_>maxTimeHit:
			maxTimeHit=hit.t_
			maxTimeZ=hit.z_
		#hitEtaH.Fill(hit.eta_)
	maxHitTimeH.Fill(maxTimeHit,maxTimeZ)
		#get the region of interest	
		#roiId= tree.Clusters[ hit.clustId_ ].roiidx_
	
		#init hit, energy and timing counters
		#if not roiId in roiInfo : roiInfo[roiId]=[0.,0.,0.,0.]
		#roiInfo[roiId][0] += 1
		#roiInfo[roiId][1] += hit.en_
		#roiInfo[roiId][2] += hit.t_
		#roiInfo[roiId][3] += hit.t_*hit.en_

		#print roiInfo[roiId][0]
	
	#now finish the averages and print information on ROI
	#for roiID in roiInfo:
	
		#id of the matched particle
		#particleMatchId=tree.ROIs[roiId].stableid_
		
		#place of interaction of the matched particle (if>317 cm then it happened in HGC)
		#zinter=ROOT.TMath.Abs(tree.ROIs[roiId].stablez_)
	
		#at least one hit found must be required
		#if roiInfo[roiId][0]==0 : continue
	
		#finish averages
		#avgT		= roiInfo[roiId][2]/roiInfo[roiId][0]
		#avgT_weightedE 	= roiInfo[roiId][3]/roiInfo[roiId][1]
	
		#print information
		#print 'ROI #%d matched to %d (z_{inter}=%fcm) avgT=%fns avgT_weightedE=%fns' %(roiId,particleMatchId,zinter,avgT,avgT_weightedE)

	d=tree.GenVertex.z() 		#true vertex position
	#z=tree.ROIs[roiId].stablez_ 	#true interaction in the detector
	#eta0=tree.ROIs[roiId].eta_ 	#pseudo-rapidity (geometric)
	#LIGHTSPEED=29.9792458 #cm/ns
	
	#simpleShift = d/(LIGHTSPEED*ROOT.TMath.TanH(eta0))
	#collTimeH.Fill(avgT+simpleShift-1.0)

	#epsd2=(ROOT.TMath.Power(z/(z+d),2)-1.0)/ROOT.TMath.Power(ROOT.TMath.CosH(eta0),2)
	#fullShift = -(1.0/LIGHTSPEED*ROOT.TMath.TanH(eta0))*(z-(z+d)*ROOT.TMath.Sqrt(1+epsd2))
	#collTimeFullH.Fill(avgT+fullShift-1.0)

#save histos to file
fOut=ROOT.TFile.Open('simpleMuonAnalysis.root','RECREATE')
#hitEtaH.Write()
hitTimeH.Write()
maxHitTimeH.Write()
fOut.Close()
