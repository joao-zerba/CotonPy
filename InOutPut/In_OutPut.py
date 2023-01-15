#Author: Paulo R. A. F. Garcia
#email: paulo.garcia@lnls.br / pauloricardoafg@yahoo.com.br

#Python script for the calculation of the intensity autocorrelation function g2 using a multi-tau algorithm.

#version 1: 20/01/2021
 

#Class with functions which work with input and output 

import h5py, sys
import numpy as np
import matplotlib.pyplot as plt
import csv, os

root_folder = '/home/joao/Documents/XPCS/'

try:
	sys.path.append(root_folder + 'Init')
	import InitPars
except Exception as e:
	print(' Could not initialize parameters! Check the InitPars.py file.', e)
	exit(0)


class Input_Output:
		
	def Init_Parameters(self):
	#To import the initial set of parameters
		try:
			return InitPars.InitPars()
			
		except Exception as e:
			print(" Error while reading InitPars.py file: ",e)
	
	def HdfInfo(self, FileName):
	#Function to read the hdf file shape 
		with h5py.File(FileName, "r", swmr=True) as f:
			hdfData = f['data']
			sizes = hdfData.shape
		return sizes
		
	def Load_Hdf(self, FileName):
	#Load the hdf file
		with h5py.File(FileName, "r", swmr=True) as f:
			hdfData = np.array(f['data'], dtype = 'float')
		return	hdfData
		
	def Load_binary(self, FileName, Nimg, Nx, Ny, data_type):
	#Load binary file
		datar = np.fromfile(FileName, dtype = data_type)
		return datar.reshape(Nimg,Nx,Ny)
		
	def Load_Mask(self, MaskName):
	#Load mask file
		try:
			Name, Ext = os.path.splitext(MaskName)
			if Ext == '.msk':
				import fabio
				return np.flip((fabio.open(MaskName)).data,0)
				#return fabio.open(MaskName).data
			else:
				return np.load(MaskName)
		except Exception as e:
			print(e)
			return np.nan
	def Output_GTwo(self, FileName,  q, N_qBins, DelayTimes, g2):
		QArray = q
		QArray.insert(0,"q")
		NCol = N_qBins+1
		NRow = len(g2[0])
		gArray =np.zeros((NRow, NCol))
		gArray[:,0] = DelayTimes 
	
		for i in range(1,NCol):
			gArray[:,i] = g2[i-1,:] 
		with open(FileName, 'w') as wfile:
			wf = csv.writer(wfile, delimiter = '\t')
			wf.writerow(QArray)
			for i in range(NRow):
				wf.writerow(gArray[i,:])
				
	def Output_TwoTime(self, FileName,  q, g2_TwoTime):
	#Export two-time graph to npy file
		with open(FileName, 'wb') as f:
			np.save(f, g2_TwoTime)

	def Output_Pars_Hdf(self,  FileName, DelayT, Fields, Pars,Unities, mask, IntInt, Bad_frames):
	# Exporting the parameters to hdf file

		if os.path.isfile(FileName):
			os.system("rm "+FileName)
		Int_data = np.zeros((Pars[11],2))
		Int_data[:,0] = np.linspace(1,Pars[11],Pars[11])
		Int_data[:,1] = IntInt
		
		
		Fields_Unities = [0] * len(Fields)
		for iff in range(int(len(Fields))):
			if(Unities[iff] == ""):
				Fields_Unities[iff] = Fields[iff]
			else:
				Fields_Unities[iff] = Fields[iff] + " ("+ Unities[iff]+ ")"
		
		if not Bad_frames:
				Bad_frames = "None"
		with h5py.File(FileName, "a") as ff: 
			ff.create_dataset("Experimental data folder/Folder path", data = FileName)
			for ih in range(int(len(Fields))):
				ff.create_dataset("Parameters/" + Fields_Unities[ih] , data =Pars[ih] )
			ff.create_dataset("Delay times/Delay times (s)", data = DelayT)
			ff.create_dataset("Integrated intensity/Integrated intensity", data = Int_data)
			ff.create_dataset("Mask/Mask", data = mask)
			ff.create_dataset("Unconsidered frames/Unconsidered frames", data = Bad_frames)
			ff.close
			
	def Output_MT_Hdf(self,FileName,delay_time, qi,  MT_data, MT_std):


	#It exports the multi-tau curve to hdf file

		data_types = [float,float,float]
		data_headers = ['delay time (s)', 'g2', 'std']	
		ds_dt = np.dtype({'names':data_headers,'formats': data_types }) 
            	
		for ik in range(len(MT_data)):
			data_data = []
			data_data.append(delay_time)
			data_data.append(MT_data[ik])
			data_data.append(MT_std[ik])
			
			rec_arr =  np.rec.fromarrays(list(map(list, zip(data_data))), dtype=ds_dt)
			with h5py.File(FileName, "a") as f:
				f.create_dataset("Multi-tau/ q = "+'{:.2e}'.format(qi[ik]) +" A^-1", (len(data_data[0]),), data=rec_arr)	
				f.close

				
	def Output_TT_TO_Hdf(self,delay_time, FileName,TT_data, TO_data, q):
	#It exports the one-time curve obtained from two-time to hdf file

		data_types = [float,float]
		data_headers = ['delay time (s)', 'g2']	
		ds_dt = np.dtype({'names':data_headers,'formats': data_types }) 
		
		for ik in range(len(q)):
			data_data = []
			data_data.append(delay_time)
			data_data.append(TO_data[ik])
			
			rec_arr =  np.rec.fromarrays(list(map(list, zip(data_data))), dtype=ds_dt)
		
			with h5py.File(FileName, "a") as f:
				
				f.create_dataset("Two-time/q = " + '{:.2e}'.format(q[ik]) + ' A^-1', data = TT_data[ik])
				f.create_dataset("Two to one time/q = " + '{:.2e}'.format(q[ik]) + ' A^-1', (len(data_data[0]),), data=rec_arr)
			f.close
				
	def Output_q_Hdf(self,FileName, q):


	# It inserts q values in the hdf file

		with h5py.File(FileName, "a") as f:
			f.create_dataset("Parameters/q (A^-1)", data = q)
			f.close
			
	def Plot_OneTime(self, ImName, tau,gA, q):
	#It saves one-time graph in a png file  
		plt.xlabel('Delay time (s)')
		plt.ylabel('g^2')
		plt.title("q = "+'{:.2e}'.format(q) + " A^-1")
		plt.semilogx(tau[1:], gA[1:],'o')
		plt.savefig(ImName)
		plt.close()

	def Plot_TwoTime(self, g2_TwoTime, q, FileName, freq, Nframes):
	#It saves two-time graph in a png file  
		fi = 1.0/freq
		ff = Nframes/freq
		plt.xlabel('Frame time (s)')
		plt.ylabel('Frame time (s)')
		plt.title("q = "+'{:.2e}'.format(q) + " A^-1")
		plt.imshow(g2_TwoTime, interpolation = 'nearest', cmap = 'inferno', origin='lower' , extent = [fi,ff,fi,ff])
		plt.colorbar()
		plt.savefig(FileName)
		plt.close()

	
	def Save_dat_file(self, file_name, data, file_path):
	#Generating the dat file
		np.savetxt(file_path + file_name +'.dat',data)
	
	def Create_results_folder(self, folder_path):
	#To create the results folder
		if not os.path.isdir(folder_path):
			os.system( "mkdir " + folder_path)

			
	def Export_pixels_ring(self, folder, f_name, Selected_pixels,q):
	#It exports the ring intensity data in a dat file
		for im in range(Selected_pixels.shape[0]):
			np.savetxt(folder +"/" + f_name + '_{0:04d}'.format(im) + '.txt', Selected_pixels[im], header = 'q = ' + str(q))

