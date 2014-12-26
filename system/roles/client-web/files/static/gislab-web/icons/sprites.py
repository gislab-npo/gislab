import os
import shutil
import subprocess

import Image


dpi = 90

base_dir = os.path.dirname(os.path.abspath(__file__))
svg_dir = os.path.join(base_dir, 'svg')
png_dir = os.path.join(base_dir, 'tmp')


if not os.path.exists(png_dir):
	os.mkdir(png_dir)

def add_icon(filename, x, y):
	png_file = os.path.join(png_dir, "%s.png" % os.path.splitext(filename)[0])
	subprocess.call("inkscape %s --export-png=%s -d %d" % (os.path.join(svg_dir, filename), png_file, dpi), shell=True)
	img = Image.open(png_file)
	image.paste(img, (x, y))



image = Image.new("RGBA", (72, 72))
add_icon("zoom_extent.svg", 0, 0)
add_icon("zoom_previous.svg", 24, 0)
add_icon("zoom_next.svg", 48, 0)
add_icon("draw.svg", 0, 24)
add_icon("search.svg", 24, 24)
add_icon("identification.svg", 48, 24)
add_icon("print.svg", 0, 48)
add_icon("measure.svg", 24, 48)
add_icon("topics.svg", 48, 48)

image.save(os.path.join(base_dir, "buttons-toolbar-color.png"), "png")


image = Image.new("RGBA", (72, 72))
add_icon("zoom_extent_bw.svg", 0, 0)
add_icon("zoom_previous_bw.svg", 24, 0)
add_icon("zoom_next_bw.svg", 48, 0)
add_icon("draw_bw.svg", 0, 24)
add_icon("search_bw.svg", 24, 24)
add_icon("identification_bw.svg", 48, 24)
add_icon("print_bw.svg", 0, 48)
add_icon("measure_bw.svg", 24, 48)
add_icon("topics_bw.svg", 48, 48)

image.save(os.path.join(base_dir, "buttons-toolbar-gray.png"), "png")


image = Image.new("RGBA", (40, 40))
add_icon("modify_bw.svg", 0, 0)
add_icon("modify.svg", 20, 0)
add_icon("snapping_bw.svg", 0, 20)
add_icon("snapping.svg", 20, 20)

image.save(os.path.join(base_dir, "buttons-drawing.png"), "png")


shutil.rmtree(png_dir)
