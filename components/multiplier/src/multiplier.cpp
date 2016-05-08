#include "multiplier.hpp"

void* dlalBuildComponent(){ return (dlal::Component*)new dlal::Multiplier; }

namespace dlal{

Multiplier::Multiplier(): _multiplier(1.0f), _offset(0.0f) {
	_checkAudio=true;
	registerCommand("set", "multiplier", [this](std::stringstream& ss){
		ss>>_multiplier;
		return "";
	});
	registerCommand("offset", "offset", [this](std::stringstream& ss){
		ss>>_offset;
		return "";
	});
}

void Multiplier::evaluate(){
	if(_outputs.empty()) return;
	for(unsigned i=0; i<_samplesPerEvaluation; ++i)
		_outputs[0]->audio()[i]*=_multiplier;
	for(unsigned j=1; j<_outputs.size(); ++j)
		for(unsigned i=0; i<_samplesPerEvaluation; ++i)
			_outputs[j]->audio()[i]*=_outputs[j-1]->audio()[i]+_offset;
}

}//namespace dlal
