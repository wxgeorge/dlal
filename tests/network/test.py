#network

import dlal, os, subprocess

#create
system=dlal.System()
raw=dlal.Component('raw')
qweboard=dlal.Qweboard()
midi=dlal.Component('midi')
sonic=dlal.Sonic()
#command
raw.set(44100, 6)
#add
system.add(raw, slot=1)
system.add(qweboard, midi, sonic)
#connect
qweboard.connect(midi)
midi.connect(sonic)
sonic.connect(raw)
#network client
os.environ['PATH']='.'
subprocess.check_call('Softboard 127.0.0.1 9120 "z 1"', shell=True)
#start
raw.start()
