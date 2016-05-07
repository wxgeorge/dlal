#buffer repeat-sound and pitch-sound, multiply two signals

import dlal

pitcher=dlal.Buffer()
buffer=dlal.Buffer()
lfo=dlal.Buffer()
multiplier=dlal.Component('multiplier')
lfo.connect(buffer)
multiplier.connect(buffer)
system=dlal.SimpleSystem(
	[pitcher, buffer, lfo, multiplier],
	midi_receivers=[],
	outputs=[pitcher, multiplier],
	test=True,
	test_duration=1000
)
pitcher.lfo(int(system.sample_rate/8.1757989156))
pitcher.pitch_sound('y')
pitcher.midi(0x90, 60, 0x40)
buffer.clear_on_evaluate('y')
lfo.lfo(system.sample_rate//30)
lfo.midi(0x90, 0, 0x40)
go, ports=system.standard_system_functionality()