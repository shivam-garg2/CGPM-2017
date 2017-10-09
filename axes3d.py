def axes3d(edges):

	import matplotlib.pyplot as plt
	from mpl_toolkits.mplot3d import Axes3D

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	n = len(edges)
	print n

	print(edges)

	X = []
	Y = []
	Z = []

	for t in range(0,n):
		X,Y,Z = [(edges[t][0][0] , edges[t][1][0]) , (edges[t][0][1] , edges[t][1][1]) , (edges[t][0][2] , edges[t][1][2])]
		print X,Y,Z
		ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
	
	plt.axis('off')	
	plt.show()
	
