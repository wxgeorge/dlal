import ctypes, platform, atexit

_port=9088
_systems=0

def set_port(port):
	assert(_systems==0)
	global _port
	_port=port

def load(name):
	def upperfirst(s): return s[0].upper()+s[1:]
	if platform.system()!='Windows': name='lib'+upperfirst(name)+'.so'
	return ctypes.CDLL(name)

def report(text):
	t=text.decode('utf-8')
	if t.startswith('error'): raise RuntimeError(t)
	return t

def connect(*args):
	if len(args)<=1: return
	result=''
	for i in range(len(args)-1):
		result+=args[i].connect(args[i+1])
		if len(result): result+='\n'
	return result

_skeleton=load('skeleton')
_skeleton.dlalDemolishComponent.argtypes=[ctypes.c_void_p]
_skeleton.dlalDyadInit.argtypes=[ctypes.c_int]
_skeleton.dlalBuildSystem.restype=ctypes.c_void_p
_skeleton.dlalDemolishSystem.restype=ctypes.c_char_p
_skeleton.dlalDemolishSystem.argtypes=[ctypes.c_void_p]
_skeleton.dlalCommand.restype=ctypes.c_char_p
_skeleton.dlalCommand.argtypes=[ctypes.c_void_p, ctypes.c_char_p]
_skeleton.dlalAdd.restype=ctypes.c_char_p
_skeleton.dlalAdd.argtypes=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
_skeleton.dlalConnect.restype=ctypes.c_char_p
_skeleton.dlalConnect.argtypes=[ctypes.c_void_p, ctypes.c_void_p]

class System:
	def __init__(self):
		global _systems
		if _systems==0: _skeleton.dlalDyadInit(_port)
		_systems+=1
		self.system=_skeleton.dlalBuildSystem()
		assert(self.system)

	def __del__(self):
		report(_skeleton.dlalDemolishSystem(self.system))
		global _systems
		_systems-=1
		if _systems==0: _skeleton.dlalDyadShutdown()

	def add(self, *args, **kwargs):
		slot=kwargs.get('slot', 0)
		result=''
		for arg in args:
			for c in arg.components_to_add:
				result+=report(_skeleton.dlalAdd(self.system, c.component, slot))
			if len(result): result+='\n';
		return result

class Component:
	_libraries={}

	def __init__(self, component):
		if component not in Component._libraries:
			Component._libraries[component]=load(component)
			Component._libraries[component].dlalBuildComponent.restype=ctypes.c_void_p
		self.library=Component._libraries[component]
		self.component=Component._libraries[component].dlalBuildComponent()
		self.components_to_add=[self]

	def __del__(self): _skeleton.dlalDemolishComponent(self.component)

	def __getattr__(self, name):
		return lambda *args: self.command(
			name+' '+' '.join([str(arg) for arg in args])
		)

	def command(self, command):
		command=str.encode(command, 'utf-8')
		return report(_skeleton.dlalCommand(self.component, command))

	def connect(self, output):
		return report(_skeleton.dlalConnect(self.component, output.component))

class Pipe:
	def __init__(self, *args):
		self.component=args[0]
		self.components_to_add=[x for arg in args for x in arg.components_to_add]

	def __getitem__(self, i): return self.components_to_add[i]

	def connect(self, output): return self.components_to_add[-1].connect(output)
