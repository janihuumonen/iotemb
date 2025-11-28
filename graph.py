import numpy as np
import matplotlib.pyplot as plt

def readcsv(fn):
	with open(fn) as f:
		lx,ly = f.readline().strip().split(',')
		x,y = map(np.array, list(zip( *[list(map(float, l.strip().split(','))) for l in f.readlines() if l.strip()!=''] )))
	return x,y,lx,ly

def linefit(x,y):
	A = np.stack([x,np.ones(len(x))]).T
	m,c = np.linalg.lstsq(A,y,rcond=None)[0]
	return m,c
'''
# convert from adc values to voltage
with open('meas-ntc.csv') as f:
	header = f.readline()
	r = [ l.strip().split(',') for l in f.readlines() if l.strip()!='' ]
with open('meas-ntc-v.csv','w') as f:
	f.write(header)
	f.writelines([t'+','+str( int(v)*3.3025/pow(2,16) )+'\n' for t,v in r])
'''
#x = np.array([1.51,1.56,1.61,1.66,1.70,1.74,1.78])
#y = np.array([0,1,2,3,4,5,6])

#k = (5000-50)/(300*np.pi/180) # ohms/rad
#I = 3.3/5000 # volts/ohm
#tm = k*I # volts/rad
#print(k,I,tm)

x,y,lx,ly = readcsv('meas-ntc-v.csv')
#y = y*3.3025/pow(2,16)
m,c = linefit(x,y)

#ys = np.linspace(0,20.5,600) # start, stop, num_of_points
#xs = tm * np.arcsin([h/20.5 for h in ys])
#plt.plot(ys,xs,'-.', label='Sinusoidal')

yg = m*x+c
plt.plot(x,yg,'-', label='Least squares fitted')
#xg = (y - c) / m
#plt.plot(xg,y,'-.', label='Lineaarinen approksimaatio')
#print(xg)

plt.plot(x,y,'o', label='Measurements')
plt.xlabel(lx)
plt.ylabel(ly)
plt.legend(loc='upper left')
#plt.title('Test results')
plt.show()
print(m,c)

'''
x_ = sum(x)/len(x)
y_ = sum(y)/len(y)
m = sum( (x-x_)*(y-y_) ) / sum( (x-x_)**2 )
c = y_ - m * x_
print(
m,c
)
'''
