void plotCTvZ()
{
	TFile *f = TFile::Open("simpleMuonAnalysisTree.root");
	TTree *t = (TTree*)f->Get("ct_zTree");	

	TCanvas *c1 = new TCanvas("c1","Reconstructed Vertex Z-Coordinate v Time",200,10,700,500);
	c1->SetGrid();

	//static const Int_t arraySize = 60;
	std::cout<<t->GetEntries()<<std::endl;	
	const Int_t nentries = 2001;
	
	Double_t dvector[nentries];
	Double_t tvector[nentries];
	Double_t d;
	Double_t ct;

	t->SetBranchAddress("d",&d);
	t->SetBranchAddress("ct",&ct);


	for (unsigned int i = 0; i < nentries; i++)
	{
		t->GetEntry(i);
		dvector[i] = d;
		tvector[i] = ct;
	}
	
	Double_t realVertexZ[0] = 2.65302252769;
	Double_t realVertexT[0] = 0.0;
	
	TGraph *g = new TGraph(nentries,dvector,tvector);
	TGraph *g2 = new TGraph(1,realVertexZ,realVertexT);
	//g->SetLineColor(2);
	//g->SetLineWidth(4);
	g->Draw("ACP");	
	g->GetXaxis()->SetTitle("Vertex Reconstructed Z-Coordinate [cm]");
	g->GetYaxis()->SetTitle("Time of Collision (ct) [cm]");
	g2->Draw("SAMECP");
	g2->SetMarkerColor(4);
	g2->SetMarkerStyle(3);
	//g.SetStats(0);
}

