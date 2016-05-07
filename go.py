#!/usr/bin/python

import os, platform, subprocess, sys

#args
import argparse
parser=argparse.ArgumentParser(description='interface for developer operations')
parser.add_argument('--setup', action='store_true', help='install dependencies')
parser.add_argument('--test', '-t', help='run tests specified by glob')
parser.add_argument('--system', '-s', help='which system to run')
parser.add_argument('--interface', '-i', action='append', help='interface:port')
parser.add_argument('--run-only', '-r', action='store_true', help='skip build, just run')
parser.add_argument('--debug', '-d', action='store_true', help='use debug configuration')
parser.add_argument('--can', '-c', help='canned commands -- name.options -- use h for help')
args=parser.parse_args()

#canned commands
if args.can:
	canned_commands={
		'b': '-s soundboard -i softboard:9120',
		'f': '-s fm         -i softboard:9120',
		's': '-s soundfont  -i softboard:9120',
		'v': '-s vst        -i softboard:9120',
		'l': '-s looper     -i softboard:9120 -i viewer:9088',
	}
	canned_options={
		'r': '-r',
		'd': '-d',
	}
	import pprint
	if args.can=='h':
		print('usage: `can.options`')
		print('available cans:')
		pprint.pprint(canned_commands)
		print('available options:')
		pprint.pprint(canned_options)
		sys.exit(0)
	can=args.can.split('.')
	name=can[0]
	options=can[1] if len(can)>1 else ''
	if name not in canned_commands:
		print('invalid command -- valid commands are')
		pprint.pprint(canned_commands)
		sys.exit(-1)
	command=canned_commands[name]
	for i in options:
		if i not in canned_options:
			print('invalid option "{0}" -- valid options are'.format(i))
			pprint.pprint(canned_options)
			continue
		command+=' '+canned_options[i]
	args=parser.parse_args(command.split())

#helpers
def shell(*args): p=subprocess.check_call(' '.join(args), shell=True)

#current directory
file_path=os.path.split(os.path.realpath(__file__))[0]
os.chdir(file_path)
built_rel_path=os.path.join('build', 'built')

#pythonpath
if 'PYTHONPATH' in os.environ:
	os.environ['PYTHONPATH']+=os.pathsep+file_path
else:
	os.environ['PYTHONPATH']=file_path

#config
config='Release'
if args.debug: config='Debug'

#setup
if args.setup:
	if platform.system()=='Linux':
		#sfml dependencies
		shell('sudo apt-get install --yes --force-yes '
			'libxcb-image0-dev freeglut3-dev libjpeg-dev libfreetype6-dev '
			'libxrandr-dev libglew-dev libsndfile1-dev libopenal-dev libudev-dev '
		)
		#tkinter
		shell('sudo apt-get install --yes --force-yes python-tk')
		#portaudio (jack) dependencies
		shell('sudo apt-get install --yes --force-yes libjack-dev jackd')
		#rtmidi dependencies
		shell('sudo apt-get install --yes --force-yes libasound2-dev')
		#cmake
		shell('wget http://www.cmake.org/files/v3.2/cmake-3.2.3-Linux-x86_64.sh')
		shell('chmod a+x cmake-3.2.3-Linux-x86_64.sh')
		shell('sudo ./cmake-3.2.3-Linux-x86_64.sh --skip-license --prefix=/usr/local')
	elif platform.system()=='Darwin':
		shell('brew update')
		shell('sudo brew uninstall --force cmake')
		shell('brew install cmake')
	else:
		print('unrecognized system '+platform.system())
		sys.exit(-1)
	sys.exit(0)

#build
if not args.run_only:
	if not os.path.exists(built_rel_path): os.makedirs(built_rel_path)
	os.chdir(built_rel_path)
	preamble=''
	generator=''
	shell(preamble, 'cmake', generator, '-DBUILD_SHARED_LIBS=ON', '-DCMAKE_BUILD_TYPE='+config, '..')
	shell(preamble, 'cmake --build . --config '+config+' --target install')
	shell(preamble, 'cmake --build . --config '+config+' --target post-install')
	os.chdir(file_path)

#library path
os.environ['LD_LIBRARY_PATH']=os.path.join(file_path, 'build', 'built')

#test
if args.test:
	#setup
	import glob
	tests=[os.path.realpath(x) for x in glob.glob(os.path.join('tests', args.test))]
	overall=0
	print('RUNNING TESTS')
	#loop over tests
	for test in tests:
		#run test
		os.chdir(built_rel_path)
		r=subprocess.call(['python', os.path.join(test, 'test.py')])
		os.chdir(file_path)
		#read result and expected
		def read(file_name):
			with open(file_name) as file: contents=file.read()
			return [float(x) for x in contents.split()]
		raw=read(os.path.join('build', 'built', 'raw.txt'))
		expected=read(os.path.join(test, 'expected.txt'))
		#compare result to expected
		if len(raw)!=len(expected): r=1
		else:
			for i in range(len(raw)):
				if abs(raw[i]-expected[i])>0.00001:
					r=1
		#report
		overall|=r
		print('-' if r else '+', os.path.split(test)[1])
	#finish
	if overall:
		print('TESTS HAVE FAILED!')
		sys.exit(-1)
	print('ALL TESTS SUCCEEDED')

#interfaces
if args.interface:
	def find_binary(name):
		for root, dirs, files in os.walk('.'):
			for file in files:
				import re
				if re.match(name.lower()+r'(\.exe)?$', file.lower()):
					return os.path.join(root, file)
	for i in args.interface:
		name, port=i.split(':')
		os.chdir(built_rel_path)
		invocation=find_binary(name)+' 127.0.0.1 '+port
		if platform.system()=='Windows': os.system('start '+invocation)
		else: subprocess.Popen(invocation, shell=True)
		os.chdir(file_path)

#run
os.chdir(built_rel_path)
x=['python', '-i']
if args.system: x+=[os.path.join('..', '..', 'systems', args.system+'.py'), '-g']
if not args.test: shell(*x)
os.chdir(file_path)

#done
print('all requests processed; call with -h for help')
