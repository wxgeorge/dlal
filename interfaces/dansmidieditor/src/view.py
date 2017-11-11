import os, sys
from fractions import Fraction
home=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(home, '..', '..', '..', 'deps', 'midi'))
import midi

class View:
	def __init__(self, margin=6, text_size=12):
		self.midi=[[], []]
		self.ticks_per_quarter=256
		self.text=''
		self.margin=margin
		self.text_size=text_size
		self.staff=0
		self.staves=4.0
		self.multistaffing=1
		self.ticks=0
		self.duration=5760
		self.cursor_staff=0
		self.cursor_note=60
		self.cursor_ticks=Fraction(0)
		self.cursor_duration=Fraction(self.ticks_per_quarter)
		self.cursor_duty=Fraction(1)
		self.selected=set()
		self.unwritten=False
		#colors
		self.color_background=[  0,   0,   0]
		self.color_staves    =[  0,  32,   0, 128]
		self.color_c_line    =[ 16,  16,  16, 128]
		self.color_quarter   =[  8,   8,   8]
		self.color_octaves   =[  0, 128,   0]
		self.color_notes     =[  0, 128, 128]
		self.color_cursor    =[128,   0, 128, 128]
		self.color_selected  =[255, 255, 255]
		self.color_warning   =[255,   0,   0]

	def read(self, path):
		self.midi=midi.read(path)
		if len(self.midi)==1: self.midi.append([])
		self.ticks_per_quarter=midi.ticks_per_quarter(self.midi)
		self.cursor_duration=Fraction(self.ticks_per_quarter)
		self.cursor_down(0)
		self.unwritten=False
		self.path=path

	def write(self, path=None):
		if not path: path=self.path
		midi.write(path, self.midi)
		self.unwritten=False

	def cursor_down(self, amount):
		self.cursor_staff+=amount
		self.cursor_staff=max(self.cursor_staff, 0)
		self.cursor_staff=min(self.cursor_staff, len(self.midi)-2)
		#move up if cursor is above window
		self.staff=min(self.staff, self.cursor_staff)
		#move down if cursor is below window
		bottom=self.staff+int(self.staves)-1
		if self.cursor_staff>bottom: self.staff+=self.cursor_staff-bottom
		#figure cursor octave
		self.cursor_note%=12
		self.cursor_note+=self.calculate_octave(self.cursor_staff)*12

	def cursor_up(self, amount): self.cursor_down(-amount)

	def cursor_right(self, amount):
		self.cursor_ticks+=self.cursor_duration*amount
		self.cursor_ticks=max(Fraction(0), self.cursor_ticks)
		#move left if cursor is left of window
		self.ticks=min(self.ticks, int(self.cursor_ticks))
		#move right if cursor is right of window
		right=self.ticks+self.duration
		cursor_right=self.cursor_ticks+self.cursor_duration
		if cursor_right>right: self.ticks+=int(cursor_right)-right
		#figure cursor octave
		self.cursor_note%=12
		self.cursor_note+=self.calculate_octave(self.cursor_staff)*12

	def cursor_left(self, amount): self.cursor_right(-amount)

	def cursor_note_down(self, amount):
		self.cursor_note-=amount
		self.cursor_note=max(0, self.cursor_note)
		self.cursor_note=min(127, self.cursor_note)

	def cursor_note_up(self, amount): self.cursor_note_down(-amount)

	def set_duration(self, fraction_of_quarter):
		self.cursor_duration=Fraction(self.ticks_per_quarter)*fraction_of_quarter

	def more_multistaffing(self, amount):
		self.multistaffing+=amount
		self.multistaffing=max(1, self.multistaffing)
		self.multistaffing=min(6, self.multistaffing)

	def less_multistaffing(self, amount): self.more_multistaffing(-amount)

	def add_note(self, number, advance=True):
		octave=self.calculate_octave(self.cursor_staff)
		midi.add_note(
			self.midi,
			self.cursor_staff+1,
			int(self.cursor_ticks),
			int(self.cursor_duration*self.cursor_duty),
			number+12*octave
		)
		if advance: self.skip_note()
		self.unwritten=True

	def skip_note(self):
		self.cursor_ticks+=self.cursor_duration

	def select(self):
		args=[
			self.midi,
			self.cursor_staff+1,
			self.cursor_ticks,
			self.cursor_duration,
		]
		notes=midi.notes_in(*args, number=self.cursor_note)
		if not notes: notes=midi.notes_in(*args, number=self.cursor_note, generous=True)
		if not notes: notes=midi.notes_in(*args)
		if not notes: notes=midi.notes_in(*args, generous=True)
		for i in notes: self.selected.add(i)

	def deselect(self): self.selected=set()

	def is_selected(self, note):
		return any([self.midi[i[0]][i[1]]==note for i in self.selected])

	def delete(self):
		midi.delete(self.midi, self.selected)
		self.selected=set()
		self.unwritten=True

	def transpose(self, amount):
		midi.transpose(self.midi, self.selected, amount)
		self.unwritten=True

	def staves_to_draw(self):
		return range(self.staff, self.staff+min(int(self.staves)+1, len(self.midi)-1-self.staff))

	def notes_per_staff(self):
		return 24*self.multistaffing

	def h_note(self):
		return self.h_window//self.staves//self.notes_per_staff()

	def y_note(self, staff, note, octave=0):
		y_staff=(staff+1-self.staff)*self.h_window//self.staves
		return int(y_staff-(note+1-12*octave)*self.h_note())

	def x_ticks(self, ticks):
		return (ticks-self.ticks)*self.w_window//self.duration

	def endures(self, ticks):
		return ticks<self.ticks+self.duration

	def calculate_octave(self, staff):
		octave=5
		lo=60
		hi=60
		for i in self.midi[1+staff]:
			if i.type!='note': continue
			if i.ticks+i.duration<self.ticks: continue
			if not self.endures(i.ticks): break
			lo=min(lo, i.number)
			hi=max(hi, i.number)
		top=(octave+2)*12
		if hi>top: octave+=(hi-top+11)//12
		bottom=octave*12
		if lo<bottom: octave+=(lo-bottom)//12
		return octave

	def notate_octave(self, octave):
		octave-=5
		if octave>= 1: return '{}va'.format(1+7*octave)
		if octave<=-1: return '{}vb'.format(1-7*octave)
		return '-'

	def draw(self, media):
		media.clear(color=self.color_background)
		self.w_window=media.width()
		self.h_window=media.height()
		#quarters
		tph=2*self.ticks_per_quarter
		for i in range(self.duration//tph+2):
			media.fill(
				xi=self.x_ticks((self.ticks//tph+i)*tph),
				xf=self.x_ticks((self.ticks//tph+i)*tph+self.ticks_per_quarter),
				yi=0,
				yf=self.h_window,
				color=self.color_quarter
			)
		media.draw_vertices()
		#staves
		h=int(self.h_note())
		for m in range(self.multistaffing):
			for i in self.staves_to_draw():
				media.fill(xi=0, xf=self.w_window, y=self.y_note(i, 24*m), h=h, color=self.color_c_line)
				for j in [4, 7, 11, 14, 17]:
					media.fill(xi=0, xf=self.w_window, y=self.y_note(i, j+24*m), h=h, color=self.color_staves)
		media.draw_vertices()
		#octaves
		octaves={}
		for i in self.staves_to_draw():
			octaves[i]=self.calculate_octave(i)
			media.text(
				self.notate_octave(octaves[i]),
				x=self.margin,
				y=self.y_note(i, 24*self.multistaffing-5),
				h=int(self.h_note()*2),
				color=self.color_octaves,
			)
		#notes
		for i in self.staves_to_draw():
			for j in self.midi[1+i]:
				if j.type!='note': print(j)
				if not self.endures(j.ticks): break
				kwargs={
					'xi': self.x_ticks(j.ticks),
					'xf': self.x_ticks(j.ticks+j.duration),
					'y' : self.y_note(i, j.number, octaves[i]),
				}
				media.fill(
					h=int(self.h_note()),
					color=self.color_selected if self.is_selected(j) else self.color_notes,
					**kwargs
				)
				if j.number-12*octaves[i]>24*self.multistaffing-4: media.fill(
					h=int(self.h_note()//2),
					color=self.color_warning,
					**kwargs
				)
		media.draw_vertices()
		#cursor
		media.fill(
			xi=self.x_ticks(int(self.cursor_ticks)),
			xf=self.x_ticks(int(self.cursor_ticks+self.cursor_duration)),
			y=self.y_note(self.cursor_staff, self.cursor_note, octaves[self.cursor_staff]),
			h=int(self.h_note()),
			color=self.color_cursor,
		)
		#text
		media.text(self.text, x=self.margin, y=self.h_window-self.margin, h=self.text_size, bottom=True)
		#
		media.display()