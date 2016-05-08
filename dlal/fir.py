from .skeleton import *

try: import tkinter
except ImportError: import Tkinter as tkinter

class Fir(Component):
	def __init__(self):
		Component.__init__(self, 'fir')
		self.commander=Component('commander')
		self.commander.connect(self)
		self.components_to_add=[self.commander, self]

	def show_controls(self, title='dlal formant synth controls'):
		root=tkinter.Tk(title)
		root.title()
		tkinter.Label(text='frequency 1').grid(row=0, column=0)
		tkinter.Label(text='magnitude 1').grid(row=0, column=1)
		tkinter.Label(text='width 1'    ).grid(row=0, column=2)
		tkinter.Label(text='frequency 2').grid(row=0, column=3)
		tkinter.Label(text='magnitude 2').grid(row=0, column=4)
		tkinter.Label(text='width 2'    ).grid(row=0, column=5)
		f1f=tkinter.Scale(command=lambda x: self.live_command('formant 0 {} {} {} 0.5'.format(f1f.get(), f1m.get(), f1w.get())))
		f1m=tkinter.Scale(command=lambda x: self.live_command('formant 0 {} {} {} 0.5'.format(f1f.get(), f1m.get(), f1w.get())))
		f1w=tkinter.Scale(command=lambda x: self.live_command('formant 0 {} {} {} 0.5'.format(f1f.get(), f1m.get(), f1w.get())))
		f2f=tkinter.Scale(command=lambda x: self.live_command('formant 1 {} {} {} 0.5'.format(f2f.get(), f2m.get(), f2w.get())))
		f2m=tkinter.Scale(command=lambda x: self.live_command('formant 1 {} {} {} 0.5'.format(f2f.get(), f2m.get(), f2w.get())))
		f2w=tkinter.Scale(command=lambda x: self.live_command('formant 1 {} {} {} 0.5'.format(f2f.get(), f2m.get(), f2w.get())))
		f1f.config(from_=10000, to=0, length=600)
		f1m.config(from_=    1, to=0, length=600, resolution=0.001)
		f1w.config(from_=10000, to=0, length=600)
		f2f.config(from_=10000, to=0, length=600)
		f2m.config(from_=    1, to=0, length=600, resolution=0.001)
		f2w.config(from_=10000, to=0, length=600)
		f1f.grid(row=1, column=0)
		f1m.grid(row=1, column=1)
		f1w.grid(row=1, column=2)
		f2f.grid(row=1, column=3)
		f2m.grid(row=1, column=4)
		f2w.grid(row=1, column=5)

	phonetics={
		'q': 'a as in father',
		'w': 'u as in tube',
		'e': 'e as in bet',
		'y': 'ee as in eel',
		'u': 'u as in cup',
		'i': 'i as in indigo (IPA I)',
		'o': 'o as in rode',
		'a': 'a as in apple',
		'x': 'oo as in foot',
		'c': 'a as in pay',
		'r': 'r as in ray',
		'l': 'l as in lay',
		'm': 'm as in may',
		'n': 'n as in need',
		',': 'ng as in sing (IPA velar nasal)',
		's': 's as in seven',
		'z': 'z as in zebra',
		'f': 'f as in fine',
		'v': 'v as in very',
		'.': 'th as in thanks (IPA theta)',
		'/': 'th as in the (IPA voiced dental fricative)',
		';': 'sh as in she (IPS S)',
		"'": 's as in fusion (IPA 3)',
		't': 't as in time',
		'd': 'd as in dime',
		'k': 'k as in kite',
		'g': 'g as in get',
		'p': 'p as in pet',
		'b': 'b as in bet',
		'[': 'ch as in check (IPA tS)',
		'j': 'j as in jet (IPA d3)',
		'h': 'h as in hat',
	}

	stops='tdkgpb[j'

	def phonetic_voice(self, p):
		formants=2
		phonetics={
			'q': [( 750, 1.0), (1000, 0.3)],
			'w': [( 315, 1.0), ( 790, 0.3)],
			'e': [( 650, 1.0), (1550, 0.6)],
			'y': [( 350, 1.0), (2500, 0.5)],
			'u': [( 650, 1.0), (1110, 0.4)],
			'i': [( 350, 1.0), (1750, 0.4)],
			'o': [( 550, 1.0), ( 800, 0.3)],
			'a': [( 900, 1.0), (1600, 0.3)],
			'x': [( 540, 1.0), (1210, 0.6)],
			'c': [( 550, 1.0), (1900, 0.2)],
			'r': [( 390, 1.0), (1400, 0.4)],
			'l': [( 390, 1.0), ( 800, 0.3)],
			'm': [( 200, 1.0), (2000, 0.3)],
			'n': [( 230, 1.0), (2200, 0.3)],
			',': [( 230, 1.0), (2400, 0.4)],
			'z': [( 200, 1.0), (1300, 0.3)],
			'v': [( 200, 1.0), (1100, 0.3)],
			'/': [( 200, 1.0), (1300, 0.3)],
			"'": [( 200, 1.0), (1300, 0.3)],
			'd': [( 230, 1.0), (2200, 0.3)],
			'g': [( 230, 1.0), (2400, 0.4)],
			'b': [( 540, 1.0), (1210, 0.6)],
			'j': [( 230, 1.0), (2200, 0.3)],
		}
		if p not in phonetics:
			for i in range(formants):
				self.live_command('formant_mute {} 0.1'.format(i))
		else:
			p=phonetics[p]
			for i in range(len(p)):
				self.live_command('formant {} {} {} 10000 0.1'.format(i, p[i][0], p[i][1]))

	def phonetic_noise(self, p):
		formants=2
		phonetics={
			's': [( 5000, 0.500, 1e4), (10000, 0.500, 1e4)],
			'z': [( 5000, 0.250, 1e4), (10000, 0.250, 1e4)],
			'f': [(10000, 1.000, 1e4), (    0, 0.000, 1e4)],
			'v': [(10000, 1.000, 1e4), (    0, 0.000, 1e4)],
			'.': [( 7000, 1.000, 1e4), (    0, 0.000, 1e4)],
			'/': [( 7000, 1.000, 1e4), (    0, 0.000, 1e4)],
			';': [(    0, 0.300, 1e4), ( 1000, 1.000, 1e4)],
			"'": [(    0, 0.300, 1e4), ( 1000, 1.000, 1e4)],
			't': [(    0, 0.100, 1e6), ( 4000, 1.000, 1e6)],
			'd': [(    0, 0.050, 1e6), ( 4000, 0.500, 1e6)],
			'k': [(    0, 0.100, 1e6), (  480, 1.000, 1e4)],
			'g': [(    0, 0.050, 1e6), (  480, 0.500, 1e4)],
			'p': [(    0, 1.000, 1e5), (    0, 0.500, 1e7)],
			'b': [(    0, 0.500, 1e5), (    0, 0.250, 1e7)],
			'[': [( 4000, 1.000, 1e4), ( 1000, 1.000, 1e4)],
			'j': [( 4000, 0.500, 1e4), ( 1000, 0.500, 1e4)],
			'h': [(  650, 0.500, 1e4), ( 1110, 0.200, 1e4)],
		}
		if p not in phonetics:
			for i in range(formants):
				self.live_command('formant_mute {} 0.1'.format(i))
		elif p in Fir.stops:
			p=phonetics[p]
			for i in range(formants):
				self.live_command('formant {} {} {} {} 1'.format(i, p[i][0], p[i][1], p[i][2]))
				self.live_command('formant_mute {} 0.1'.format(i))
		else:
			p=phonetics[p]
			for i in range(formants):
				self.live_command('formant {} {} {} {} 1'.format(i, p[i][0], p[i][1], p[i][2]))

	def live_command(self, command):
		self.commander.command('queue 0 0 '+command)
