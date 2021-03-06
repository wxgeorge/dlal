#include "network.hpp"

#include <vector>
#include <sstream>
#include <iostream>

#include <obvious.hpp>

DLAL_BUILD_COMPONENT_DEFINITION(Network)

static void onData(dyad_Event* e){
	auto& self=*(dlal::Network*)e->udata;
	self._data.write((uint8_t*)e->data, e->size);
	std::stringstream ss;
	while(dlal::dataToStringstream(self._data, ss)) self.queue(dlal::Page(ss));
}

static void onDestroyed(dyad_Event* e){
	std::cerr<<"error: server destroyed"<<std::endl;
}

static void onError(dyad_Event* e){
	std::cerr<<"error: "<<e->msg<<std::endl;
}

static void onAccept(dyad_Event* e){
	((dlal::Network*)e->udata)->_system->dyadAddListener(
		e->remote, DYAD_EVENT_DATA, onData, e->udata
	);
}

namespace dlal{

Network::Network(): _data(10), _port(9089), _queue(8) {
	addJoinAction([this](System&)->std::string{
		_system->setVariable(componentToStr(this)+".port", std::to_string(_port));
		return _system->dyadPauseAnd([this]()->std::string{
			dyad_Stream* server=_system->dyadNewStream();
			_system->dyadAddListener(server, DYAD_EVENT_ACCEPT , onAccept   , this);
			_system->dyadAddListener(server, DYAD_EVENT_ERROR  , onError    , this);
			_system->dyadAddListener(server, DYAD_EVENT_DESTROY, onDestroyed, this);
			if(_system->dyadListenEx(server, "0.0.0.0", _port, 511)<0)
				return obvstr("error: couldn't listen to port", _port);
			return "";
		});
	});
	registerCommand("port", "", [this](std::stringstream& ss)->std::string{
		ss>>_port;
		return "";
	});
	registerCommand("lockless", "", [this](std::stringstream& ss){
		return (_data.lockless()&&_queue.lockless())?"lockless":"lockfull";
	});
	registerCommand("map_midi", "<key> <midi bytes>", [this](std::stringstream& ss){
		std::string key;
		ss>>key;
		std::vector<uint8_t> midi;
		unsigned byte;
		while(ss>>byte) midi.push_back(byte);
		_map[key]=dlal::Page(midi.data(), midi.size(), 0);
		return "";
	});
	registerCommand("map_command", "<key> <command>", [this](std::stringstream& ss){
		std::string key;
		ss>>key;
		std::string command;
		ss.ignore(1);
		std::getline(ss, command);
		_map[key]=dlal::Page(command, 0);
		return "";
	});
	registerCommand("serialize_network", "", [this](std::stringstream&){
		std::stringstream ss;
		ss<<_port;
		return ss.str();
	});
	registerCommand("deserialize_network", "<serialized>", [this](std::stringstream& ss){
		ss>>_port;
		return "";
	});
}

void Network::evaluate(){
	Page page;
	if(_queue.read(page, true)){
		if(page._type==dlal::Page::TEXT&&_map.count(page._text))
			page=_map[page._text];
		page.dispatch(*this, _outputs, _samplesPerEvaluation);
	}
}

void Network::queue(const Page& page){ _queue.write(page); }

}//namespace dlal
