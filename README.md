dlal
====
dlal stands for Dan's Live Audio Lab.
The highest-level description of it is something that enables the user to explore and manipulate sound.

| Platform(s) | Status |
| --- | --- |
| OSX/Linux | [![Build Status](https://travis-ci.org/dansgithubuser/dlal.svg?branch=master)](https://travis-ci.org/dansgithubuser/dlal) |
| Windows | [![Build status](https://ci.appveyor.com/api/projects/status/tvni128gp6o02890/branch/master?svg=true)](https://ci.appveyor.com/project/dansgithubuser/dlal/branch/master) |

Try `python go.py -h` to get started.
Look over the continuous integration files to see what's supported and what you'll need to install.

design
------
dlal uses C++ for audio processing and Python for audio system description.
C++ is well-suited to the timing constraints of audio processing.
Python is easily written and customized to create your ideal audio system.

dlal is cross-platform.
The benefit of being cross-platform is that as underlying systems change,
dlal remains capable of taking whatever best suits it.

dlal is conservative in its dependencies.
C++11, Python (2 or 3), and cmake are used to build.
As much as possible, dependencies are kept in-repo and reasonable errors should pop up if a requirement isn't met.
Despite this, build scripts should be flexible enough to use out-of-repo versions of dependencies.

example uses
------------
- design a sound from scratch
- run a digital jam session
- augment a real-life instrument

features
--------
- FM synthesis modeled after the Sega Genesis YM2612 chip
- MIDI input
- mic input
- SFML input and output over a network
- looping
- record and replay sessions
- networking
- SoundFont
- VST host
- soundboarding
- filtering
- robot voices
- MIDI editor

file organization
-----------------
- build folders are build descriptions for the item represented by the parent folder.
- deps folders are 3rd party dependencies for the item represented by parent folder.
- src folders are source code for the item represented by the parent folder.

- components: C++ components that can be connected to each other to create an audio system.
- dlal: Python module that wraps skeleton.
- interfaces: Interfaces that communicate with audio systems over the network.
- skeleton: C++ library; audio system definition and abstract component definition.
- systems: Python scripts that describe some useful audio systems.
- tests: Sanity tests.

todo
----
- audio select input and output

- upgrade system viewer to editor, build like midi editor
	- remove components
	- UI remove components
	- scroll
	- load system, bootstrap system (system commands)
- audiobro
	- reverb
	- piano
	- vibrato
	- pitch slide
	- long-term commander
	- render to file
	- new ideas

- radio (load a bunch of sounds and select between them)
- bunch of simple components
	- adsr
	- sine, triangle, square, saw, noise
	- enough to make a bassline, snare, bass drum, chords, cymbal
	- look to modular synths for examples

- save and load system
	- midi controllee, all components
- investigate audio clicking (buffer underflow, right?)
- midi editor
	- quantization
	- niceties
		- controls -- regex list into regex with a bunch of |s
		- many-notes render speed
		- indicator that more notes are off-screen
		- track 0 events
		- other events
		- zoom
		- horizontal scale shouldn't change when ticks per quarter does

- vocoder
- pitch shift component
- auto dj
