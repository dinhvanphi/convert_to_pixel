# convert_to_pixel

Convert an input image (`jpg`, `png`, ...) into a pixel-art style image.

## Usage

```bash
python /home/runner/work/convert_to_pixel/convert_to_pixel/convert_to_pixel.py /path/to/input.jpg
```

Optional arguments:

- `-o, --output`: output file path
- `-p, --pixel-size`: block size for pixelation (default `12`)

Example:

```bash
python /home/runner/work/convert_to_pixel/convert_to_pixel/convert_to_pixel.py ./photo.jpg -o ./photo_pixel.png -p 16
```
