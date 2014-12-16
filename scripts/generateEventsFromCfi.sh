#!/bin/bash


#
# PARSE CONFIGURATION PARAMETERS
#
PID=211
ENERGY=25
NEVENTS=100
CFI=UserCode/HGCanalysis/python/particleGun_cfi.py
WORKDIR="/tmp/`whoami`/"
STOREDIR=${WORKDIR}
JOBNB=1
GEOMETRY="Extended2023HGCalMuon,Extended2023HGCalMuonReco"
EE_AIR=""
HEF_AIR=""
TAG=""
PHYSLIST="QGSP_FTFP_BERT_EML"
TKFILTER=""

while getopts "hp:e:n:c:o:w:j:g:t:l:xzf" opt; do
    case "$opt" in
    h)
        echo ""
        echo "generateEventsFromCfi.sh [OPTIONS]"
	echo "     -p      pdg ids to generate (csv)"
	echo "     -e      energy to generate"
	echo "     -n      number of events go generate"
	echo "     -c      cfi to use with cmsDriver command"
	echo "     -o      output directory (local or eos)"
	echo "     -w      local work directory (by default /tmp/user)"
	echo "     -l      GEANT4 physics list: QGSP_FTFP_BERT_EML (default) / FTFP_BERT_EML / FTFP_BERT_XS_EML / QBBC"
        echo "     -j      job number"
	echo "     -g      geometry"
	echo "             v4:            Extended2023HGCalV4Muon,Extended2023HGCalV4MuonReco"
	echo "             v5 (default) : ${GEOMETRY}"
	echo "     -x      exclude EE (turn into air)"
	echo "     -z      exclude HEF (turn into air)"
        echo "     -t      tag to name output file"
	echo "     -f      filter events interacting before HGC"
	echo "     -h      help"
        echo ""
	exit 0
        ;;
    l)  PHYSLIST=$OPTARG
	;;
    p)  PID=$OPTARG
        ;;
    e)  ENERGY=$OPTARG
        ;;
    n)  NEVENTS=$OPTARG
        ;;
    c)  CFI=$OPTARG
        ;;
    o)  STOREDIR=$OPTARG
	;;
    w)  WORKDIR=$OPTARG
	;;
    j)  JOBNB=$OPTARG
	;;
    g)  GEOMETRY=$OPTARG
	;;
    x)  EE_AIR="True"
	;;
    z)  HEF_AIR="True"
	;;
    t)  TAG=$OPTARG
        ;;
    f)  TKFILTER="True"
	;;
    esac
done

#
# CONFIGURE JOB
#
if [ "$TAG" = "" ]; then
   TAG=${PID}_${ENERGY}
   if [[ "${EE_AIR}" != "" ]]; then
       TAG="${TAG}_NOEE"
   fi
   if [[ "${HEF_AIR}" != "" ]]; then
       TAG="${TAG}_NOHEF"
   fi
fi
BASEJOBNAME=Events_${TAG}_${JOBNB}
BASEJOBNAME=${BASEJOBNAME/","/"_"}
OUTFILE=${BASEJOBNAME}.root
PYFILE=${BASEJOBNAME}_cfg.py
LOGFILE=${BASEJOBNAME}.log

#run cmsDriver
cmsDriver.py ${CFI} -n ${NEVENTS} \
    --python_filename ${WORKDIR}/${PYFILE} --fileout file:${WORKDIR}/${OUTFILE} \
    -s GEN,SIM,DIGI:pdigi_valid,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO --datatier GEN-SIM-DIGI-RECO --eventcontent FEVTDEBUGHLT \
    --conditions auto:upgradePLS3 --beamspot Gauss --magField 38T_PostLS1 \
    --customise SLHCUpgradeSimulations/Configuration/combinedCustoms.cust_2023HGCalMuon \
    --geometry ${GEOMETRY} \
    --no_exec 

#customize with values to be generated
echo "process.g4SimHits.StackingAction.SaveFirstLevelSecondary = True" >> ${WORKDIR}/${PYFILE}
m_randseed=${JOBNB}
let "m_randseed=${RANDOM} + ${m_randseed}"
#m_randseed=${JOBNB} 
echo "Random seed for this job is $m_randseed"
echo "process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(${m_randseed})" >> ${WORKDIR}/${PYFILE}
echo "process.source.firstEvent=cms.untracked.uint32($((NEVENTS*(JOBNB-1)+1)))" >> ${WORKDIR}/${PYFILE}

#use a different physics list
if [ -z ${PHYSLIST} ]; then
    echo "Changing default Geant4 physics list to $PHYSLIST"
    echo "process.g4SimHits.Physics.type=cms.string('SimG4Core/Physics/${PHYSLIST}')" >> ${WORKDIR}/${PYFILE}
fi

#substitute sub-detectors by dummy air volumes
echo "for ifile in xrange(0,len(process.XMLIdealGeometryESSource.geomXMLFiles)):" >> ${WORKDIR}/${PYFILE}
echo "    fname=process.XMLIdealGeometryESSource.geomXMLFiles[ifile]" >> ${WORKDIR}/${PYFILE}
if [[ "${EE_AIR}" != "" ]]; then
    echo "    if fname.find('hgcalEE')>0 :"  >> ${WORKDIR}/${PYFILE} 
    echo "        process.XMLIdealGeometryESSource.geomXMLFiles[ifile]='UserCode/HGCanalysis/data/air/hgcalEE.xml'" >> ${WORKDIR}/${PYFILE}
    echo "EE will be substituted by dummy air volume" 
fi
if [[ "${HEF_AIR}" != "" ]]; then
    echo "    if fname.find('hgcalHEsil')>0 :"  >> ${WORKDIR}/${PYFILE} 
    echo "        process.XMLIdealGeometryESSource.geomXMLFiles[ifile]='UserCode/HGCanalysis/data/air/hgcalHEsil.xml'" >> ${WORKDIR}/${PYFILE}
    echo "HEF will be substituted by dummy air volume" 
fi

#customize particle gun
if [[ ${CFI} =~ .*jetGun.* ]]; then
    SUBSTRING="s/MinP = cms.double(0)/MinP = cms.double(${ENERGY})/"
    SUBSTRING="${SUBSTRING};s/MaxP = cms.double(0)/MaxP = cms.double(${ENERGY})/"
else
    SUBSTRING="s/MinE = cms.double(0)/MinE = cms.double(${ENERGY})/"
    SUBSTRING="${SUBSTRING};s/MaxE = cms.double(0)/MaxE = cms.double(${ENERGY})/"
fi
SUBSTRING="${SUBSTRING};s/ParticleID = cms.vint32(0)/ParticleID = cms.vint32(${PID})/"
sed -i.bak "${SUBSTRING}" ${WORKDIR}/${PYFILE}
rm ${WORKDIR}/${PYFILE}.bak

#check if filter is required
if [[ "${TKFILTER}" != "" ]]; then
    echo "Adding hgcTrackerInteractionsFilter"
    echo "process.load('UserCode.HGCanalysis.hgcTrackerInteractionsFilter_cfi')" >> ${WORKDIR}/${PYFILE}
    echo "getattr(process,'simulation_step')._seq = getattr(process,'simulation_step')._seq * process.trackerIntFilter" >> ${WORKDIR}/${PYFILE}
fi

#
# RUN cmsRun and at the end move the output to the required directory
#
cmsRun ${WORKDIR}/${PYFILE} > ${WORKDIR}/${LOGFILE} 2>&1

if [[ $STOREDIR =~ .*/store/cmst3.* ]]; then
    cmsMkdir ${STOREDIR}
    cmsStage -f ${WORKDIR}/${OUTFILE} ${STOREDIR}/${OUTFILE}
    rm ${WORKDIR}/${OUTFILE}
elif [[ $STOREDIR =~ /afs/.* ]]; then
    cmsMkdir ${STOREDIR}
    cp -f ${WORKDIR}/${OUTFILE} ${STOREDIR}/${OUTFILE}
    rm ${WORKDIR}/${OUTFILE}
fi


echo "Generated $NEVENTS events for pid=$PID with E=$ENERGY GeV"
echo "Local output @ `hostname` stored @ ${WORKDIR}/${OUTFILE} being moved to ${STOREDIR}" 
echo "cmsRun cfg file can be found in ${WORKDIR}/${PYFILE}"
echo "log file can be found in ${WORKDIR}/${LOGFILE}"
