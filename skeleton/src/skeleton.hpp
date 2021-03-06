#ifndef DLAL_SKELETON_INCLUDED
#define DLAL_SKELETON_INCLUDED

#include "queue.hpp"

#include <dyad.h>

#include <atomic>
#include <cstdint>
#include <string>
#include <vector>
#include <functional>
#include <map>
#include <mutex>
#include <sstream>

#ifdef _MSC_VER
	#define DLAL __declspec(dllexport)
	//this is a warning that certain well-defined behavior has occurred
	//there doesn't seem to be a way to silence it in code
	#pragma warning(disable: 4250)
#else
	#define DLAL
#endif

#define DLAL_BUILD_COMPONENT_DEFINITION(COMPONENT)\
	extern "C" {\
		void* dlalBuildComponent(const char* name){\
			auto component=new dlal::COMPONENT;\
			component->_name=name;\
			return (dlal::Component*)component;\
		}\
	}

namespace dlal{

class Component;

typedef void (*TextCallback)(const char*);

//cast to Component
Component* toComponent(void*);

//to uniquely identify component
std::string componentToStr(const Component*);

//allocate c string with contents of c++ string
char* toCStr(const std::string&);

//returns true if parameter starts with "error"
bool isError(const std::string&);

//add audio to components
void add(const float* audio, unsigned size, std::vector<Component*>&);

//add audio to components that have audio
void safeAdd(const float* audio, unsigned size, std::vector<Component*>&);

//convert data to a stringstream
bool dataToStringstream(Queue<uint8_t>& data, std::stringstream& ss);

class System{
	public:
		System(int port=9088, TextCallback pythonCallback=nullptr);
		~System();
		std::string add(Component& component, unsigned slot, bool queue=false);
		std::string remove(Component& component, bool queue=false);
		std::string check();
		void evaluate();
		std::string set(unsigned sampleRate, unsigned samplesPerEvaluation);
		std::string setVariable(std::string name, std::string value);
		std::string serialize() const;
		Component* componentWithName(const char* name);

		dyad_Stream* dyadNewStream();
		void dyadAddListener(dyad_Stream*, int event, dyad_Callback, void* userData);
		int dyadListenEx(dyad_Stream*, const char* host, int port, int backlog);
		std::string dyadPauseAnd(std::function<std::string()>);
		void dyadWrite(std::string);

		std::vector<dyad_Stream*> _clients;
		std::vector<dyad_Stream*> _streams;
		Queue<std::string> _reportQueue;//for system visualization, populated in evaluation
		std::vector<std::pair<std::string, std::string>> _reportConnections;
		std::map<std::string, std::string> _variables;
		std::vector<std::vector<Component*>> _components;
		std::map<std::string, Component*> _nameToComponent;
		dyad_Stream* _server;
		Queue<uint8_t> _data;
		TextCallback _pythonHandler;

	private:
		std::vector<std::vector<Component*>> _componentsToAdd;
		std::vector<Component*> _componentsToRemove;
		std::function<dyad_Stream*()> _dyadNewStream;
		std::function<void(dyad_Stream*, int event, dyad_Callback, void* userData)> _dyadAddListener;
		std::function<int(dyad_Stream*, const char* host, int port, int backlog)> _dyadListenEx;
		std::atomic<bool>& _dyadDone;
		std::recursive_mutex& _dyadMutex;
};

class Component{
	public:
		Component();
		virtual ~Component(){}
		virtual void* derived(){ return nullptr; }
		virtual std::string type() const=0;

		//on success, return x such that isError(x) is false
		//on failure, return x such that isError(x) is true
		virtual std::string command(const std::string&);//see registerCommand
		virtual std::string join(System&);//see addJoinAction
		virtual std::string connect(Component& output){ return "error: unimplemented"; }
		virtual std::string disconnect(Component& output){ return "error: unimplemented"; }

		//evaluation - audio/midi/command processing
		virtual void evaluate(){}

		//audio/midi
		virtual void midi(const uint8_t* bytes, unsigned size){}
		virtual bool midiAccepted(){ return false; }
		virtual float* audio(){ return nullptr; }
		virtual bool hasAudio(){ return false; }

		System* _system;
		std::string _name;
		std::string _label;
	protected:
		typedef std::function<std::string(std::stringstream&)> Command;
		typedef std::function<std::string(System&)> JoinAction;
		void registerCommand(
			const std::string& name,
			const std::string& parameters,
			Command
		);
		std::string command(std::stringstream&);
		void addJoinAction(JoinAction);
	private:
		struct CommandWithParameters{
			Command command;
			std::string parameters;
		};
		std::map<std::string, CommandWithParameters> _commands;
		std::vector<JoinAction> _joinActions;
};

class SamplesPerEvaluationGetter: public virtual Component{
	public:
		SamplesPerEvaluationGetter();
		virtual ~SamplesPerEvaluationGetter(){}
	protected:
		unsigned _samplesPerEvaluation;
};

class Periodic: public SamplesPerEvaluationGetter{
	public:
		Periodic();
		virtual ~Periodic(){}
	protected:
		virtual std::string resize(uint64_t period);
		virtual std::string setPhase(uint64_t phase);
		bool phase();
		uint64_t _period, _phase;
	private:
		float _last;
};

class SampleRateGetter: public virtual Component{
	public:
		SampleRateGetter();
		virtual ~SampleRateGetter(){}
	protected:
		unsigned _sampleRate;
};

class MultiOut: public virtual Component{
	public:
		MultiOut();
		virtual ~MultiOut(){}
		virtual std::string connect(Component& output);
		virtual std::string disconnect(Component& output);
		bool _checkAudio, _checkMidi;
	protected:
		std::vector<Component*> _outputs;
};

class MidiControllee: public virtual Component{
	public:
		MidiControllee();
		virtual void midi(const uint8_t* bytes, unsigned size);
		bool midiAccepted(){ return true; }
	protected:
		std::map<std::string, float*> _nameToControl;
	private:
		enum class PretendControl{
			PITCH_WHEEL=0x100,
			SENTINEL
		};
		class Range{
			public:
				Range(): _new(true) {}
				operator int(){ return _max-_min; }
				void value(int v);
				int _min, _max;
			private:
				bool _new;
		};
		struct Control{
			Control(): _control(NULL) { _f.push_back(0.0f); _f.push_back(1.0f); }
			int _min, _max;
			std::vector<float> _f;
			float* _control;
		};
		float* _listening;
		std::map<int, Range> _listeningControls;
		std::vector<Control> _controls;
};

class Dummy: public SamplesPerEvaluationGetter{
	public:
		Dummy(){ addJoinAction([this](System&){ _audio.resize(_samplesPerEvaluation, .101f); return ""; }); }
		std::string type() const { return "dummy"; }
		float* audio(){ return _audio.data(); }
		bool hasAudio(){ return true; }
		std::vector<float> _audio;
};

}//namespace dlal

#endif//#ifndef DLAL_SKELETON_INCLUDED
