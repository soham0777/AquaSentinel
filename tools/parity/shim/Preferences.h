#pragma once
#include <map>
#include <string>
#include <vector>
#include <string.h>
class Preferences {
  static std::map<std::string,std::vector<unsigned char>>& store(){ static std::map<std::string,std::vector<unsigned char>> s; return s; }
  std::string ns;
public:
  bool begin(const char* n, bool ro=false){ ns=n; return true; }
  void end(){}
  size_t putBytes(const char* k, const void* v, size_t len){ store()[ns+"/"+k]=std::vector<unsigned char>((unsigned char*)v,(unsigned char*)v+len); return len; }
  size_t getBytes(const char* k, void* v, size_t len){ auto it=store().find(ns+"/"+k); if(it==store().end()) return 0; size_t n=it->second.size()<len?it->second.size():len; memcpy(v,it->second.data(),n); return n; }
};
