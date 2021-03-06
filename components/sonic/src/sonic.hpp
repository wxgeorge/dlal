#ifndef DLAL_SONIC_INCLUDED
#define DLAL_SONIC_INCLUDED

#include <skeleton.hpp>

namespace dlal{

class Sonic:
	public MultiOut, public SamplesPerEvaluationGetter, public SampleRateGetter, public MidiControllee
{
	public:
		Sonic();
		std::string type() const { return "sonic"; }
		void evaluate();
		void midi(const uint8_t* bytes, unsigned size);
		bool midiAccepted(){ return true; }
	private:
		static const unsigned NOTES=128;
		static const unsigned OSCILLATORS=4;
		struct Runner{
			Runner();
			void start(bool done);
			void phase(float frequencyMultiplier);
			enum Stage{ ATTACK, DECAY, SUSTAIN, RELEASE };
			Stage _stage;
			float _phase, _step, _volume, _output;
		};
		struct Oscillator{
			Oscillator();
			bool update(Runner&, float frequencyMultiplier) const;//returns true if the runner is done
			float _attack, _decay, _sustain, _release;
			float _frequencyMultiplier, _inputs[OSCILLATORS];
			float _output;
		};
		struct Note{
			Note();
			void set(unsigned i, unsigned sampleRate, const Oscillator* oscillators);
			void start(float volume, const Oscillator* oscillators);
			void stop();
			float update(//returns output
				unsigned runner,
				const Oscillator* oscillators,
				float frequencyMultiplier
			);
			Runner _runners[OSCILLATORS];
			float _volume, _desiredVolume;
			bool _done;
		};
		void update();
		Oscillator _oscillators[OSCILLATORS];
		Note _notes[NOTES];
		float _frequencyMultiplier;
};

}//namespace dlal

#endif
