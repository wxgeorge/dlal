#ifndef DLAL_FILEI_INCLUDED
#define DLAL_FILEI_INCLUDED

#include <skeleton.hpp>
#include <page.hpp>

namespace dlal{

class Filei: public MultiOut, SamplesPerEvaluationGetter{
	public:
		Filei();
		std::string type() const { return "filei"; }
		void evaluate();
	private:
		uint64_t _evaluation;
		std::vector<Page> _loaded;
		unsigned _index;
};

}//namespace dlal

#endif
