#include<TH2F.h>

int plot()
{
	TFile *f = TFile::Open("simpleMuonAnalysis.root");
	TH2F *maxHits = f->Get("recoVsim");

	
	maxHits->Draw("BOX");
	maxHits->SetTitle("Reconstructed Vertex Z and Time for 1 Muon Events");
	maxHits->SetStats(0);
	return 0;
}

