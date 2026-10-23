#include "anomaly_engine.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstdlib>
// usage: harness csv  -> prints per row: idx level trigger flags score
int main(int argc,char**argv){
  std::ifstream f(argv[1]); std::string line; std::getline(f,line);
  std::vector<std::string> hdr; { std::stringstream s(line); std::string c; while(std::getline(s,c,',')) hdr.push_back(c); }
  int iT=-1,iPH=-1,iEC=-1,iDO=-1,iTU=-1,iTE=-1;
  for(size_t i=0;i<hdr.size();i++){ if(hdr[i]=="timestamp")iT=i; if(hdr[i]=="ph")iPH=i; if(hdr[i]=="ec_us_cm")iEC=i; if(hdr[i]=="do_mg_l")iDO=i; if(hdr[i]=="turbidity_ntu")iTU=i; if(hdr[i]=="temp_c")iTE=i; }
  if(iT<0||iPH<0||iEC<0||iDO<0||iTU<0||iTE<0){ fprintf(stderr,"bad header\n"); return 2; }
  AnomalyEngine e; e.init(false);
  uint32_t idx=0;
  while(std::getline(f,line)){
    std::vector<std::string> c; std::stringstream s(line); std::string x; while(std::getline(s,x,',')) c.push_back(x);
    SensorReadings r; memset(&r,0,sizeof(r));
    r.ph=atof(c[iPH].c_str()); r.ec=atof(c[iEC].c_str()); r.do_val=atof(c[iDO].c_str()); r.turbidity=atof(c[iTU].c_str()); r.temperature=atof(c[iTE].c_str()); r.stage=1.0f;
    for(int i=0;i<5;i++){ r.valid[i]=true; r.health[i]=HEALTH_OK; } r.valid[5]=false; r.health[5]=HEALTH_NOT_FITTED;
    int hour=atoi(c[iT].substr(c[iT].find('T')+1,2).c_str());
    AnomalyResult a=e.evaluate(r,hour,idx);
    printf("%u %d %d %d %.4f\n",idx,(int)a.level,(int)a.autosampler_trigger,(int)a.contributing_flags,a.max_score);
    idx++;
  }
}
