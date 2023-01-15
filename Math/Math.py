#Author: Paulo R. A. F. Garcia
#email: paulo.garcia@lnls.br / pauloricardoafg@yahoo.com.br

#Python script for the calculation of the intensity autocorrelation function g2 using a multi-tau algorithm.

#version 1: 20/01/2021
 

#Class to deal with math calculations 

import numpy as np
import sys

root_folder = '/home/joao/Documents/XPCS/'

sys.path.append(root_folder + 'GUI')
import GUI


#	print(' Could not import GUI functions from the Math module! Check GUI.py and Math.py files!')


class Math:

	def Return_GUI(self):
	#Object of the GUI class
		return GUI.GUI()
		
	def Define_Threshold(self, N_data, I_data, ck):
	#Isum = Integrated intensity determined to each image
	#IsumFit = Polynomial curve fitted to the Iint points
	#StdDiff = Standard deviation of the IinDiff data
	
		Isum = np.zeros(N_data)
		DataIndex = np.arange(1,N_data+1)
		for i in range(N_data):
			Isum[i] = np.sum(I_data[i,:,:])
		FitCoef = np.polyfit(DataIndex, Isum, 40)
		FitFunc = np.poly1d(FitCoef)
		IsumFit = FitFunc(DataIndex)
		IsumDiff = Isum - IsumFit
		StdDiff = np.std(IsumDiff)
		return Isum, IsumFit, IsumDiff, StdDiff
		
	def Pick_ROI_Pixels(self, Int_data, N_frames, x0,y0,Rin,Rout,mask_arr):
	#Defining the array with the pixels
	
		rows, cols = self.Pixels_ROI_definer(x0,y0, Int_data[0], Rin, Rout, mask_arr)

		Arr_Pixels = Int_data[:,rows,cols]
		return Arr_Pixels
			
	def Pixels_ROI_definer(self, x0, y0, image_arr, Rin, Rout, mask):
	#Return the array with the pixel coordinates of the non-masked pixels inside the ring
	
		sizes = image_arr.shape
		X = np.arange(0, sizes[0]) 
		Y = np.arange(0,sizes[1])
		Rpix = np.sqrt(2.0)*0.5
		maskTemp = (X[np.newaxis,:] -  x0)**2 + (Y[:,np.newaxis] -y0)**2
		return np.where(np.logical_and(np.logical_and(maskTemp<=Rout**2 ,maskTemp >=Rin**2),mask<0.5))
		
	def ROI_Rings(self, x0, y0, image_arr, Rinit, Rfinal, ROI_width, N_ROIs):
	#Return the rings arry with different intensity values assigned to each ring for plotting
	
		sizes = image_arr.shape
		
		X = np.arange(0, sizes[0]) 
		Y = np.arange(0,sizes[1])
		
		Rings = np.zeros([sizes[0],sizes[1]])
		
		Radii = self.ROIS_generator(Rinit, Rfinal, N_ROIs)
		
		for it in range(N_ROIs):
			
			Rin = Radii[it] - (ROI_width-1)/2
			Rout = Radii[it] + (ROI_width-1)/2
			mask = (X[np.newaxis,:]- x0)**2 + (Y[:,np.newaxis]-y0)**2
			ROI_Value = it+1
			Rpix = np.sqrt(2)*0.5
			Rings[np.logical_and(mask<=(Rout+Rpix)**2 ,mask >=(Rin-Rpix)**2)] = ROI_Value 
		return Rings		
		
	
	def Multi_tau_LagTs(self,buffers, max_number):
	#It generates the multi-tau delay times
		MultT_times = np.linspace(0, (2*buffers), (2*buffers)+1, dtype = int)
		Lagt0 = 2*buffers
		ex = 1
		
		while True:
		
			for il in range(buffers):
				LValue = (Lagt0 + (il+1)*2**ex)
				if LValue>max_number:
					break
				MultT_times = np.append(MultT_times,LValue)
				
			if LValue>max_number:
					break	
			Lagt0 += buffers*2**ex
			ex = ex+1
		
		return MultT_times
		
	def G_two_mult_tau(self, MultT_times, Pixels_arr, Bad_frames, N_frames, Iq_mean):
	# Multi-tau function
		N_Tau = len(MultT_times)
		N_pixels = Pixels_arr.shape[1] 
		ImgCorr = np.zeros((N_Tau, N_pixels), dtype= 'float64')
		k=0
		
		for i in MultT_times:
			NIt = 0
			Gt =0
			for j in range(N_frames):
				
				if j+i>=N_frames:
					break
				else:
					if j not in Bad_frames and j+i not in Bad_frames:
						j_Arr =  Pixels_arr[j][:]
						ji_Arr = Pixels_arr[j+i][:]
						ImgCorr[k][:] += j_Arr*ji_Arr/(np.mean(j_Arr)*np.mean(ji_Arr))
						NIt += 1

			if NIt !=0:
				ImgCorr[k][:] /= NIt
				k+=1
				
		return [np.mean(ImgCorr[i,:])for i in range(N_Tau)], [np.std(ImgCorr[ii,:])/np.sqrt(len(ImgCorr[ii,:])) for ii in range(N_Tau)]

	def G_two_two_timeA(self, Pixels_arr, N_frames, master, PBar, style):
	#Two-time function, algorithm 1
	
		PBar.config(style='text.Horizontal.TProgressbar')
		ImgCorr = np.zeros((N_frames, N_frames))
		for i in range(N_frames):
			for j in range(N_frames):
				left_Arr =  Pixels_arr[i][:]
				right_Arr = Pixels_arr[j][:]
				L_mean = np.mean(left_Arr)
				R_mean = np.mean(right_Arr)
				
				Den1 = np.sqrt(np.mean(left_Arr*left_Arr) - L_mean*L_mean)
				Den2 = np.sqrt(np.mean(right_Arr*right_Arr) - R_mean*R_mean)
				ImgCorr[j][i]= (np.mean(left_Arr*right_Arr) - L_mean*R_mean)/(Den1*Den2)
			Pct = (i+1)*100/N_frames
			PBar['value'] = Pct
			style.configure('text.Horizontal.TProgressbar',text='{:g} %'.format(Pct))
			master.update_idletasks()
		return ImgCorr
	def G_two_two_timeB(self, Pixels_arr, N_frames, master, PBar, style):
	#Two-time function, algorithm 2
	
		PBar.config(style='text.Horizontal.TProgressbar')
		ImgCorr = np.zeros((N_frames, N_frames))
		for i in range(N_frames):
			for j in range(N_frames):
				left_Arr =  Pixels_arr[i][:]
				right_Arr = Pixels_arr[j][:]
				L_mean = np.mean(left_Arr)
				R_mean = np.mean(right_Arr)
				
				ImgCorr[j][i]= np.mean(left_Arr*right_Arr)/(L_mean*R_mean)
			Pct = (i+1)*100/N_frames
			PBar['value'] = round(Pct,2)
			style.configure('text.Horizontal.TProgressbar',text='{:g} %'.format(Pct))
			master.update_idletasks()
		return ImgCorr
	def Two_time_to_one_time(self,TT_data):
	#It calculates the one-time curve from two-time
	
		N_time = TT_data.shape[0]
		g_2_to_1 = np.zeros(N_time)
		 
		for i in range(N_time):
			for j in range(i,N_time):
				g_2_to_1[i] += TT_data[j,j-i]	
			g_2_to_1[i]/=(N_time -i)
		return g_2_to_1
	
	def ROIS_generator(self, Rin, Rout, N_Rois):
	#Generation of the rings radius array
		return np.linspace(Rin, Rout, N_Rois)
	
	def Q_Vector(self, Lambda,Sample_to_Detector,  Radius, Pixel_size):
	#It calculates the q value: q = (4pi/lam)sin(theta), lam is the wavelength and theta is
	#half of the scattering angle
	
		#Pixel size in microns!!!!
		#Sample to detector distance in meters!!!
		#Lambda in Angstrons!!
		#Return q in A^-1!!
		
		YDist = (Radius)*Pixel_size*1E-6
		Theta = 0.5*np.arctan(YDist/Sample_to_Detector)
		
		return (4*np.pi/(Lambda*1E-10))*np.sin(Theta)*1E-10
	
