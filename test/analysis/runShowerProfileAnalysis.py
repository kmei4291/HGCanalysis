#!/usr/bin/env python

import ROOT
from UserCode.HGCanalysis.PlotUtils import *
from array import array
import os,sys
import optparse
import commands
import threading

"""
Draws the final plots
"""
def showProfiles(histos,norm,genEn,output):

    COLORS=[1,8,9,46,33,2]
    
    #prepare output
    fOut=ROOT.TFile.Open('%s/ShowerProfiles_%d.root'%(output,genEn),'RECREATE')

    stepTitle={'sim':'SimHit',
               'rec':'Perfect cluster',
               'clus':'CMS PF',
               'clus_arbor':'Arbor',
               'clus_pandora':'Pandora',
               'pf':'PF candidate'}
    
    #show the histograms
    canvas     = ROOT.TCanvas('c_%d'%genEn,'c',500,500)
    profCanvas = ROOT.TCanvas('profc_%d'%genEn,'profc',500,500)
    canvas2D   = ROOT.TCanvas('c2d_%d'%genEn,'c2d',1000,1000)
    for var in histos:

        #show 2D
        canvas2D.Clear()
        canvas2D.Divide(2,2)
        i2dCtr=0
        for step in histos[var]:
            i2dCtr=i2dCtr+1
            canvas2D.cd(i2dCtr).SetLogz()
            histos[var][step].Draw('colz')
            MyPaveText(stepTitle[step],0.5,0.8,0.9,0.9).SetTextSize(0.05)
            if i2dCtr==0 : MyPaveText('#bf{CMS} #it{simulation}   E=%3.1f GeV'%genEn).SetTextSize(0.05)

        #inclusive distributions
        canvas.Clear()
        canvas.SetRightMargin(0.15)
        leg=ROOT.TLegend(0.2,0.8,0.5,0.94)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.035)
        varProj=[]
        for step in histos[var]:
            nproj=len(varProj)
            varProj.append( histos[var][step].ProjectionY('%s_%s_proj'%(var,step),1,histos[var][step].GetXaxis().GetNbins()) )
            if varProj[nproj].Integral()==0 : continue
            varProj[nproj].SetMarkerStyle(20+nproj)
            varProj[nproj].SetMarkerColor(COLORS[nproj])
            varProj[nproj].SetLineColor(COLORS[nproj])
            varProj[nproj].SetTitle(stepTitle[step])
            varProj[nproj].SetDirectory(0)
            varProj[nproj].GetYaxis().SetTitle('PDF')
            fixExtremities(varProj[nproj])
            varProj[nproj].Scale(norm)
            leg.AddEntry(varProj[nproj],varProj[nproj].GetTitle(),'p')
            if nproj==0 :
                varProj[nproj].Draw('e1')
                varProj[nproj].GetYaxis().SetRangeUser(0,varProj[nproj].GetMaximum()*1.5)
            else:
                varProj[nproj].Draw('e1same')
        leg.Draw()
        simpt=MyPaveText('#bf{CMS} #it{simulation}   E=%3.1f GeV'%genEn)
        simpt.SetTextSize(0.035)
        simpt.SetTextFont(42)    

        #profiles
        profCanvas.Clear()
        profCanvas.SetRightMargin(0.15)
        profleg=ROOT.TLegend(0.2,0.8,0.5,0.94) 
        profleg.SetFillStyle(0)
        profleg.SetBorderSize(0)
        profleg.SetTextFont(42)
        profleg.SetTextSize(0.035)
        varProfs=[]
        probSum = array('d', [0.5])
        quantiles = array('d', [0.0])
        for step in histos[var]:

            nprof=len(varProfs)
            varProfs.append( ROOT.TGraphErrors() )
            varProfs[nprof].SetMarkerStyle(20+nprof)
            varProfs[nprof].SetMarkerColor(COLORS[nprof])
            varProfs[nprof].SetLineColor(COLORS[nprof])
            varProfs[nprof].SetTitle(stepTitle[step])
            for xbin in xrange(1, histos[var][step].GetXaxis().GetNbins() ):

                #coordinates for this projection
                xcen=histos[var][step].GetXaxis().GetBinCenter(xbin)
                xerr=0.5*histos[var][step].GetXaxis().GetBinWidth(xbin)
                
                #compute the median
                yproj=histos[var][step].ProjectionY('yproj',xbin,xbin)
                if yproj.Integral()==0 : continue
                fixExtremities(yproj)
                yproj.GetQuantiles(1,quantiles,probSum)

                #add to graph
                np=varProfs[nprof].GetN()
                varProfs[nprof].SetPoint(np,xcen,quantiles[0])
                varProfs[nprof].SetPointError(np,xerr,1.253*yproj.GetMeanError())
        
            #compute difference wrt to nprof=0
            chi2,ndf=getChi2(varProfs[0],varProfs[nprof])
            title ='%s #chi^{2} = %3.1f'%(varProfs[nprof].GetTitle(),chi2/ndf)
            profleg.AddEntry(varProfs[nprof],title,'p')
            if nprof==0 :
                varProfs[nprof].Draw('ap')
                varProfs[nprof].GetYaxis().SetRangeUser(0,varProfs[nprof].GetYaxis().GetXmax()*1.5)
                varProfs[nprof].GetYaxis().SetTitle('Median %s'%histos[var][step].GetYaxis().GetTitle())
                varProfs[nprof].GetXaxis().SetTitle(histos[var][step].GetXaxis().GetTitle())
            else:
                varProfs[nprof].Draw('p')

        profleg.Draw()
        profpt=MyPaveText('#bf{CMS} #it{simulation}   E=%3.1f GeV'%genEn)
        profpt.SetTextSize(0.035)
        profpt.SetTextFont(42)    

        #raw_input()
        #save to png
        for c in [canvas,profCanvas,canvas2D]:
            c.Modified()
            c.cd()
            c.SaveAs('%s/%s_%s_en%d.png'%(output,var,c.GetName(),genEn))

        fOut.cd()
        for vp in varProfs:
            vp.Write()

    fOut.Close()

"""
"""
def getLayerLambda(layerIdx,eta=0) :
    eta=ROOT.TMath.Abs(eta)
    geomFactor=1.0
    if eta>1.45 and eta<3.1: geoFactor=1./ROOT.TMath.TanH(eta)

    if layerIdx==0:                   return 0.010*geomFactor
    if layerIdx>=1 and layerIdx<=10:  return 0.036*geomFactor
    if layerIdx>=11 and layerIdx<=20: return 0.043*geomFactor
    if layerIdx>=21 and layerIdx<=29: return 0.056*geomFactor
    if layerIdx==30:                  return 0.338*geomFactor
    if layerIdx>=31 and layerIdx<=41: return 0.273*geomFactor
    if layerIdx>=42 and layerIdx<=53: return 0.475*geomFactor
    return 0
  


"""
Loops over the trees and profiles the showers
"""
def runShowerProfileAnalysis(opt,en):
    
    #max layers to show
    maxLayers=54
    if opt.input.find('Single22')>=0 or opt.input.find('photon')>=0 : maxLayers=30

    #prepare histograms
    baseHistos={
        'area'                     : ROOT.TH2F('area',';HGC layer;Area [cm^{2}];Events',maxLayers,0,maxLayers,50,0,100),
        'showerlength'             : ROOT.TH2F('showerlength',   ';Pseudo-rapidity;Shower length [#lambda];Events ',          5,1.5,3.0,45,0,6),
        'edep'                     : ROOT.TH2F('edep',   ';HGC layer;Energy [MIP];Events ',                                   maxLayers,0,maxLayers,2000,0,5e3),
        'edep_beforestart'         : ROOT.TH2F('edep_beforestart',   ';Starting layer;Energy [MIP];Events ',                  maxLayers,0,maxLayers,2000,0,5e3),
        'edep_afterstart'          : ROOT.TH2F('edep_afterstart',   ';#lambda after start;Energy [MIP];Events ',              45,0,6,2000,0,5e3),
        'nhits'                    : ROOT.TH2F('nhits',  ';HGC layer;Number of hits;Events',             maxLayers,0,maxLayers,1000,0,1000),
        'nhits5mip'                : ROOT.TH2F('nhits5mip',  ';HGC layer;Number of hits(>5 MIP);Events',             maxLayers,0,maxLayers,1000,0,1000),
        'sihih'                    : ROOT.TH2F('sihih',  ';HGC layer;#sigma(#eta,#eta);hits / event',    maxLayers,0,maxLayers,50,0,0.2),
        'sipip'                    : ROOT.TH2F('sipip',  ';HGC layer;#sigma(#phi,#phi);hits / event',    maxLayers,0,maxLayers,50,0,0.2),
        'sipih'                    : ROOT.TH2F('sipih',  ';HGC layer;#sigma(#eta,#phi);hits / event',    maxLayers,0,maxLayers,50,0,0.2)
        }

    #check steps needed to profile
    steps=['rec','clus']
    urlList=opt.input.split(',')
    for url in urlList:
        if url.find('pandoraRECO')>=0: steps.append('clus_pandora')
        if url.find('mqRECO')>=0: steps.append('clus_arbor')

    #instantiate histograms for all
    histos={}
    for var in baseHistos:
        histos[var]={}
        baseHistos[var].Sumw2()
        for step in steps:
            histos[var][step]=baseHistos[var].Clone('%s_%s'%(var,step))
            histos[var][step].SetDirectory(0)

    #loop over available files
    for url in urlList:

        #choose steps to profile
        stepsToProf=[]
        if url.find('pandoraRECO')>=0: 
            stepsToProf.append('clus_pandora')
        elif url.find('mqRECO')>=0: 
            stepsToProf.append('clus_arbor')
        else : 
            stepsToProf.append('rec')
            stepsToProf.append('clus')

        #loop over events
        if url.find('/store/')>=0 : url='root://eoscms//eos/cms/%s'%url
        nEvts=0
        fIn=ROOT.TFile.Open(url)
        HGC=fIn.Get('analysis/HGC')
        print '\t processing %s'%url
        for i in xrange(0,HGC.GetEntriesFast()):
            HGC.GetEntry(i)
            if i%1000==0 : drawProgressBar(float(i)/float(HGC.GetEntriesFast()))

            #kinematics filter
            if HGC.genEn>en+1 or HGC.genEn<en-1 : continue 

            #interaction in HGC
            if HGC.hasInteractionBeforeHGC : continue

            #fully contained shower in HGC
            sumBackHEB=0
            for ilayer in [51,52,53]:
                sumBackHEB+=(getattr(HGC,'edep_sim'))[ilayer-1]
            if sumBackHEB>3 : continue

            #count selected event
            nEvts=nEvts+1

            #init counters
            totalEn={}
            showerLength={}
            for step in stepsToProf:
                totalEn[step]=0
                showerLength[step]=0

            for ilay in xrange(0,HGC.nlay):

                ilambda=getLayerLambda(ilay,HGC.genEta)

                for step in stepsToProf:

                    stepName=step.split('_')[0]

                    #require some energy deposit in the layer and 1 hit
                    ien=getattr(HGC,'edep_%s'%(stepName))[ilay]
                    if ien<0.5: continue
                    nhits=getattr(HGC,'nhits_%s'%(stepName))[ilay]
                    if nhits==0: continue

                    totalEn[step]+=ien

                    #area
                    layerArea=getattr(HGC,'edepArea_%s'%(stepName))[ilay]
                    histos['area'][step].Fill(ilay,layerArea)
                
                    #other simple variables
                    for var in ['edep','nhits','nhits5mip','sihih','sipip','sipih']:
                        varVal=getattr(HGC,'%s_%s'%(var,stepName))[ilay]
                        histos[var][step].Fill(ilay,varVal)
                        if var!='edep': continue
                        if ilay<HGC.layerShowerStart-2: 
                            histos[var+'_beforestart'][step].Fill(ilay,varVal)
                        else:
                            showerLength[step]+=ilambda
                            histos[var+'_afterstart'][step].Fill(showerLength[step],varVal)
                        

            for step in stepsToProf:
                histos['showerlength'][step].Fill(ROOT.TMath.Abs(HGC.genEta),showerLength[step])

        fIn.Close()

    #show results
    if nEvts>10:
        showProfiles(histos=histos,norm=1./nEvts,genEn=en,output=opt.output)
    

"""
steer 
"""
def main():
    
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i',      '--in' ,      dest='input',        help='Input files (CSV)',       default=None)
    parser.add_option('-o',      '--out' ,     dest='output',       help='Output directory',        default='./')
    (opt, args) = parser.parse_args()
                                       
    #check inputs
    if opt.input is None and opt.en is None:
        parser.print_help()
        sys.exit(1)

    #basic ROOT customization
    customROOTstyle()
    #ROOT.gROOT.SetBatch(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)

    
    #launch jobs
    threads = []
    #for en in [10, 20, 40, 50, 75, 100, 125, 175, 250, 400, 500]:
    for en in [10,20,50,75,100,175,250,500] :
        print 'Starting %f'%en
        t=threading.Thread(target=runShowerProfileAnalysis, args=(opt,en,))
        threads.append(t)
        t.start()

    nalive=len(threads)
    while  nalive>0:
        nalive=0
        for t in threads: nalive += t.isAlive()
        #sys.stdout.write("\r %d threads active"%nalive)
        continue
    print 'All done'


if __name__ == "__main__":
    sys.exit(main())
