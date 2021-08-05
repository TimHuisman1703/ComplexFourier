if __name__ == "__main__":
	from math import sin, cos, pi
	from numpy import linalg as la
	import os
	from time import time

	DIRECTORY = os.path.dirname(__file__)

	timer = time()

	f = open(f"{DIRECTORY}/coords.txt")
	coords = f.read().split("\n")
	f.close()

	b = [complex(*map(float, j.split(", "))) for j in coords if j[0] != "#"]

	n = len(b)
	offset = -n // 2

	A = []
	for i in range(offset, offset+n):
		A.append([complex(cos(2*pi * i * j / n), sin(2*pi * i * j / n)) for j in range(n)])

	lengths = la.solve(A, b)

	f = open(f"{DIRECTORY}/lengths.txt", "w")
	f.write("\n".join(f"{j.real}, {j.imag}" for j in lengths))
	f.close()

	print("\nDone solving!")
	print(f"Execution time: {time() - timer:.3f}s")