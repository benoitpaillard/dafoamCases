import numpy,os
#from pylab import *
from scipy.interpolate import splev,interp1d
os.environ['OPENBLAS_NUM_THREADS'] = '1'

TEGap=0.01
#####thickness

thicknessx2=0.2050091764
thicknessxOffset3=0.3029833948
thicknessx3=thicknessx2+(1-thicknessx2)*thicknessxOffset3
thicknessxOffset4=0.3664161831
thicknessx4=thicknessx3+(1-thicknessx3)*thicknessxOffset4

#thicknessList = numpy.array([[ 0.,  0],
#[ 0.,  0.0581612997],
#   [ thicknessx2,  0.0270721757],
#   [ thicknessx3,  0.03409493902],
#   [ thicknessx4,  0.1923609404],
#   [ 1,   TEGap/2.]])

## TE LE Symmetry
thicknessList = numpy.array([[ 0.,  .05],
[ 0.,  0.0581612997],
   [ thicknessx2/2,  0.0270721757],
   [ thicknessx3/2,  0.03409493902],
   [ thicknessx4/2,  0.1923609404],
   [ 1-thicknessx4/2,  0.1923609404],
   [ 1-thicknessx3/2,  0.03409493902],
   [ 1-thicknessx2/2,  0.0270721757],
[ 1.,  0.0581612997],
   [ 1,   TEGap/2.]])

thicknessList[:,1]+=.05

deg=len(thicknessList)-1###to reproduce bezier curve behavior

t = numpy.array([0]*deg + list(range(len(thicknessList)-deg+1)) + [len(thicknessList)-deg]*deg,dtype='int')
xRange=numpy.linspace(0,(len(thicknessList)-deg),100)#Parametric curve range, not actual curve !!
thickness = splev(xRange,[t,[thicknessList[:,0],thicknessList[:,1]],deg])

thicknessInterp = interp1d(*thickness)

#plot(thicknessList[:,0],thicknessList[:,1],'k--',label='Control polygon',marker='o',markerfacecolor='red')
#plot(thickness[0],thickness[1],'b',linewidth=2.0,label='B-spline curve')
#plot(numpy.linspace(0,1,100),thicknessInterp(numpy.linspace(0,1,100)),'r',linewidth=1.0,label='interp')

#show()

####camber
camberx1=0.01002785608
camberxOffset2=0.1897883398
camberx2=camberx1+(1-camberx1)*camberxOffset2
camberxOffset3=0.4894257887
camberx3=camberx2+(1-camberx2)*camberxOffset3
camberxOffset4=0.09246983033
camberx4=camberx3+(1-camberx3)*camberxOffset4

#camberList = numpy.array([[ 0.,  0],
#   [ camberx1,  0.02481887589],
#   [ camberx2,  0.1891368349],
#   [ camberx3,  0.2247985243],
#   [ camberx4,  0.2543729741],
#   [ 1,   0]])

## TE LE Symmetry
camberList = numpy.array([[ 0.,  0],
   [ camberx1/2,  0.02481887589],
   [ camberx2/2,  0.1891368349],
   [ camberx3/2,  0.2247985243],
   [ camberx4/2,  0.2543729741],
   [ 1-camberx4/2,  0.2543729741],
   [ 1-camberx3/2,  0.2247985243],
   [ 1-camberx2/2,  0.1891368349],
   [ 1-camberx1/2,  0.02481887589],
   [ 1,   0]])

camber = splev(xRange,[t,[camberList[:,0],camberList[:,1]],deg])
camberInterp = interp1d(*camber)

#### combination

#xVec=numpy.linspace(0,1,10)
baseVec=(numpy.logspace(0,1,5)-1)/18#gives log paneling
xVec=numpy.hstack((baseVec,(-baseVec+1)[-2::-1]))

extrados=numpy.array([xVec,camberInterp(xVec)+thicknessInterp(xVec)/2])
#extrados=extrados[:,1:]
extrados=extrados[:,::-1]#remove LE duplicate
intrados=numpy.array([xVec,camberInterp(xVec)-thicknessInterp(xVec)/2])

profil=numpy.hstack((extrados,intrados))
#plot(*profil)
#show()

numpy.savetxt('box0',profil.T)
