#include <vector>
#include <interface/SlimmedRecHit.h>

int fastTimingAnalysis()
{
	inputFileName = "/afs/cern.ch/user/k/kmei/public/FastTiming/ntuples/practice.root";
	TFile *f = new TFile(inputFileName);

	TTree *t = f->Get("analysis/HGC");

	std::vector<SlimmedRecHit> RecHits;

	TBranch *bRecHits = t.GetBranch("RecHits");
	bRecHits->SetAddress(&RecHits);
	unsigned int nevent = t.GetEntries();
	for (unsigned int i=0; i<nevent; i++)
	{
		std::cout<<RecHits[0]<<std::endl;
	}
	return 0;
}
