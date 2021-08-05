COMPASS = "eswn"

LINE_DENSITY = 3
ARC_DENSITY = 6

WIDTH = 1920
HEIGHT = 1080
SCALE = 40

if __name__ == "__main__":
	from math import sin, cos, pi
	import os
	from time import time

	DIRECTORY = os.path.dirname(__file__)

	timer = time()

	f = open(f"{DIRECTORY}/directions.txt")
	directions = [j for j in f.read().split("\n") if j != "" and j[0] != "#"]
	f.close()

	x = y = 0
	points = [(x, y)]

	for dir in directions:
		args = dir.split()

		if args[0] == "left":
			dist = float(args[1])
			density = int(args[2]) if len(args) > 2 else LINE_DENSITY

			for i in range(1, round(dist * density + 1)):
				points.append((x - i / density, y))

			x -= dist
		elif args[0] == "right":
			dist = float(args[1])
			density = int(args[2]) if len(args) > 2 else LINE_DENSITY

			for i in range(1, round(dist * density + 1)):
				points.append((x + i / density, y))

			x += dist
		elif args[0] == "up":
			dist = float(args[1])
			density = int(args[2]) if len(args) > 2 else LINE_DENSITY

			for i in range(1, round(dist * density + 1)):
				points.append((x, y - i / density))

			y -= dist
		elif args[0] == "down":
			dist = float(args[1])
			density = int(args[2]) if len(args) > 2 else LINE_DENSITY

			for i in range(1, round(dist * density + 1)):
				points.append((x, y + i / density))

			y += dist
		elif args[0] == "arc":
			start, end, clockwise, radius = args[1], args[2], args[3] == ">", float(args[4])
			density = int(args[5]) if len(args) > 5 else ARC_DENSITY

			cx = x + radius * (int(start == "w") - int(start == "e"))
			cy = y + radius * (int(start == "n") - int(start == "s"))

			pos = COMPASS.index(start) + 4

			while COMPASS[pos % 4] != end:
				for i in range(1, round(density * radius + 1)):
					angle = pi / 2 * (pos + (2 * clockwise - 1) * i / (density * radius))
					points.append((cx + radius * cos(angle), cy + radius * sin(angle)))

				pos += 2 * clockwise - 1
			
			x = cx + radius * (int(end == "e") - int(end == "w"))
			y = cy + radius * (int(end == "s") - int(end == "n"))

	min_x = min_y = max_x = max_y = 0
	for p in points:	
		if p[0] < min_x:
			min_x = p[0]
		if p[0] > max_x:
			max_x = p[0]
		if p[1] < min_y:
			min_y = p[1]
		if p[1] > max_y:
			max_y = p[1]

	margin = ((WIDTH / SCALE - max_x + min_x) // 2, (HEIGHT / SCALE - max_y + min_y) // 2)

	points = [(j[0] - min_x + margin[0], j[1] - min_y + margin[1]) for j in points[:-1]]

	f = open(f"{DIRECTORY}/coords.txt", "w")
	f.write("\n".join(f"{float(p[0] * SCALE)}, {float(p[1] * SCALE)}" for p in points))
	f.close()

	print("\nDone plotting!")
	print(f"Points: {len(points)}")
	print(f"Execution time: {time() - timer:.3f}s")