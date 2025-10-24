import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt

#        1 +--------------------------------------------------------------------+
#          |                           *****     ****                           |
#          |                       **** (0.5,ytop1)  *****                      |
#          |                  *****                       ****                  |
#      0.8 |             *****              *****             *****             |
#          |         ****               ****     ****              ****         |
#      (xtop,ytop2)***               ****           ****              ***(1-xtop,ytop2)
#          |      *             ****     (0.5,ybot2)     ****             *     |
#      0.6 |     *          ****                             ****         *     |
#          |     *       ***                                     **        *    |
#          |    *       * (xbot,ybot1)             (1-xbot,ybot1 ) *       *    |
#          |    *     **                                            **      *   |
#      0.4 |   *     *                                                *     *   |
#          |   *    *                                                  *     *  |
#          |  *    *                                                    **   *  |
#          |  *  **                                                       *   * |
#      0.2 | *  *                                                          *  * |
#          | * *                                                            *  *|
#          |***                                                              ***|
#    (0,0) |*                                                                  *|(1,0)
#        0 +--------------------------------------------------------------------+
#          0            0.2           0.4          0.6           0.8            1

xtop={xtop}#.2#absolute
xbot={xbot}*(0.5-xtop)+xtop#.01+xtop#absolute

ytop1=1#absolute
ytop2={ytop2}*ytop1#.8*ytop1#relative
ybot1={ybot1}*ytop2#.7*ytop2#relative
ybot2={ybot2}*(ytop1-ybot1)+ybot1#.5*(ytop1-ybot1)+ybot1#relative

ytop1Thick={ytop1Thick}#0.35

#x = np.array([0,  xtop,    .5, 1-xtop, 1,1-xbot,    .5,  xbot, 0])
#y = np.array([0, ytop2, ytop1,  ytop2, 0, ybot1, ybot2, ybot1, 0])

x = np.array([1, 1-xtop,    .5,  xtop,0, xbot,    .5, 1-xbot, 1])
y = np.array([0,  ytop2, ytop1, ytop2,0,ybot1, ybot2,  ybot1, 0])

# fit splines to x=f(u) and y=g(u), treating both as periodic. also note that s=0
# is needed in order to force the spline fit to pass through all the input points.
tck, u = interpolate.splprep([x, y], s=0, per=True)

# evaluate the spline fits for 1000 evenly spaced distance values
xi, yi = interpolate.splev(np.linspace(0, 1, 1000), tck)

yi*=ytop1Thick

profil=np.vstack((xi,yi))

np.savetxt('profile0',profil.T)

#plot the result
fig, ax = plt.subplots(1, 1)
#ax.plot(x, y, 'or')
ax.plot(xi, yi, '-b')

### BOX
offset=.2
x = np.array([1+offset/2, 1-xtop+offset,    .5,  xtop-offset,-offset/2,offset/2, xbot+offset,    .5, 1-xbot-offset, 1-offset/2,1+offset/2])
y = np.array([-offset/10,  ytop2+offset, ytop1+offset, ytop2+offset,-offset/10,-offset/10,ybot1-offset, ybot2-offset,  ybot1-offset, -offset/10,-offset/10])

# fit splines to x=f(u) and y=g(u), treating both as periodic. also note that s=0
# is needed in order to force the spline fit to pass through all the input points.
tck, u = interpolate.splprep([x, y], u=np.linspace(0,1,len(x)), s=0, per=True)

# evaluate the spline fits for 1000 evenly spaced distance values
#xi, yi = interpolate.splev(np.linspace(0, 1, 21), tck)

xi, yi = interpolate.splev([0. , 0.05 , 0.1 , 0.15, 0.2 , 0.25, 0.3 , 0.35, 0.4 , 0.5 ,0.55 , 0.6 , 0.65, 0.7 , 0.75, 0.8 , 0.85, 0.9 , 1.  ], tck)
yi*=ytop1Thick

ax.plot(xi, yi, 'or')
ax.plot(xi, yi, '-b')

box=np.vstack((xi,yi))

ax.plot(*profil, '-b')
ax.plot(*box, '-b')
ax.set_aspect('equal', adjustable='box')
#plt.show()

np.savetxt('box0',box.T[:-1])

#import termplotlib as tpl
#fig= tpl.figure()
#fig.plot(x, y, 'o')
#fig.show()




