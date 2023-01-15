import sys

root_folder = '/home/joao/Documents/XPCS/'

sys.path.append(root_folder + 'GUI')
try:
	import GUI
except Exception as e:
	print(' Could not initialize graphical interface!', e)
	exit(0)
Graph_Int = GUI.GUI()
Graph_Int.InitWindow()
