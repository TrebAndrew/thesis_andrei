#############################################################################
#Calculate electric field from an undulator/upload electric field from files. 
#Propogate them through a slit. Plot intensity distribution and spectrum.
#v0.1
#############################################################################

from __future__ import print_function #Python 2.7 compatibility
from srwlib import *
from uti_plot import *
import os
import sys
import pickle
import matplotlib.pyplot as plt
print('SKIF Extended Example # 3:')
print('Calculate electric field from an undulator/upload electric field from files. Propogate them through a slit')

#**********************Output files
wfrPathName = '/home/andrei/Documents/SKIF_XFAS_beamline/fields/' #example data sub-folder name
wfr1FileName = 'wfr1_for_und.wfr' #file name for output UR flux data
wfr2FileName = 'wfr2_for_und.wfr' #file name for output UR intesity data

#***********Undulator

undarr = []
undarrH = []
distz =  []
distx =  []
disty =  []

PER = 60
NumPIECE = 3
undper = 0.0156
numper = PER/NumPIECE
magf = 1
magf_step = 10/100

Bx = 1 #Peak Horizontal field [T]
By = 1 + magf_step/2 #+ (NumPIECE-1)*magf_step#Peak Vertical field [T]
phBx = 0#Initial Phase of the Horizontal field component
phBy = 0 #Initial Phase of the Vertical field component
sBx = 1 #Symmetry of the Horizontal field component vs Longitudinal position
sBy = 1 #Symmetry of the Vertical field component vs Longitudinal position
xcID = 0 #Transverse Coordinates of Undulator Center [m]
ycID = 0
zcID = 0 #Longitudinal Coordinate of Undulator Center [m]

harmB1 = SRWLMagFldH() #magnetic field harmonic
harmB1.n = 1 #harmonic number
harmB1.h_or_v = 'v' #magnetic field plane: horzontal ('h') or vertical ('v')
harmB1.B = magf + 0*magf_step #magnetic field amplitude [T]
und1 = SRWLMagFldU([harmB1])
und1.per = undper  #period length [m]
und1.nPer = numper #number of periods (will be rounded to integer)

magFldCnt = SRWLMagFldC([und1], array('d', [0]), array('d', [0]), array('d', [0])) #Container of all Field Elements

#***********Auxiliary Electron Trajectory structure (for test)
partTraj = SRWLPrtTrj() #defining auxiliary trajectory structure
partTraj.partInitCond = eBeam.partStatMom1
partTraj.allocate(20001) 
partTraj.ctStart = -1.6 #Start "time" for the calculation
partTraj.ctEnd = 1.6

#***********Precision Parameters
arPrecF = [0]*5 #for spectral flux vs photon energy
arPrecF[0] = 1 #initial UR harmonic to take into account
arPrecF[1] = 21 #final UR harmonic to take into account
arPrecF[2] = 1.5 #longitudinal integration precision parameter
arPrecF[3] = 1.5 #azimuthal integration precision parameter
arPrecF[4] = 1 #calculate flux (1) or flux per unit surface (2)

arPrecP = [0]*5 #for power density
arPrecP[0] = 1.5 #precision factor
arPrecP[1] = 1 #power density computation method (1- "near field", 2- "far field")
arPrecP[2] = 0 #initial longitudinal position (effective if arPrecP[2] < arPrecP[3])
arPrecP[3] = 0 #final longitudinal position (effective if arPrecP[2] < arPrecP[3])
arPrecP[4] = 20000 #number of points for (intermediate) trajectory calculation

meth = 1 #SR calculation method: 0- "manual", 1- "auto-undulator", 2- "auto-wiggler"
relPrec = 0.001 #relative precision
zStartInteg = 0 #longitudinal position to start integration (effective if < zEndInteg)
zEndInteg = 0 #longitudinal position to finish integration (effective if > zStartInteg)
npTraj = 20000 #Number of points for trajectory calculation 
useTermin = 1 #Use "terminating terms" (i.e. asymptotic expansions at zStartInteg and zEndInteg) or not (1 or 0 respectively)
sampFactNxNyForProp = 0 #sampling factor for adjusting nx, ny (effective if > 0)
arPrecPar = [meth, relPrec, zStartInteg, zEndInteg, npTraj, useTermin, sampFactNxNyForProp]

afile = open(wfrPathName + wfr1FileName, 'rb')
wfr1 =  pickle.load(afile)
afile.close()

afile = open(wfrPathName + wfr2FileName, 'rb')
wfr2 =  pickle.load(afile)
afile.close()
            ######### Spectrum #######

print('   Extracting Intensity from calculated Electric Field(Spectral Flux) ... ', end='')
arI1 = array('f', [0]*wfr1.mesh.ne)
srwl.CalcIntFromElecField(arI1, wfr1, 6, 2, 0, wfr1.mesh.eStart, wfr1.mesh.xStart, wfr1.mesh.yStart)
print('done')

print('   Plotting the results (blocks script execution; close any graph windows to proceed) ... ', end='')
uti_plot1d(arI1, [wfr1.mesh.eStart, wfr1.mesh.eFin, wfr1.mesh.ne], ['Photon Energy [eV]', 'Flux [ph/s/.1%bw]', 'Multielectron Calculation Spectrum Spectrum'])
plt.savefig('/home/andrei/Documents/9_term/diplom/BEAMLINE/images/' + 'Spectral_Flux_multi_electr_ph_s_.1%bw' + '.png', dpi=500)
#/mm^2
'''
print('   Extracting Intensity from calculated Electric Field(Spectral Flux) ... ', end='')
arI1 = array('f', [0]*wfr1.mesh.ne)
srwl.CalcIntFromElecField(arI1, wfr1, 6, 0, 0, wfr1.mesh.eStart, wfr1.mesh.xStart, wfr1.mesh.yStart)
print('done')

print('   Plotting the results (blocks script execution; close any graph windows to proceed) ... ', end='')
uti_plot1d(arI1, [wfr1.mesh.eStart, wfr1.mesh.eFin, wfr1.mesh.ne], ['Photon Energy [eV]', 'Intensity [ph/s/.1%bw/mm^2]', 'Single Electron Calculation Spectrum'])
plt.savefig('/home/andrei/Documents/9_term/diplom/BEAMLINE/images/' + 'Intensity_one_electr_ph_s_.1%bw_mm^2' + '.png', dpi=500)

print('   Extracting Intensity from calculated Electric Field(Spectral Flux) ... ', end='')
arI1 = array('f', [0]*wfr1.mesh.ne)
srwl.CalcIntFromElecField(arI1, wfr1, 6, 1, 0, wfr1.mesh.eStart, wfr1.mesh.xStart, wfr1.mesh.yStart)
print('done')

print('   Plotting the results (blocks script execution; close any graph windows to proceed) ... ', end='')
uti_plot1d(arI1, [wfr1.mesh.eStart, wfr1.mesh.eFin, wfr1.mesh.ne], ['Photon Energy [eV]', 'Intensity [ph/s/.1%bw/mm^2]', 'Multielectron Calculation Spectrum'])
plt.savefig('/home/andrei/Documents/9_term/diplom/BEAMLINE/images/' + 'Intensity_multi_electr_ph_s_.1%bw_mm^2' + '.png', dpi=500)

'''
            ######### Intensity #######
'''
print('   Performing Electric Field (wavefront at fixed photon energy) calculation ... ', end='')
srwl.CalcElecFieldSR(wfr2, 0, magFldCnt, arPrecPar)
print('done')
'''
print('   Extracting Intensity from calculated Electric Field ... ', end='')
arI2 = array('f', [0]*wfr2.mesh.nx*wfr2.mesh.ny) #"flat" array to take 2D intensity data
srwl.CalcIntFromElecField(arI2, wfr2, 6, 0, 3, wfr2.mesh.eStart, 0, 0)
print('done')

uti_plot2d(arI2, [1000*wfr2.mesh.xStart, 1000*wfr2.mesh.xFin, wfr2.mesh.nx], [1000*wfr2.mesh.yStart, 1000*wfr2.mesh.yFin, wfr2.mesh.ny], ['Horizontal Position [mm]', 'Vertical Position [mm]', 'Intensity at ' + str(wfr2.mesh.eStart) + ' eV'])
plt.savefig('/home/andrei/Documents/9_term/diplom/BEAMLINE/images/' + 'Intensity_multi_electr' + '.png', dpi=500)

srwl.CalcIntFromElecField(arI2, wfr2, 6, 0, 3, wfr1.mesh.eStart, 0, 0)
print('done')
'''
arI2x = array('f', [0]*wfr2.mesh.nx) #array to take 1D intensity data (vs X)
srwl.CalcIntFromElecField(arI2x, wfr2, 6, 0, 1, wfr2.mesh.eStart, 0, 0)
uti_plot1d(arI2x, [1000*wfr2.mesh.xStart, 1000*wfr2.mesh.xFin, wfr2.mesh.nx], ['Horizontal Position [mm]', 'Intensity [ph/s/.1%bw/mm^2]', 'Intensity at ' + str(wfr2.mesh.eStart) + ' eV\n(horizontal cut at x = 0)'])

arI2y = array('f', [0]*wfr2.mesh.ny) #array to take 1D intensity data (vs Y)
srwl.CalcIntFromElecField(arI2y, wfr2, 6, 0, 2, wfr2.mesh.eStart, 0, 0)
uti_plot1d(arI2y, [1000*wfr2.mesh.yStart, 1000*wfr2.mesh.yFin, wfr2.mesh.ny], ['Vertical Position [mm]', 'Intensity [ph/s/.1%bw/mm^2]', 'Intensity at ' + str(wfr2.mesh.eStart) + ' eV\n(vertical cut at y = 0)'])
    
uti_plot_show() #show all graphs (and block execution)
print('done')
'''

#***************** Optical Elements and Propagation Parameters
slit = 0.6 # mm
Drift_Slits_HFM = SRWLOptD(1.) #Drift from first Slits to Horizontally-Focusing Mirror (HFM)
SSA = SRWLOptA('r', 'a', 2*slit*1e-03, 2*slit*1e-03)
Drift_SSA_SCREEN = SRWLOptD(1.) #Drift from SSA to Center of Vertically Focusing K-B Mirror (VKB)


#Wavefront Propagation Parameters:
#                    [ 0] [1] [2]  [3] [4] [5]  [6]  [7]  [8]  [9] [10] [11] 
ppSSA =              [ 0,  0, 1.0,  0,  0, 1.0, 1.0, 1.0, 1.0,  0,  0,   0]
ppDrift_SSA_VKB =    [ 0,  0, 1.0,  1,  0, 1.1, 1.0, 1.1, 1.0,  0,  0,   0]
#[ 0]: Auto-Resize (1) or not (0) Before propagation
#[ 1]: Auto-Resize (1) or not (0) After propagation
#[ 2]: Relative Precision for propagation with Auto-Resizing (1. is nominal)
#[ 3]: Allow (1) or not (0) for semi-analytical treatment of the quadratic (leading) phase terms at the propagation
#[ 4]: Do any Resizing on Fourier side, using FFT, (1) or not (0)
#[ 5]: Horizontal Range modification factor at Resizing (1. means no modification)
#[ 6]: Horizontal Resolution modification factor at Resizing
#[ 7]: Vertical Range modification factor at Resizing
#[ 8]: Vertical Resolution modification factor at Resizing
#[ 9]: Type of wavefront Shift before Resizing (not yet implemented)
#[10]: New Horizontal wavefront Center position after Shift (not yet implemented)
#[11]: New Vertical wavefront Center position after Shift (not yet implemented)

#"Beamline" - Container of Optical Elements (together with the corresponding wavefront propagation instructions)
optBL = SRWLOptC([SSA, Drift_SSA_SCREEN], [ppSSA, ppDrift_SSA_VKB])#SSA, Drift_SSA_SCREEN],
#optBL = SRWLOptC([Drift_Slits_HFM, Drift_SSA_SCREEN], [ppDrift_Slits_HFM, ppDrift_SSA_VKB])#SSA, Drift_SSA_SCREEN],
#, ppSSA, ppDrift_SSA_VKB])#, ppApKB, ppVKB, ppDrift_VKB_HKB, ppHKB, ppDrift_HKB_Sample, ppFinal]) 

#///////////WAVEFRONT PROPOGATION//////#

print('   Simulating Electric Field Wavefront Propagation ... ', end='')
t0 = time.time();
srwl.PropagElecField(wfr2, optBL)
srwl.PropagElecField(wfr1, optBL)

print('done; lasted', round(time.time() - t0), 's')

print('   Extracting Intensity from the Propagated Electric Field  ... ', end='')
arI1 = array('f', [0]*wfr2.mesh.nx*wfr2.mesh.ny) #"flat" 2D array to take intensity data
srwl.CalcIntFromElecField(arI1, wfr2, 6, 0, 3, wfr2.mesh.eStart, 0, 0)
uti_plot2d(arI1, [1000*wfr2.mesh.xStart, 1000*wfr2.mesh.xFin, wfr2.mesh.nx], [1000*wfr2.mesh.yStart, 1000*wfr2.mesh.yFin, wfr2.mesh.ny], ['Horizontal Position [mm]', 'Vertical Position [mm]', 'Intensity at ' + str(wfr2.mesh.eStart) + ' eV'])

print('   Extracting Intensity from calculated Electric Field(Spectral Flux) ... ', end='')
arI1 = array('f', [0]*wfr1.mesh.ne)
srwl.CalcIntFromElecField(arI1, wfr1, 6, 3, 0, wfr1.mesh.eStart, wfr1.mesh.xStart, wfr1.mesh.yStart)
uti_plot1d(arI1, [wfr1.mesh.eStart, wfr1.mesh.eFin, wfr1.mesh.ne], ['Photon Energy [eV]', 'Intensity [ph/s/.1%bw/mm^2]', 'On-Axis Spectrum'])












