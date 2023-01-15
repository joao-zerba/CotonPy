#Author: Paulo R. A. F. Garcia
#email: paulo.garcia@lnls.br / pauloricardoafg@yahoo.com.br

#Python script for the calculation of the intensity autocorrelation function g2 using a multi-tau algorithm.
#Tkinter library is used for the graphical interface development. 

#version 1: 20/01/2021
 
import h5py
import numpy as np
import os
from os.path import expanduser
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk) 
from matplotlib.colors import LogNorm
from tkinter import messagebox
from matplotlib import ticker
from PIL import Image, ImageFont


import sys

root_folder = '/home/joao/Documents/XPCS/'

Extensions = [["hdf5", "h5", "npy", "b","bin"],["npy","msk" ]]


sys.path.append(root_folder+'InOutPut')
sys.path.append(root_folder+'Math')

#---------------------- Loading the modules ----------------------------------------#
try:
	import In_OutPut
	InOutput = In_OutPut.Input_Output()
except Exception as e:
	messagebox.showerror("Error", "Message")

	print(' Could not initialize input/out module! Check In_OutPut.py  file.', e)
	exit(0)
try:
	import Math
	Math = Math.Math()
except Exception as e:
	print(' Could not initialize Math module! Check the Math.py file.', e)
	exit(0)
#------------------------------------------------------------------------------------



class GUI:
	def __init__(self):
	
		#Initializing the variables  		
		self.W_Title = 'XPCS Correlator software'
		self.W_XSize = 800
		self.w_YSize = 800
		self.Fields =  ['Wavelength ', 'Sam-to-det dist ', 'Inner ring rad ', 'Outer ring rad ', 
		'Frequency ', 'X center ', 'Y center ', 'q bins number ', 'Mask file ', 'Buffers ', 
		'File name ', 'Number of frames  ', 'Image size ' ]
		self.Values = ['' for i in self.Fields]
		self.Unities = ['px' for i in self.Fields]
		self.Unities[0] = "A"
		self.Unities[1] = "m"
		self.Unities[4] = "Hz"
		self.Unities[7] = ""
		self.Unities[8] = ""
		self.Unities[9] = ""
		self.Unities[10] = ""
		self.Unities[11] = ""
		self.Unities[12] = ""
		
		#0 Wavelength
		#1 Sam-to-det dist
		#2 Inner int radius
		#3 Outter int radius
		#4 Frequency
		#5 X center
		#6 Y center
		#7 Number of q bins
		#8 Mask file
		#9 Buffers
		#10 File name
		#11 Number of frames
		#12 Image size
		

		#-------------------------------------------------------------------------#
		self.ROI_size = 9 #rings size (px)
		self.Pixel_size = 55 #pixel size (um)
		self.Res_folder = expanduser("~")  + "/XPCS_results" #Results folder
		self.Rings_data_folder =self.Res_folder + "/Rings_data" #Rings data folder 
		#-------------------------------------------------------------------------#		
		 
	def InitWindow(self):
	
		#-----------------------------Initializing Window----------------------------------#

		self.init_pars_bool = False
		self.master = Tk()
		self.fields_number = len(self.Fields)
		self.master.title(' XPCS Correlator software')
		self.Gui_Menu = Menu(self.master)
		self.master.config(menu=self.Gui_Menu)
		File_Menu = Menu(self.Gui_Menu)
		Adv_Menu = Menu(self.Gui_Menu)
		#Menu: File
		self.Gui_Menu.add_cascade(label = 'File',font = ('',18	),menu = File_Menu)
		File_Menu.add_command(label = 'Load',font = ('',18	),command = self.LoadFile, )
		File_Menu.add_separator()
		File_Menu.add_command(label = 'Quit',font = ('',18	),command = self.master.quit)
		#Menu: Advanced
		self.Gui_Menu.add_cascade(label = 'Advanced',font = ('',18	),menu = Adv_Menu, state = 'disabled')
		Adv_Menu.add_command(label = 'Ring thickness',font = ('',16	), command = lambda: self.Par_window("Ring thickness",  str(self.ROI_size) , "Ring thickness: ",self.ROI_size, "px") )
		Adv_Menu.add_command(label = 'Pixel size',font = ('',16	),  command = lambda: self.Par_window("Pixel size",  str(self.Pixel_size), "Pixel size: ",  self.Pixel_size, "um") )		
		
		
		#Formatting the initial window
		
		self.master.columnconfigure(4, weight=2)
		self.master.rowconfigure(0, weight=1)
		self.master.rowconfigure(14, weight=3)
		self.master.rowconfigure(17, weight=1)
		
		#-------------- Setting the entry fields ------------------------------------------------------------------#
		
		self.entry = [] * (self.fields_number -3)
		FirstLabel = Label(self.master,text = "").grid(row = 0 ,column=1)
		for i in range(self.fields_number-3):
			label = Label(self.master, text = self.Fields[i], font = ('',14), anchor = 'e', width = 13)
			label.grid(row=i+1,column = 1, padx = (5,0), pady = 10)
			self.entry.append(Entry(self.master,width=10, borderwidth =5, justify='center', state = 'disabled'))
			self.entry[i].configure(disabledbackground = 'white', disabledforeground = 'black', font=('','14'))
			self.entry[i].insert(0,self.Values[i])
			self.entry[i].grid(row=i+1,column = 2, pady = 5)
			labelb = Label(self.master, text = self.Unities[i], font = ('',14))
			labelb.grid(row=i+1,column = 3, padx = (0,10), pady = 5)
		
		
		# Binding ENTER key event to update the scattering image  
		self.entry[2].bind('<Return>',  self.Update_scattering_Img)
		self.entry[3].bind('<Return>',  self.Update_scattering_Img)
		self.entry[5].bind('<Return>',  self.Update_scattering_Img)
		self.entry[6].bind('<Return>',  self.Update_scattering_Img)
		self.entry[7].bind('<Return>',  self.Update_scattering_Img)
		self.entry[8].bind('<Return>',  self.Update_scattering_Img)
		
		#------------- Setting the white text area -------------------------------------------------------------#
		
		self.area =  scrolledtext.ScrolledText(self.master, background="white", font = ('', 14))
		self.area.grid(row=1, column=4, rowspan=14, padx=(0,5), pady = 5, sticky=E+W+S+N)
		last_column_label = Label(self.master, text = "", width =60, height = 30)
		last_column_label.grid(row=1, column=5, rowspan=14)
		
		#-------------------- Progress bar ----------------------------------------------------------------------#
		
		self.style = ttk.Style(self.master)
		self.style.layout('text.Horizontal.TProgressbar', [('Horizontal.Progressbar.trough',
		 {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'}),  
		 ('Horizontal.Progressbar.label', {'sticky': ''})])
              
		self.style.configure('text.Horizontal.TProgressbar', text='0 %')
		self.PBar = ttk.Progressbar(self.master, orient = HORIZONTAL, length = 400,mode = 'determinate')
		self.PBar.place(relx = 0.246, rely = 0.935, relwidth = 0.385, relheight = 0.03)

		
		#-------------------- Building the fields containing the information about the loaded file --------------#

		MiddleLabel = Label(self.master,text = "").grid(row = i+2 ,column=1)
		FileFrame = LabelFrame(self.master,  pady = 2) 
		FileFrame.grid(row=i+3,column = 1,columnspan = 3, rowspan = 3)

		self.LabelFrameEnt = [] * 3
		
		
		for f in range(0,3):	
			LabelFr = Label(FileFrame, text = self.Fields[i+f+1], font = ('',14)).grid(row=i+f +4,column = 1, pady = 1)
			if f ==0:

			
				self.LabelFrameEnt.append(Entry(FileFrame, text = self.Values[i+f+1],bg = 'white', justify='center',
				width = 15, borderwidth=2, relief="groove", state = 'disabled'))

				self.LabelFrameEnt[f].configure(disabledbackground = 'white', disabledforeground = 'black',font = ('',14) )
			else:
				self.LabelFrameEnt.append(Label(FileFrame, text = self.Values[i+f+1],bg = 'white', justify='center',
				width = 15, borderwidth=2, relief="groove", font = ('',14)))
			self.LabelFrameEnt[f].grid(row=i+f+4,column = 2, pady = 1, padx = (0,5))
			
			
		labelV = Label(self.master, text = '').grid(row=17, column = 1)
		

		Graph_parent = ttk.Notebook(self.master, width = 650, height = 800)
		
		style = ttk.Style()
		style.configure('TNotebook.Tab', font=('','14'), padding=[10, 10])
	
		#------------------ Building the Frame containing the scattering image and the integrated intensity graph -------------#
		
		
		self.Graph1_Frame = Frame(Graph_parent, borderwidth="2", relief=GROOVE)
		self.Graph1_Frame.place(relx=0, rely=0.2, relwidth = 0.7, relheight =0.7)
		
		Graph1_label = Label(self.Graph1_Frame , text = 'Frame:', font = ('',16	)).place(relx =0.24, rely = 0.05, width = 90, height = 30)
		
		self.Int_int_Frame = Frame(Graph_parent, borderwidth="2", relief=GROOVE, width = 100, height = 230)
		self.Int_int_Frame.place(relx=0, rely=0.3, width = 100, height =230)
		
		self.Frame_Entry  = Entry(self.Graph1_Frame, justify='center',width = 5, borderwidth="2", relief=GROOVE, font = ('',14))
		self.Frame_Entry.place(relx =0.4, rely = 0.05, width = 65, height = 35)
		
		self.Frame_Entry.bind('<Return>',  self.Update_scattering_Img)
		
		Graph_parent.grid(row =1,rowspan =14, column= 5)
		Graph_parent.add(self.Graph1_Frame, text = "Scattering Images")
		Graph_parent.add(self.Int_int_Frame, text = "Int intensity")
		
		#--------------------------- Button stuff-------------------------------------------------------------------------#
		
		mask_button_img =  PhotoImage(file = root_folder + 'GUI/Pictures/Imagem6.png')
		self.mask_button = Button(self.master,image =mask_button_img,command = self.Load_mask_file )
		self.mask_button.grid(row=9,column = 3, padx = (10,10), pady = 0)
		
		self.button1 = Button(self.master,text = "Correlate!",font = ('URW Gothic L','16','bold'), command = self.Pre_correlation, 
		fg = 'lavender', bg =  'brown4', state = DISABLED, height = 2, width = 8)
		self.button1.grid(row=18,column = 1,columnspan = 2, padx = (15,0), pady = (0,15))
		#----------------------------------------------------------------------------------------------------------------------------------#
		
		#Initializing the integrated intensity graph window
		self. Init_Int_Graph()
		#Rendering loop
		self.master.mainloop()
	
	def Write(self, message, sameline):
	
		# Function to write the messages in the white text area
		self.area.configure(state ='normal')
		self.area.mark_set(INSERT, END)
		
		if not sameline: 
			self.area.insert(INSERT,"\n" +  message)
		else:
			self.area.insert(INSERT, message)
			
		self.area.configure(state ='disabled')
		self.Update_window()
		
	def Update_scattering_Img(self, event):
	
		#To update the scattering image window
		FrameI = int(self.Frame_Entry.get())
		if FrameI >= self.Hdf_sizes[0]:
			FrameI = self.Hdf_sizes[0] -1
			self.Frame_Entry.delete(0,'end')
			self.Frame_Entry.insert(0,FrameI)
		if FrameI < 0:
			FrameI = 0
			self.Frame_Entry.delete(0,'end')
			self.Frame_Entry.insert(0,FrameI)
		
		self.Get_Entry_Values()
		self.Frame_image(FrameI, 'False')
		
	def Get_Entry_Values(self):
	
		#To get the values of the variables in the entry fields
		for i in range(len(self.entry)):
			self.Values[i] = self.entry[i].get()
		for i in range(8):
			self.Values[i] = float(self.Values[i])
		self.Values[9] = int(self.Values[9])
		self.Values[7] = int(self.Values[7])
		if self.Values[8] != '':
			self.mask_Arr = InOutput.Load_Mask(self.Values[8])
		else:
			self.mask_Arr = np.nan

		
		
	def Clear_Entry(self):
		#Clear the fields for new values
		for en in self.entry:
			en.delete(0,'end')
		self.LabelFrameEnt[0].delete(0,'end')
		self.Frame_Entry.delete(0,'end')
		
	def LoadFile(self):
	
		# Load the scattering image file, load the variables and update the window
		from tkinter import filedialog
		
		#building the extensions string
		ext_str = ""
		for exs in Extensions[0]:
			ext_str+= "*." +  exs +" "
		
		self.Input_name = filedialog.askopenfilename(initialdir = ".",title = 'Select a file', 
		filetypes=(("", ext_str),("all files", "*.*"))) #Load file window  
		
		if not self.Input_name:
			return

		
		self.Write("Loading images ... ", 0)

		
		try:
			#Loading the hdf file
			self.file_path, self.Values[10] = os.path.split(self.Input_name)
			self.Name, self.Ext = os.path.splitext(self.Values[10])
			self.Hdf_sizes = ""
			if self.Ext == ".hdf5" or self.Ext == ".h5": 
				self.Int_data = InOutput.Load_Hdf(self.Input_name)
				self.Write("Hdf File: " + self.Values[10] , 0)
				self.Hdf_sizes= InOutput.HdfInfo(self.Input_name) #Hdf file dimensions
				self.Values[11] = self.Hdf_sizes[0] 
			if self.Ext == ".b" or self.Ext == ".bin":
				self.Bin_shape_window()
				self.Write("Binary File: " + self.Values[10] , 0)
			try:
				self.Values[11] = self.Hdf_sizes[0] 
				self.Write("\nFile: " + self.file_path + "/"+ self.Values[10] + " loaded!", 0)
			except:
				return
			
		except Exception as e:
			messagebox.showerror("Error",str(e))
			return
		
		

			
		if self.init_pars_bool == False:
		
			#Loading initial set of parameters
			try:
				self.Clear_Entry()
				Pars = InOutput.Init_Parameters() 
				NPars = self.fields_number -3
				self.Values[0:NPars] = Pars[0:NPars]
				self.init_pars_bool = True
			except Exception as e:
				messagebox.showerror("Error message", 'Could not load parameters from InitPars.py. ' +str(e))
				return
		fname = str(self.Values[10]) 
	
		#------------------- Displaying the information about the hdf file --------------------------------------------#
		self.LabelFrameEnt[0].config(state = 'normal')
		self.LabelFrameEnt[0].insert(0,self.Values[10])
		
		
		SizeStr = str(str(self.Hdf_sizes[1]) + "X" + str(self.Hdf_sizes[2]))
		self.Values[12] = SizeStr 
		self.LabelFrameEnt[1].config(text = str(self.Hdf_sizes[0]), justify = 'left')
		
		self.LabelFrameEnt[2].config(text = SizeStr)

		try:
			for i in range(NPars): 
				self.entry[i].config(state = 'normal')
				self.entry[i].insert(0,self.Values[i])
		except:
			pass
		#--------------------------------------------------------------------------------------------------------------#
		

	
		self.Write("Loading parameters ... " , 0)
	
		#---------------------------------- Getting the initial set of parameters -------------------------------------#
		try:
			self.Get_Entry_Values()
		except Exception as e:
			messagebox.showerror("Error message", 'There is something wrong with the inital set of parameters. ' +str(e))
			return
		
		self.Write("Done!", 1)
		self.Write("Plotting the scattering images ... ",0)
		
		self.Frame_Entry.insert(0,0)
		self.Frame_image(0, 'True')
		
		self.Write("Done!", 1)
	
		self.button1['state'] = NORMAL
		self.Gui_Menu.entryconfig('Advanced', state = 'normal')
		self.Int_plot_window()
		
	def Load_mask_file(self):
	
		#Load mask window
		from tkinter import filedialog
		import ntpath
		ext_str = ''	
		for exs in Extensions[1]:
			ext_str+= "*." +  exs +" "
		self.Values[8] = filedialog.askopenfilename(initialdir = ".",title = 'Select the mask file',
		 filetypes=(("", ext_str),("all files", "*.*"))) 
		
		self.entry[8].delete(0,'end')
		self.entry[8].insert(0,self.Values[8])
		self.Update_scattering_Img(0)
		
	def Par_window(self, wtitle, current, parname, par, unit):
		#Build the the advanced options window
		par_window = Toplevel()
		#par_window.geometry("400x200")
		par_window.title(wtitle)
		unit = " " + unit
		opt = 0
		par_window.grid_rowconfigure(0, weight=1)
		par_window.grid_columnconfigure(0, weight=1)
		Label(par_window, text = "     ",  anchor = 'w',  justify = LEFT).grid(row=0,column = 0, sticky = W)
		current_label = Label(par_window, text = parname +   " " + current  + unit, font = ('',14),   anchor = 'w')
		current_label.grid(row=1,column = 1, columnspan = 3)
		Label(par_window, text = "New:",  font = ('',14), justify = LEFT, anchor = 'w').grid(row=2,column=1, sticky = W)
		entry = Entry(par_window, justify='center',width =10)
		entry.grid(row=2,column =2, sticky = W)
		Label(par_window, text = unit,   font = ('',14)).grid(row=2,column = 3, sticky = W)
		Label(par_window, text = '').grid(row=3,column = 1)
		OK_button = Button(par_window,text ="OK" , command = lambda eny = entry, labl = current_label, parn = parname:   self.Get_par_value(eny, current_label,parn, unit ), fg = 'black', bg = 'white')
		OK_button.grid(row =4, column= 1, columnspan =2, padx = (0,50))
		
		cancel_button = Button(par_window,text ="Cancel", command = lambda w_obj = par_window: self.Cancel_parW(w_obj),fg = 'white', bg = 'black' )
		cancel_button.grid(row =4, column= 2, columnspan =2, padx= (0,30), sticky = E)
		
		Label(par_window, text = "     ", justify='right').grid(row=5,column = 4, sticky = E)
	def Get_par_value(self,ent, lbl, parname, unit ):
		if parname == "Ring thickness: ":
			self.ROI_size = float(ent.get())
			self.Write("Ring thickness set to " +  str(self.ROI_size) + unit, 0)
			lbl.config(text= parname +   str(ent.get()) + unit)
			self.Update_scattering_Img("")
		if parname == "Pixel size: ":
			self.Pixel_size = float(ent.get())
			self.Write("Pixel size set to "+ str(self.Pixel_size) +  unit,0)
			lbl.config(text= parname +   str(ent.get()) + unit)
	def Cancel_parW(self, par_window):
		par_window.destroy()
			
	def Bin_shape_window(self):
	
		#Load bin file window
		shape_window = Toplevel()

		#shape_window.geometry("700x300")
		shape_window.title('binary file shape')
		
		#declaring the labels
		Label(shape_window, text = "", font = ('',14), justify = 'center').grid(row=1,column = 0)
		Label(shape_window, text = "Image dimensions", font = ('',14), justify = 'center').grid(row=0,column = 2,columnspan =3,  pady = 1)
		Label(shape_window, text ="").grid(rowspan =3,column= 0,)
		
		#declaring the entries
		entry_a = Entry(shape_window, justify='center',width = 11)
		entry_b = Entry(shape_window, justify='center',width = 11)
		entry_c = Entry(shape_window, justify='center',width = 11)
		
		#positioning the widgets
		entry_a.grid(row =4,column =1, sticky = 'e')
		Label(shape_window, text ="X").grid(row =4,column= 2)
		entry_b.grid(row =4,column =3, sticky = 'e')
		Label(shape_window, text ="X").grid(row =4,column= 4)
		entry_c.grid(row =4,column =5)
		Label(shape_window, text ="").grid(row =4,column= 6)
		
		
		Label(shape_window, text ="").grid(rowspan =3,column= 4, padx = 2)
		
		Label(shape_window, text ="N of images").grid(row =3,column= 1)
		Label(shape_window, text ="Y dim").grid(row =3,column= 3)
		Label(shape_window, text ="X dim").grid(row =3,column= 5)
		
		Label(shape_window, text ="  ",  font = ('',18)).grid(row =7,column= 0)
		Label(shape_window, text ="  ",  font = ('',18)).grid(row =5,column= 0)
		
		data_type_list = ('float_', 'float16', 'float32', 'float64', 'int_', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64')
		
		#building the expand button showing the dtypes
		expand_button = ttk.Menubutton(shape_window, text= data_type_list[2])
		Label(shape_window, text = "data type:").grid(row = 7, column =1)
		expand_button.grid(row =7,rowspan = 3, column= 2)
		

        	# create a new menu instance
		menu = tk.Menu(expand_button, tearoff=0)
		
		self.selected_type = tk.StringVar()
			
		self.b_data_type = data_type_list[2]
		
		#menu button
		for dtype in data_type_list:
			menu.add_radiobutton(label=dtype,value=dtype, variable=self.selected_type, command = lambda button = expand_button : self.Define_dtype(button))
		
        	# associate menu with the Menubutton
		expand_button["menu"] = menu

		#building OK button
		OK_button = Button(shape_window,text ="OK",command =  lambda:  self.Read_binary(entry_a.get(), entry_b.get(),entry_c.get(),self.b_data_type, shape_window) )
		OK_button.grid(row =6,rowspan = 3, column= 5, padx= 20)
		self.Update_window()
		OK_button.wait_window(OK_button)
	
	def Define_dtype(self, bbutton):
	
		#function to update the dtype displayed by the expand button 
		#and to save the chosen dtype
		self.b_data_type = self.selected_type.get()
		bbutton.config(text = self.b_data_type )
		
	def Read_binary(self, Nimg, ydim,xdim,data_type,  shape_window):
	
		#It reads the file in binary format
		try:
			self.Hdf_sizes = [int(Nimg),int(ydim), int(xdim) ]
			self.Int_data = InOutput.Load_binary(self.Input_name,self.Hdf_sizes[0] ,self.Hdf_sizes[1] ,self.Hdf_sizes[2] , data_type)
			shape_window.destroy()
		except Exception as e:
			messagebox.showerror("Error message", 'Could not load the binary file. Please check the file parameters. ' +str(e))
			
	def Init_Int_Graph(self):
	
		#It initializes the integrated intensity graph displayed in the "Int Intensity" tab 
		self.figI, self.axI = plt.subplots()
		self.figII, self.axII = plt.subplots()
		
		self.canvasI = FigureCanvasTkAgg(self.figI, master = self.Graph1_Frame)
		NavigationToolbar2Tk(self.canvasI, self.Graph1_Frame)
		
		
		self.canvasII = FigureCanvasTkAgg(self.figII, master = self.Int_int_Frame)
		NavigationToolbar2Tk(self.canvasII, self.Int_int_Frame)
		
	def Frame_image(self, FrameI, FigBool):
		
		#For plotting the rings, the mask and the scattering image in the "Scattering images" tab
		ROIs = Math.ROI_Rings(self.Values[5], self.Values[6], self.Int_data[FrameI], self.Values[2], self.Values[3], self.ROI_size , self.Values[7])
		
		self.axI.clear()
		
		#plt.title("Frame " + str(FrameI))
		ROIs[ROIs==0] = np.nan
		if type(self.mask_Arr) is not np.ndarray:
			Mask = np.empty_like(self.Int_data[FrameI])
			Mask[:,:]=np.nan
		else:
			Mask = np.array(self.mask_Arr, dtype = 'float')
			Mask[Mask ==0] = np.nan
			
		
		self.axI.imshow(self.Int_data[FrameI], interpolation='none', norm=LogNorm(), cmap='viridis', label ='', origin = 'lower') 
		self.axI.imshow(ROIs, cmap='Paired', interpolation='nearest', alpha=.3,label = '', origin = 'lower')
		self.axI.imshow(Mask, cmap='Paired', interpolation='nearest', alpha=.75,label="Mask", origin = 'lower')
		
		
			
		self.canvasI.draw() 
		
		self.figI.tight_layout()
		self.canvasI.get_tk_widget().place(rely = 0.15, relx = 0.0, relwidth = 0.95, relheight = 0.7)
		plt.switch_backend('Agg')
		
	def Pre_correlation(self):
	
		#Checking if there is a mask defined 
		#and initializing the on-off boolean variables of the multi-tau and two-time buttons

		self.MT_OnOff_bool = False
		self.TT_OnOff_bool = False
		if type(self.mask_Arr) is not np.ndarray:
			if self.Mask_warning_window():
				self.Corr_checkbox_window()
			else:
				return
		else:
			self.Corr_checkbox_window()
	
	def Mask_warning_window(self):
	
		#Warning if the mask in empty
		return messagebox.askyesno('WARNING', 'Mask array is empty. Continue without a mask?')

	def Int_int_window(self):
		#Function to build the integrated intensity window used for excluding bad frames
		
		Std_Multiplier = 2.0
		Graph_Window = Toplevel()
		Graph_Window.title('Integrated intensity')
		
		Iint, IintFit, IinDiff, StdDiff = Math.Define_Threshold(self.Hdf_sizes[0], self.Int_data, Std_Multiplier)
		#Iint = Integrated intensity determined to each image
		#IintFit = Polynomial curve fitted to the Iint points
		#IinDiff = Iint - IintFit
		#StdDiff = Standard deviation of the IinDiff data
		
		#Building the widgets
		Thr_Label = Label(Graph_Window, text = "Multiplier: ", font = ('',14), anchor = 'e', width = 10).grid(row =2,
		column =1,padx = (60,0), pady = (0,15))

		self.Thr_Entry  = Entry(Graph_Window, justify='center',width = 5)
		self.Thr_Entry.insert(0,Std_Multiplier)
		self.Thr_Entry.bind('<Return>',  lambda Int_data = self.Int_data, Iint = Iint, IintFit = IintFit,
		IinDiff = IinDiff,StdDiff = StdDiff, Graph_Window = Graph_Window : self.Update_StdMultiplier(Int_data, 
		Iint, IintFit, IinDiff, StdDiff, Graph_Window))
		self.Thr_Entry.configure(font = ('',14))
		self.Thr_Entry.grid(row =2,column =2,pady = (0,15),padx = (30,0) )
		

		Thr_button2 = Button(Graph_Window,text = "Submit", font = ('',14),fg = 'lavender', bg =  'brown4')
		Thr_button2['command'] = lambda Int_data = self.Int_data, Iint = Iint, IintFit = IintFit, IinDiff = IinDiff, \
		 StdDiff = StdDiff, Graph_Window = Graph_Window : self.Find_bad_frames(Int_data,Iint, IintFit, IinDiff, StdDiff, Graph_Window)
		Thr_button2.grid(row=2,column = 4, padx = (100,0), pady = (0,15))
		
		self.Write("Opening the integrated intensity graph window",0)

		#And plotting the everything
		self.PlotIntInt(Iint, IintFit, IinDiff, float(self.Thr_Entry.get())*StdDiff,'True',  Graph_Window)	
		self.Thr_Entry.wait_window(self.Thr_Entry)	
		self.Update_window()
		
	def Update_StdMultiplier(self,Int_data,Iint, IintFit, IinDiff,StdDiff,Graph_Window):
	
		#Update the threshold variable and the plot
		Std_Multiplier = float(self.Thr_Entry.get())
		self.PlotIntInt(Iint, IintFit, IinDiff, Std_Multiplier*StdDiff,'False', Graph_Window)
		
	def Find_bad_frames(self,Int_data,Iint, IintFit, IinDiff, StdDiff, Graph_Window):
	
		#Function to define the frames which will not be considered in the calculations
		
		Std_Multiplier = float(self.Thr_Entry.get())
		Threshold = Std_Multiplier*StdDiff
		self.Bad_frames = []
		
		#Indexes of the unconsidered frames will be stored in the Bad_frames array
		for i in range(int(self.Hdf_sizes[0])):
			if np.abs(IinDiff[i])>Threshold:
				self.Bad_frames.append(i)
		self.Write("\nThreshold for frames selection defined!", 0)
		self.Write("Threshold (counts) = ", 0)
		self.Write(int(Threshold), 1)
		self.Write('Number of "bad" frames: ' , 0 )
		self.Write(len(self.Bad_frames), 1)
		
		#Printing the bad frames
		if self.Bad_frames:	
			self.Write("Bad frames: ",0)
			for ff in range(len(self.Bad_frames)-1):
				self.Write(self.Bad_frames[ff], 1)
				self.Write(", ", 1)
			self.Write(self.Bad_frames[len(self.Bad_frames) -1],1)
		else:
			self.Write("0",0)
			
		#To destroy the integrated intensity window
		Graph_Window.destroy()
	
	
	
	def Corr_checkbox_window(self):
			
		#Function to build the checkbox window which appears before the correlation calculations starts
		
		#Window dimensions
		W_width = 700
		W_hight = 400
		
		MT_Opt = IntVar()
		TT_Opt = IntVar()
		Thrs_Opt = IntVar()
		MTGrap_Opt = IntVar()
		TTGrap_Opt = IntVar()
		
		Thrs_Opt.set(1)
		MTGrap_Opt.set(1)
		TTGrap_Opt.set(1)
		
		Corr_Window = Toplevel()
		Corr_Window.resizable(0,0)
		Corr_Window.geometry(str(W_width) + 'x' +str(W_hight))
		
		
		Corr_Window.title('Correlation setup panel')
		
		# Declaring the widgets
		MTLabel = LabelFrame(Corr_Window,text = "Multi tau", font = ('', 14), width=W_width/2.2, height=W_hight/1.3,labelanchor = 'n') 
		MTLabel.grid(row = 0 ,column = 0, rowspan = 4,padx = (30,0), pady = (10,0))
		
		
		TTLabel = LabelFrame(Corr_Window, text = 'Two time', font = ('', 14), width=W_width/2.2, height=W_hight/1.3, labelanchor = 'n')
		TTLabel.grid(row = 0 ,column = 1, rowspan = 4, pady = (10,0))
		
		
		#ck1 = Checkbutton(Corr_Window, text='Multi-time',variable=MT_Opt, onvalue=1, offvalue=0, anchor ='w',   command = lambda : self.Enable_MT(ck2,ck3, MT_Opt.get()))
		
		
		
		ck2 = Checkbutton(Corr_Window, text='Set threshold', font = ('', 14),variable=Thrs_Opt, onvalue=1, offvalue=0, anchor = 'w', state = DISABLED)
		
		ck2.grid(row =2,column =0)
	
		ck3 = Checkbutton(Corr_Window, text='Generate MT graphs',font = ('', 14),variable=MTGrap_Opt, onvalue=1, offvalue=0, anchor = 'w', state = DISABLED)
		ck3.grid(row =3,column =0)
		
		ck4 = Checkbutton(Corr_Window, text='Generate TT graphs',font = ('', 14),variable=TTGrap_Opt, onvalue=1, offvalue=0, anchor ='w', state = DISABLED)
		ck4.grid(row =2,column =1)
		
		ON = PhotoImage(file = root_folder+ 'GUI/Pictures/On.png').subsample(4)
		OFF = PhotoImage(file = root_folder + 'GUI/Pictures/OFF.png').subsample(4)
		
		
		MT_Button = Button(Corr_Window, image =OFF, bd =0 )
		MT_Button['command'] = lambda  MT_Button = MT_Button,   ON = ON, OFF = OFF, ck2 = ck2, ck3 = ck3, ck4 = ck4 : self.Switch(MT_Button, ON, OFF, ck2, ck3,ck4, 0) 
		MT_Button.grid(row =1,column =0, padx = (20,0))
		
		TT_Button = Button(Corr_Window, image =OFF, bd =0) 
		TT_Button['command'] = lambda   TT_Button = TT_Button, ON = ON, OFF = OFF, ck2 = ck2, ck3 = ck3, ck4 = ck4 : self.Switch(TT_Button, ON, OFF, ck2, ck3, ck4, 1) 
		TT_Button.grid(row =1,column =1,padx = (20,0))
		
		
		
		
		
		ck_button1 = Button(Corr_Window,text = "OK",fg = 'black', bg = 'white', command = self.Terminate_Cor_CheckBox, width = 7)
		ck_button1['command'] = lambda Corr_Window = Corr_Window, MTOpt = MT_Opt, ThrsOpt =Thrs_Opt,  TTOpt = TT_Opt, MTGrapOpt = MTGrap_Opt, TTGrapOpt = TTGrap_Opt: self.Terminate_Cor_CheckBox(Corr_Window, MTOpt, ThrsOpt, TTOpt, MTGrapOpt,TTGrapOpt )
		ck_button1.grid(row = 4,column = 1, pady = (40,0), sticky="S")
		
		ck_button2 = Button(Corr_Window,text = "CANCEL",fg = 'white', bg = 'black', command = Corr_Window.destroy, width = 7)
		ck_button2.grid(row = 4,column = 0, pady = (40,0), sticky="S")
		
		Corr_Window.update()
		
	def Switch(self,  OnOff_button, ON, OFF, ck2, ck3, ck4, Opt):
		#On-off buttons switch of the checkbox window
		
		if Opt == 0:
			OnOff_bool = self.MT_OnOff_bool
		else:
			OnOff_bool = self.TT_OnOff_bool
		
		if OnOff_bool:
			OnOff_button .config(image = OFF)
			FT = False
			if Opt == 0:
				self.Enable_MT( ck2,ck3, 0)
			else:
				self.Enable_TT( ck4, 0)
		else:
        
			OnOff_button .config(image = ON)
			FT = True
			if Opt == 0:
				self.Enable_MT(ck2,ck3, 1)
			else:
				self.Enable_TT( ck4, 1)
		if Opt == 0:
			self.MT_OnOff_bool = FT
		else:
			self.TT_OnOff_bool = FT
	
	def Int_plot_window(self):
		
		#Plotting the integrated intensity graph displayed in the Int Intensity tab
		self.axII.clear()
		try:
			plt.cla()
			plt.clf()
		except:
			pass
		self.axII.set_xlabel('Image index')
	
		self.axII.set_title("Integrated intensity")
		self.Iint = np.zeros(self.Hdf_sizes[0])
		formatter = ticker.ScalarFormatter(useMathText=True)
		formatter.set_powerlimits((-1,1)) 
		formatter.set_scientific(True) 
		self.axII.yaxis.set_major_formatter(formatter) 
		for i in range(self.Hdf_sizes[0]):
			self.Iint[i] = np.sum(self.Int_data[i]) 
		
		
		self.figII.patch.set_facecolor('None')
		
		self.axII.plot(np.arange(self.Hdf_sizes[0]), self.Iint, 'o')
		
		
		
		self.canvasII.draw() 
		self.canvasII.get_tk_widget().place(relx= 0, rely=0.1, relwidth = 1, relheight = 0.8)
		
		self.figII.tight_layout()
		plt.switch_backend('Agg')
		
	def Enable_MT(self, ck2,ck3, Opt):
	#Configure the on-off multi-tau button 
		if Opt == 1:
			
			ck2.config(state = NORMAL)
			ck3.config(state = NORMAL)
		else:
			ck2.config(state = DISABLED)
			ck3.config(state = DISABLED)
	def Enable_TT(self, ck4,Opt):
	#Configure the on-off two-time button 
		if Opt == 1:
			
			ck4.config(state = NORMAL)
			
		else:
			ck4.config(state = DISABLED)

	def Terminate_Cor_CheckBox(self, Corr_Window, MTOpt, ThrsOpt,  TTOpt, MTGrapOpt, TTGrapOpt):
	#It closes the checkbox window and call the function to start the correlation calculations
		Corr_Window.destroy()
		MT_Opt = self.MT_OnOff_bool
		Thrs_Opt = int(ThrsOpt.get())
		TT_Opt = self.TT_OnOff_bool
		MTGrap_Opt = int(MTGrapOpt.get())
		TTGrap_Opt = int(TTGrapOpt.get())
		
		if Thrs_Opt  == 1:
		
			self.Int_int_window()
		else:
			self.Bad_frames = np.array([])
		
		if MT_Opt == 1 or TT_Opt == 1:
			InOutput.Create_results_folder(self.Res_folder)
			self.CorrelatorPanel(MT_Opt, TT_Opt, Thrs_Opt, MTGrap_Opt, TTGrap_Opt)
		
	def PlotIntInt(self, Iint, IintFit, IinDiff, Threshold, FigBool, Graph_Window):
	# Function to plot the scattering images displayed on the main window
		NData = len(Iint)
		Xi = np.arange(1,NData+1)
		if FigBool == 'True':
			self.fig, self.ax = plt.subplots(2)
			plt.xlabel('Image index')
			self.ax[0].legend(frameon = 'False')
			self.ax[0].plot(Xi, Iint, 'o')
			self.ax[0].plot(Xi, IintFit, 'r-', linewidth =4, label = "Fit")
		
		else:
			self.ax[1].clear()
		
		self.ax[1].plot(Xi, IinDiff, 'o', label = 'Subtracted')
		self.ax[1].plot([Xi[0], Xi[NData-1]], [Threshold, Threshold], 'r--', label = "Threshold")
		self.ax[1].plot([Xi[0], Xi[NData-1]], [-Threshold, -Threshold], 'r--')
		
		if FigBool == 'True':
			self.canvas = FigureCanvasTkAgg(self.fig, master = Graph_Window)
		self.canvas.draw() 
		self.canvas.get_tk_widget().grid(row =1,column =1, columnspan = 4)
		
		plt.close()
	def Plot_ROIS(self):
	# Plot the rings with the scattering image displayed on the main window
		Frame = 1
		self.Get_Entry_Values()
		ROIs = Math.ROI_Rings(self.Values[5], self.Values[6], self.Int_data[Frame], self.Values[2], self.Values[3], self.ROI_size , self.Values[7])
		fig, ax = plt.subplots(1)
		plt.title(self.Values[10] + ", frame 1")
		ROIs[ROIs==0] = np.nan
		Mask = np.array(self.mask_Arr, dtype = 'float')
		Mask[Mask ==0] = np.nan
		ax.imshow(self.Int_data[Frame], interpolation='none', norm=LogNorm(), cmap='viridis', label ='') 
		ax.imshow(Mask, cmap='Paired', interpolation='nearest', alpha=.75,label="Mask")
		ax.imshow(ROIs, cmap='Paired', interpolation='nearest', alpha=.5,label = '')
		ax.legend()
		plt.show()
			
	
	def CorrelatorPanel(self, MT_Opt, TT_Opt, Thrs_Opt, MTGrap_Opt, TTGrap_Opt):
	# This function handles the correlation calculations
		
		# Reading the parameters on the entry fields
		self.Get_Entry_Values()
		
		# Array containing all the radius of the selected rings
		ROIS = Math.ROIS_generator(self.Values[2],self.Values[3] , self.Values[7])

		
		#If the mask is empty ...
		if type(self.mask_Arr) is not np.ndarray:
			self.mask_Arr = np.zeros((self.Hdf_sizes[1], self.Hdf_sizes[1]))
		
		# If multi-tau option is selected

		if MT_Opt ==1:
		
			#Generating the multi-tau delay times
			MTdelay_intervals = Math.Multi_tau_LagTs(self.Values[9], self.Hdf_sizes[0]) 
			DelayTimes = MTdelay_intervals/float(self.Values[4])
			
			self.Write("\nMulti tau delay times (s): ",0)
			for mt in range(len(DelayTimes)-1):
				self.Write( DelayTimes[mt],1)
				self.Write(", ",1)
			self.Write(DelayTimes[len(DelayTimes)-1],1)
		g2 = []
		g2_1 = []
		q=[]
		g2_TT = []
		std_g2= []

		
		#Generating the delay times of the one-time curve
		Lin_times = np.linspace(0,self.Hdf_sizes[0]-1, self.Hdf_sizes[0])/self.Values[4]

		Name, Ext = os.path.splitext(self.Values[10])

		
		#Setting the results folder
		Results_Folder =   self.Res_folder+"/" + Name + "_RESULTS.hdf5"
		Rings_folder_name = self.Rings_data_folder  +"_"+ Name
		InOutput.Create_results_folder(Rings_folder_name)
		
		for j in range(len(ROIS)):
			
			#Inner and outter radius of the ring
			R_i = ROIS[j] - (self.ROI_size-1)/2
			R_o = ROIS[j] + (self.ROI_size-1)/2
			
			Name_It = Name + "TT_"+ '{0:04d}'.format(j)
			Name_files_ring =  Name + '_{0:04d}'.format(j)

			
			self.Write("\nRing "+ str(j+1), 0)
			q.append(Math.Q_Vector(self.Values[0],self.Values[1],  ROIS[j], self.Pixel_size))
			self.Write('q = '+ '{:.2e}'.format(q[j]) + ' 1/A',0)
			self.Write('Inner radius = '+ '{:.1f}'.format(R_i)+ ' px; ',0 )
			self.Write('Outer radius = '+ '{:.1f}'.format(R_o) + ' px;',1 )
		
			#Selecting pixels inside the ring
			self.Selected_Pixels = Math.Pick_ROI_Pixels(self.Int_data,self.Hdf_sizes[0], self.Values[5],self.Values[6],R_i,R_o,self.mask_Arr)
			
			#Retrieving the intensity of the non-masked pixels
			Iq = Math.Pick_ROI_Pixels(self.Int_data,self.Hdf_sizes[0], self.Values[5],self.Values[6],R_i,R_o,self.mask_Arr)
			
			self.Write("ROI size: "+ str(self.Selected_Pixels.shape[1]) + " pixels",0)
			
			#Saving the array containing all the intensities of the ring
			InOutput.Export_pixels_ring(Rings_folder_name, Name_files_ring, self.Selected_Pixels, q[j])
			
			#If the two-time option is selected ...
			if TT_Opt==1:
				self.Write("Calculating two-time g2 ...", 0)
				
				#Calculating the two time g2
				g2_TT.append( Math.G_two_two_timeB(self.Selected_Pixels, self.Hdf_sizes[0], self.master, self.PBar, self.style))
				TTName =   self.Res_folder + "/" + Name + "_TT_"+ '{0:04d}'.format(j)

				#Saving two-time g2 in npy format
				InOutput.Output_TwoTime(TTName +'.npy' ,  q[j], g2_TT[j])
				
				self.Write("done!", 1)
				self.Write("Calculating one-time g2 from two-time ...", 0)
			
				g2_1.append(Math.Two_time_to_one_time(g2_TT[j]))
				self.Write("done!",1)
				
				#It generates the png graph if this option is selected
				if TTGrap_Opt == 1:

					self.Write("Generating two-time g2 graph ...",0)
					InOutput.Plot_TwoTime(g2_TT[j], q[j],  TTName +".png", self.Values[4], self.Values[11])
					InOutput.Plot_OneTime( self.Res_folder + "/" + Name +  "_OT_"+ '{0:04d}'.format(j), Lin_times ,g2_1[j], q[j])		
					self.Write("graph generated!", 1)

				
			#If the multi-tau option is selected ...	
			if MT_Opt ==1:
			
				Iq_mean = np.mean(Math.Pick_ROI_Pixels(self.Int_data,self.Hdf_sizes[0], self.Values[5],self.Values[6],ROIS[j] - 1/2,ROIS[j] + 1/2,self.mask_Arr))
				
				

				self.Write("Calculating multi-tau g2 ...", 0)
				
				#Calculating the multi-tau g2

				g2_data = (Math.G_two_mult_tau(MTdelay_intervals , self.Selected_Pixels, self.Bad_frames, self.Hdf_sizes[0], np.mean(Iq_mean)))
				
				g2.append(g2_data[0])
				std_g2.append(g2_data[1])
			
				self.Write("done!", 1)
				
				#It generates the png graph if this option is selected
				if MTGrap_Opt == 1:
								
					self.Write("Generating multi-tau g2 graph ...",0)	
					InOutput.Plot_OneTime(self.Res_folder + "/" + Name + "_MT_"+ '{0:04d}'.format(j), DelayTimes,g2[j], q[j] )
					
					self.Write("graph generated!", 1)
					
			
		#-----------------Exporting the results to hdf files	------------------------------------------------------------------------			
		InOutput.Output_Pars_Hdf(Results_Folder, DelayTimes, self.Fields, self.Values,self.Unities, self.mask_Arr, self.Iint, self.Bad_frames)
		InOutput.Output_q_Hdf(Results_Folder, q)
		
		self.Write("\nGenerating the results file ...", 0)
		
		if  MT_Opt ==1:
			
			self.Update_window()
			InOutput.Output_MT_Hdf(Results_Folder,DelayTimes,   q, g2, std_g2)
			
			
		if TT_Opt==1:
			InOutput.Output_TT_TO_Hdf(Lin_times/self.Values[4], Results_Folder, g2_TT, g2_1, q)
		#---------------------------------------------------------------------------------------------------------------------------------
		
		self.Write("\nResults saved in " + Results_Folder,1)
		self.Write("Finished!",0)

		self.PBar['value'] = 0
		self.style.configure('text.Horizontal.TProgressbar',text='')
		self.Update_window()	
	def Update_window(self):
		self.area.see(END)
		self.master.update()
