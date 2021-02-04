#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#	- This file is a part of the supplementary material for the scientific paper 'Modelling microprosodic effects leads to an audible improvement in 
#	  articulatory synthesis', see https://github.com/TUD-STKS/Microprosody
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#
#	- Copyright (C) 2021, Paul Konstantin Krug, Dresden, Germany
#	- https://github.com/TUD-STKS/Microprosody
#	- Author: Paul Konstantin Krug, TU Dresden
#
#	- License:
#
#		This program is free software: you can redistribute it and/or modify
#		it under the terms of the GNU General Public License as published by
#		the Free Software Foundation, either version 3 of the License, or
#		(at your option) any later version.
#		
#		This program is distributed in the hope that it will be useful,
#		but WITHOUT ANY WARRANTY; without even the implied warranty of
#		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#		GNU General Public License for more details.
#		
#		You should have received a copy of the GNU General Public License
#		along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Requirements:
#	- python 3 (tested with version 3.7)
#	- numpy    (tested with version 1.19.5)
#	- pandas   (tested with version 1.2.1)
#	- scipy    (tested with version 1.6.0)
#
# Optional, used for visualization:
#	- matplotlib        (tested with version 3.3.3)
#	- praat-parselmouth (tested with version 0.3.3)
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Load essential packages:
import os, sys, argparse
import numpy as np
import pandas as pd
from PyVTL import PyVTL as pv
from PyVTL import F0_Manipulation
# Try to load some non-essential packages, used for the visualization of the pitch manipulation:
try:
	import matplotlib
	import matplotlib.pyplot as plt
	import parselmouth
	visualization = True
except ImportError:
	visualization = False
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################



#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# List of the utterances:
utterances = [
'01-Badetag-final',
'02-Bewirken-final',
'03-Butterweich-final',
'04-Giraffe-final',
'05-Kakadu-final',
'06-Karotte-final',
'07-Kassette-final',
'08-Musiker-final',
'09-Vergessen-final',
'10-Zigarre-final',
'11-Aber sehen will sie ihn doch-final',
'12-Er sah viele bunte Regenbogen-final',
'13-Chabos wissen wer der Babo ist-final',
'14-Das Telefon ist seit sieben Tagen kaputt-final',
'15-Die Artikel waren wieder vorraetig-final',
'16-Die Sosse ist viermal uebergekocht-final',
'17-Die Strassenbahn fuhr weiter geradeaus-final',
'18-Diese Zeitung ist bereits veraltet-final',
'19-Sie faehrt keinen Ferrari sondern einen Maserati-final',
'20-Benno gefaellt die orange Vase-final',
]

# Create stimuli with following modes:
modes = [
{'mode': '_plain',   'flutter': 0,   'A': 0.0},  # Plain stimuli
{'mode': '_mp',      'flutter': 0,   'A': 1.0},  # Manipulated stimuli with an amplitude factor of A = 1.0
{'mode': '_mp',      'flutter': 0,   'A': 1.5},  # Manipulated stimuli with an amplitude factor of A = 1.5
{'mode': '_mp',      'flutter': 0,   'A': 2.0},  # Manipulated stimuli with an amplitude factor of A = 2.0
]
# To create samples with flutter use entries like this:
#{'mode': '_flutter', 'flutter': 25,  'A': 0.0},  # Stimuli without microprosody, but with flutter = 25

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################



#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
class Analysis:
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __init__( self, verbose = True ):
		self.gesFilePath   = 'Stimuli/Gestural_Scores/'
		self.segFilePath   = 'Stimuli/Segment_Sequences/'
		self.tractFilePath = 'Stimuli/Tract_Sequences/'
		self.audioFilePath = 'Stimuli/Audio/'
		if not os.path.exists( self.tractFilePath ):
			os.mkdir( self.tractFilePath )
		if not os.path.exists( self.audioFilePath ):
			os.mkdir( self.audioFilePath )
		self.VTL = pv.PyVTL()
		self.F0 = F0_Manipulation.F0_Manipulation()
		self.verbose = verbose
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __del__( self ):
		print('Analysis closed.')
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def create_stimulus( self, utterance: str, mode: str, flutter_amplitude: int = 0, mp_amplitude: float = 0.0 ):
		if self.verbose:
			print('\n#------------------------------------------------------------------------------------------------#')
			print( 'Generating utterance: "{}", using parameters: flutter = {}, A = {}'.format(utterance, flutter_amplitude, mp_amplitude) )
		gestural_score   = self.gesFilePath + utterance + '.ges'
		segment_sequence = self.segFilePath + utterance + '.seg'
		tract_sequence   = self.tractFilePath + utterance + '_tractSeq.txt'

		df_GLP, df_VTP = self.VTL.ges_score_to_tract_seq( gestural_score, tract_sequence, return_Sequence = True ) # Read ges score, return content
		df_GLP_manipulated = df_GLP.copy()
		label_f = ''
		label_mp = ''
	
		df_GLP_manipulated.iloc[:,9] = flutter_amplitude # Glottis parameter number 9 (flutter) is set to 0 for all plain and manipulated samples
		if flutter_amplitude > 0:
			label_f = '_{}'.format( str(flutter_amplitude) )
		if mp_amplitude > 0.0:
			df_timestamps, _ , _ = self.F0.get_obstruents( segment_sequence )
			df_GLP_manipulated.iloc[:,0] = self.F0.manipulate_F0( df_GLP.iloc[:,0], df_timestamps, mp_amplitude )
			label_mp = '_{}'.format( str(mp_amplitude) )

		tract_sequence_mod = self.tractFilePath + utterance + mode + label_mp + label_f + '_tractSeq.txt' # Name of the modified tract sequence
		audio_file = self.audioFilePath + utterance + mode + label_mp + label_f + '.wav'
	
		self.VTL.df_to_tract_seq( tract_sequence_mod, df_GLP_manipulated, df_VTP ) # Create manipulated tract sequence

		Audio = self.VTL.tract_seq_to_audio( tract_sequence_mod ) # Turn tract sequence into an audio file
		Audio_N = self.VTL.Normalise_Wav( Audio, -1 ) #Normalise wav to -1 dB
		self.VTL.Write_Wav( Audio_N, audio_file )
		if self.verbose:
			print( 'Synthesized and saved the utterance.' )
	
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def visualize_stimuli( self, audio_files: list, labels: list, utterance: str ):
		assert visualization, 'Can not visualize the stimuli, you have to install the matplotlib and parselmouth libraries!'
		df_list = []
		for audio_file in audio_files:
			snd = parselmouth.Sound( audio_file )
			pitch = snd.to_pitch()
			pitch_times  = pitch.xs()
			pitch_values = pitch.selected_array['frequency']
			pitch_values[pitch_values==0] = np.nan
			pitch_values[pitch_values>=250] = np.nan
			pitch_values[pitch_values<=50] = np.nan
			df = pd.DataFrame( np.array( [pitch_times, pitch_values] ).T, columns =['Time','Pitch'] )
			df_list.append( df )
		df_obstruents, df_values, df_times = self.F0.get_obstruents( self.segFilePath + utterance + '.seg' )
		fig, ax = plt.subplots( figsize = (14, 6) )
		for f, df in enumerate( df_list ):
			LABEL = labels[f]
			ax.scatter( df.iloc[:,0], df.iloc[:,1], label=LABEL, marker='.' )
		value_range = np.abs( df['Pitch'].max() - df['Pitch'].min() )
		f0_min, f0_max = [ df['Pitch'].min()-0.25*value_range, df['Pitch'].max()+0.25*value_range ]
		ax.set( xlabel="Time [s]", ylabel="F0 [Hz]", title=utterance, ylim=[f0_min, f0_max])
		first_IF0 = True
		first_CF0 = True
		for row, _ in enumerate(df_obstruents.index):
			if df_obstruents.iloc[row,2] == 'IF0':
				d_abs = df_obstruents.iloc[row,1] - df_obstruents.iloc[row,0]
				if first_IF0 == True:
					Label = 'IF0'
					first_IF0 = False
				else:
					Label = None
				time_IF0_start = df_obstruents.iloc[row,0] - 0.4*d_abs
				time_IF0_end   = df_obstruents.iloc[row,1] + 0.2*d_abs
				ax.axvspan( time_IF0_start, time_IF0_end, alpha=0.2, edgecolor='darkviolet', ls='--', label = Label)
			elif df_obstruents.iloc[row,2] == 'CF0':
				if first_CF0 == True:
					Label = 'CF0'
					first_CF0 = False
				else:
					Label = None
				ax.axvspan(df_obstruents.iloc[row,1], df_obstruents.iloc[row,1] + self.F0.CF0_Duration, alpha=0.2, color='magenta', label= Label)
		y_min, y_max = ax.get_ylim()
		for index, time in enumerate(df_times):
			ax.axvspan(time, time, ymin= 0.9, alpha =1.0, color= 'black')
			if index < len(df_times)-1:
				x_pos = np.abs(df_times[index + 1] + df_times[index]) /2
				ax.text(x_pos,y_max-(0.07*(y_max-y_min)), df_values[index], ha='center')
		plt.legend(loc='center right')
		if not os.path.exists( 'Figures/' ):
			os.mkdir( 'Figures/' )
		plt.tight_layout()
		plt.savefig( 'Figures/F0_' + utterance + '.png' )
		#plt.show()
		plt.close()
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################


			
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
def main( args ):
	analysis = Analysis()
	if args.create_stimuli:
		for utterance in utterances:
			for mode in modes:
				analysis.create_stimulus( utterance = utterance, mode = mode['mode'], flutter_amplitude = mode['flutter'], mp_amplitude = mode['A'] )

	if args.visualize:
		for utterance in utterances:
			audios = []
			labels = []
			for mode in modes:
				label = mode['mode']
				if mode['mode'] == '_mp':
					label += '_{}'.format( mode['A'] )
				elif mode['mode'] == '_flutter':
					label += '_{}'.format( mode['flutter'] )
				audios.append( analysis.audioFilePath + utterance + label + '.wav' )
				labels.append( label.strip('_') )
			print( 'Visualizing following modes: {}'.format( labels ) )
			analysis.visualize_stimuli( audios, labels, utterance )

	return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################



#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
	parser = argparse.ArgumentParser( description='Description of the Microprosody Analysis class:' )
	parser.add_argument('--create_stimuli', action = 'store_true' )
	parser.add_argument('--visualize', action = 'store_true' )
	args = parser.parse_args()
	main( args )
print('Done.')
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################