#include <iostream>
#include <TGraph.h>
#include <cmath>
#include <TTree.h>
#include <TFile.h>

void plotCTvZ_v2()
{
	TFile *f = TFile::Open("simpleMuonAnalysisTree_v2.root");
	TTree *t = (TTree*)f->Get("ct_zTree");	

	//static const Int_t arraySize = 60;
	std::cout<<t->GetEntries()<<std::endl;	
	const Int_t nentries = 5427;
	
	TCanvas *c1 = new TCanvas("c1","Reconstructed Vertex Z-Coordinate v Time",200,10,700,500);
	//c1->SetGrid();
	
	Double_t dvector[nentries];
	Double_t tvector[nentries];
	Double_t d;
	Double_t ct;
	Int_t layer;
	Int_t index;

	t->SetBranchAddress("d",&d);
	t->SetBranchAddress("ct",&ct);
	t->SetBranchAddress("layer",&layer);
	t->SetBranchAddress("index",&index);
	
	//t->GetEntry((Long64_t) 54027);
	//std::cout<<d<<" "<<ct<<std::endl;
	const Int_t maxIndex = 26;
	//std::cout<<maxIndex<<std::endl;
	
	TGraph *graphVector[maxIndex];

	for(unsigned int jentry = 0; jentry < 2; jentry++)
	{
		for (unsigned int i = 0; i < nentries; i++)
		{
			t->GetEntry(i);
			if (index != jentry) continue;
	
			if (std::fabs(d) < 0.01 && std::fabs(ct) < 0.01) std::cout<<jentry<<" "<<d<<" "<<ct<<std::endl;	
			dvector[i] = d;
			tvector[i] = ct;
			
		}
		graphVector[jentry] = new TGraph(nentries,dvector,tvector);
	}
	TMultiGraph *mg = new TMultiGraph;
	mg->Add(graphVector[0]);
	mg->Add(graphVector[1]);	

	//graphVector[1]->Draw("SAME");
	for(unsigned int gindex = 0; gindex < 2; gindex++)
	{	
		//graphVector[gindex]->SetLineColor((gindex % 9)+1);
		/*f(gindex == 0) 
		{
			graphVector[gindex]->Draw("AP");
			graphVector[gindex]->GetXaxis()->SetTitle("Vertex Reconstructed Z-Coordinate [cm]");
			graphVector[gindex]->GetYaxis()->SetTitle("Time of Collision (ct) [cm]");
		}
		else graphVector[gindex]->Draw("SAME");	*/
	}
	mg->Draw("ap");
	Double_t realVertexZ[0] = 2.65302252769;
	Double_t realVertexT[0] = 0.0;
	TGraph *g2 = new TGraph(1,realVertexZ,realVertexT);
	g2->Draw("SAME");
	g2->SetMarkerColor(4);
	g2->SetMarkerStyle(3);
}

