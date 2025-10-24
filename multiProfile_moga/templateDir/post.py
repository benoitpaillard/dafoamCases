import subprocess,numpy

try:
	cls=[float(x) for x in subprocess.getoutput("grep -r \"'scenario1.aero_post.functionals.CL'\" logOpt* | tr -s ' ' | cut -d '[' -f 2 | sed 's/...$//'").split()]
	cd=float(subprocess.getoutput("grep -r CD logOpt* | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 2"))
	cl=-max(cls)
	numpy.savetxt('results.tmp',[cl,cd])
except:
	numpy.savetxt('results.tmp',[0,0])
	print('bite')
