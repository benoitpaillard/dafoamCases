import os,numpy,glob

os.system("csplit -z deformedFFD.dat /Zone/ '{*}'")

nElements=len(glob.glob('profile*.stl'))

for ii in range(nElements):
	box=numpy.loadtxt('xx0'+str(int(ii*2+1)),skiprows=2)
	box=box[:int(len(box)/2)]

	boxExtrados=box[:int(len(box)/2)]
	boxIntrados=box[int(len(box)/2):]

	weightTip=0.95

	boxTEx=weightTip*(boxExtrados[0,0]+boxIntrados[0,0])/2 +(1-weightTip)*(boxExtrados[1,0]+boxIntrados[1,0])/2
	boxTEy=weightTip*(boxExtrados[0,1]+boxIntrados[0,1])/2 +(1-weightTip)*(boxExtrados[1,1]+boxIntrados[1,1])/2

	boxLEx=weightTip*(boxExtrados[-1,0]+boxIntrados[-1,0])/2+(1-weightTip)*(boxExtrados[-2,0]+boxIntrados[-2,0])/2
	boxLEy=weightTip*(boxExtrados[-1,1]+boxIntrados[-1,1])/2+(1-weightTip)*(boxExtrados[-2,1]+boxIntrados[-2,1])/2

	numpy.savetxt('LEconsProfile'+str(ii),[boxLEx,boxLEy,0])
	numpy.savetxt('TEconsProfile'+str(ii),[boxTEx,boxTEy,0])
	
##debug

numpy.savetxt('LEconsProfile0',[1e-3,1e-3,0])
numpy.savetxt('TEconsProfile0',[1-1e-3,1e-3,0])
