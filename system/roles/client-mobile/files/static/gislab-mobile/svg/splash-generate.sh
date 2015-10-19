#--export-area=x0:y0:x1:y1

inkscape gislab_splash_portrait.svg --export-png=port-mdpi.png -w320 -h480 --export-area=0:40:480:760
inkscape gislab_splash_portrait.svg --export-png=port-hdpi.png -w480 -h800
inkscape gislab_splash_portrait.svg --export-png=port-xhdpi.png -w720 -h1280 --export-area=15:0:465:800
inkscape gislab_splash_portrait.svg --export-png=port-xxhdpi.png -w1080 -h1920 --export-area=15:0:465:800

inkscape gislab_splash_landscape.svg --export-png=land-mdpi.png -w480 -h320 --export-area=40:0:760:480
inkscape gislab_splash_landscape.svg --export-png=land-hdpi.png -w800 -h480
inkscape gislab_splash_landscape.svg --export-png=land-xhdpi.png -w1280 -h720 --export-area=0:15:800:465
inkscape gislab_splash_landscape.svg --export-png=land-xxhdpi.png -w1920 -h1080 --export-area=0:15:800:465
