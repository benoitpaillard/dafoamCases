import os,numpy

os.system("csplit -z deformedFFD.dat /Zone/ '{*}'")

main=numpy.loadtxt('xx01',skiprows=2)
main=main[:int(len(main)/2)]

mainExtrados=main[:int(len(main)/2)]
mainIntrados=main[int(len(main)/2):]

weightTip=0.9

mainTEx=weightTip*(mainExtrados[0,0]+mainIntrados[0,0])/2 +(1-weightTip)*(mainExtrados[1,0]+mainIntrados[1,0])/2
mainTEy=weightTip*(mainExtrados[0,1]+mainIntrados[0,1])/2 +(1-weightTip)*(mainExtrados[1,1]+mainIntrados[1,1])/2

mainLEx=weightTip*(mainExtrados[-1,0]+mainIntrados[-1,0])/2+(1-weightTip)*(mainExtrados[-2,0]+mainIntrados[-2,0])/2
mainLEy=weightTip*(mainExtrados[-1,1]+mainIntrados[-1,1])/2+(1-weightTip)*(mainExtrados[-2,1]+mainIntrados[-2,1])/2

numpy.savetxt('LEconsMain',[mainLEx,mainLEy,0])
numpy.savetxt('TEconsMain',[mainTEx,mainTEy,0])

flap=numpy.loadtxt('xx03',skiprows=2)
flap=flap[:int(len(flap)/2)]

flapExtrados=flap[:int(len(flap)/2)]
flapIntrados=flap[int(len(flap)/2):]

flapTEx=weightTip*(flapExtrados[0,0]+flapIntrados[0,0])/2 +(1-weightTip)*(flapExtrados[1,0]+flapIntrados[1,0])/2
flapTEy=weightTip*(flapExtrados[0,1]+flapIntrados[0,1])/2 +(1-weightTip)*(flapExtrados[1,1]+flapIntrados[1,1])/2

flapLEx=weightTip*(flapExtrados[-1,0]+flapIntrados[-1,0])/2 +(1-weightTip)*(flapExtrados[-2,0]+flapIntrados[-2,0])/2
flapLEy=weightTip*(flapExtrados[-1,1]+flapIntrados[-1,1])/2 +(1-weightTip)*(flapExtrados[-2,1]+flapIntrados[-2,1])/2

numpy.savetxt('LEconsFlap',[flapLEx,flapLEy,0])
numpy.savetxt('TEconsFlap',[flapTEx,flapTEy,0])
