ACCURACY = 5
LINE_THICKNESS = 4
VIDEO_RENDER = True
VECTOR_RENDER = True

if __name__ == "__main__":
	import cairo
	import cv2
	from math import sin, cos, sqrt, pi
	import os
	from plot import WIDTH, HEIGHT
	from shutil import rmtree
	from time import time

	DIRECTORY = os.path.dirname(__file__)

	timer = time()

	f = open(f"{DIRECTORY}/lengths.txt")
	lengths = [tuple(map(float, j.split(", "))) for j in f.read().split("\n")]
	f.close()

	f = open(f"{DIRECTORY}/coords.txt")
	coords = [tuple(map(float, j.split(", "))) for j in f.read().split("\n")]
	f.close()

	n = len(lengths)
	offset = -n // 2
	size = ACCURACY * n
	start = -size // 2

	def get_coords(lengths, phase):
		x = y = 0

		for i in range(offset, offset+n):
			x += cos(phase * i) * lengths[i][0] - sin(phase * i) * lengths[i][1]
			y += sin(phase * i) * lengths[i][0] + cos(phase * i) * lengths[i][1]
		
		return x, y

	if VIDEO_RENDER:
		if os.path.exists(f"{DIRECTORY}/frames"):
			rmtree(f"{DIRECTORY}/frames")
		os.mkdir(f"{DIRECTORY}/frames")
		
		print("\nRendering frames...")
	else:
		print("\nDrawing SVG...")

	with cairo.SVGSurface(f"{DIRECTORY}/out.svg", WIDTH, HEIGHT) as surface:
		con = cairo.Context(surface)

		con.set_source_rgb(0.129, 0.392, 0.612)
		con.rectangle(0, 0, WIDTH, HEIGHT)
		con.fill()

		con.set_source_rgb(1.0, 1.0, 1.0)
		con.set_line_width(LINE_THICKNESS)

		sx, sy = x, y = get_coords(lengths, (start * 2*pi) / size)

		if VIDEO_RENDER:
			con.arc(x, y, LINE_THICKNESS / 2, 0, 2*pi)
			con.fill()

			surface.write_to_png(f"{DIRECTORY}/frames/trace_0000.png")

		for i in range(1, size):
			con.move_to(x, y)
			x, y = get_coords(lengths, ((i + start) * 2*pi) / size)
			con.line_to(x, y)
			con.stroke()

			con.arc(x, y, LINE_THICKNESS / 2, 0, 2*pi)
			con.fill()
			
			if VIDEO_RENDER:
				surface.write_to_png(f"{DIRECTORY}/frames/trace_{i:04d}.png")
				
				if i % 50 == 49:
					print(f"{i+1}/{size+1}")
		
		con.move_to(x, y)
		con.line_to(sx, sy)
		con.stroke()
		
		if VIDEO_RENDER:
			surface.write_to_png(f"{DIRECTORY}/frames/trace_{size:04d}.png")

			print(f"{size+1}/{size+1}")
		else:
			con.set_source_rgb(1.0, 0.0, 0.0)
			for p in coords:
				con.arc(p[0], p[1], LINE_THICKNESS / 2, 0, 2*pi)
				con.fill()
	
	if VIDEO_RENDER and VECTOR_RENDER:
		print("\nRendering vectors...")

		vector_order = []
		j = 1
		while -j >= offset:
			vector_order.append(-j)
			if j < offset + n:
				vector_order.append(j)
			j += 1

		for i in range(size + 1):
			with cairo.SVGSurface(f"{DIRECTORY}/temp.svg", WIDTH, HEIGHT) as surface:
				con = cairo.Context(surface)
				
				con.set_source_rgb(0.0, 0.0, 0.0)
				con.rectangle(0, 0, WIDTH-1, HEIGHT-1)
				con.fill()

				phase = ((i + start) * 2*pi) / size
				x, y = lengths[0][0], lengths[0][1]
				
				con.set_source_rgb(0.15, 0.15, 0.15)

				points = [None for _ in range(len(vector_order) + 1)]
				points[0] = (x, y)

				for j in range(len(vector_order)):
					rot = vector_order[j]
					dx = cos(phase * rot) * lengths[rot][0] - sin(phase * rot) * lengths[rot][1]
					dy = sin(phase * rot) * lengths[rot][0] + cos(phase * rot) * lengths[rot][1]
					length = sqrt(dx * dx + dy * dy)
					
					con.arc(x, y, length, 0, 2*pi)
					con.stroke()
					
					points[j+1] = (x + dx, y + dy)

					x += dx
					y += dy
				
				con.set_source_rgb(0.4, 0.4, 0.4)

				x, y = points[0]
				
				con.arc(x, y, LINE_THICKNESS, 0, 2*pi)
				con.fill()
				con.stroke()

				for j in range(1, len(points)):
					nx, ny = points[j]
					
					con.move_to(x, y)
					con.line_to(nx, ny)
					con.stroke()

					x, y = nx, ny

				surface.write_to_png(f"{DIRECTORY}/frames/vectors_{i:04d}.png")
			
			if i % 10 == 9 or i == size:
				print(f"{i+1}/{size+1}")
		
		os.remove(f"{DIRECTORY}/temp.svg")

	if VIDEO_RENDER:
		first_frame = cv2.imread(f"{DIRECTORY}/frames/trace_0000.png")

		video = cv2.VideoWriter(f"{DIRECTORY}/out.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 60, (WIDTH, HEIGHT))

		print("\nWriting frames to video...")
		for i in range(size+1):
			img = cv2.imread(f"{DIRECTORY}/frames/trace_{i:04d}.png")
			
			if VECTOR_RENDER:
				img_vectors = cv2.imread(f"{DIRECTORY}/frames/vectors_{i:04d}.png")
				img = cv2.addWeighted(img, 1.0, img_vectors, 1.0, 0)

			if i == 0:
				for _ in range(60):
					video.write(img)
			elif i == size:
				for _ in range(90):
					video.write(img)
			else:
				video.write(img)

			if i % 50 == 49 or i == size:
				print(f"{i+1}/{size+1}")

		cv2.destroyAllWindows()
		video.release()

		print("\nCleaning up files...")
		if os.path.exists(f"{DIRECTORY}/frames"):
			rmtree(f"{DIRECTORY}/frames")

	print("\nDone rendering!")
	print(f"Lines: {size}")
	print(f"Execution time: {time() - timer:.3f}s")