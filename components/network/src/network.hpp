#ifndef DLAL_NETWORK_INCLUDED
#define DLAL_NETWORK_INCLUDED

#include <skeleton.hpp>
#include <page.hpp>

#include <map>

namespace dlal{

class Network: public MultiOut, public SamplesPerEvaluationGetter{
	public:
		Network();
		std::string type() const { return "network"; }
		void evaluate();
		void queue(const Page&);
		Queue<uint8_t> _data;
	private:
		int _port;
		Queue<Page> _queue;
		std::map<std::string, dlal::Page> _map;
};

}//namespace dlal

#endif
