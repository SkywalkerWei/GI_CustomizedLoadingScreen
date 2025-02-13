import os
import glob
import subprocess
from PIL import Image, ImageDraw
from PIL import ImageFilter
from PIL import ImageEnhance
from typing import Tuple
import numpy as np

def apply_effect(image: Image, resolution: Tuple[int, int], crop_mode: str) -> Image:
    """
    Args:
        image: Source image
        resolution: Target resolution (width, height)
        crop_mode: Either 'crop' for cropping or 'letterbox' for adding bars
    """
    width, height = image.size
    target_width, target_height = resolution
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height

    if crop_mode == 'crop':
        # Crop the image to match target aspect ratio
        if aspect_ratio > target_aspect_ratio:
            # Image is wider than target - crop sides
            new_width = int(height * target_aspect_ratio)
            left = (width - new_width) // 2
            image = image.crop((left, 0, left + new_width, height))
        else:
            # Image is taller than target - crop top/bottom
            new_height = int(width / target_aspect_ratio)
            top = (height - new_height) // 2
            image = image.crop((0, top, width, top + new_height))
        
        # Resize to target resolution
        image = image.resize(resolution, Image.BICUBIC)
    else:  # letterbox mode
        if aspect_ratio > target_aspect_ratio:
            # Image is wider than target resolution
            new_height = int(target_width / aspect_ratio)
            image = image.resize((target_width, new_height))
            offset = (0, (target_height - new_height) // 2)
        else:
            # Image is taller than target resolution
            new_width = int(target_height * aspect_ratio)
            image = image.resize((new_width, target_height))
            offset = ((target_width - new_width) // 2, 0)

        # Add bars
        background = Image.new("RGBA", resolution, (0,0,0,1))
        background.paste(image, offset)
        # Create Gaussian Blur
        background = background.filter(ImageFilter.GaussianBlur(radius=min(width,height)/8))
        background.paste(image, offset)
        image = background

    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image = image.convert('RGBA')
    color_layer = Image.new("RGBA", resolution, color_avg(image))
    composite = Image.alpha_composite(color_layer, image)
    return composite

def color_avg(image: Image) -> Tuple[int, int, int]:
    pixels = np.array(image)
    return tuple(map(int, np.average(pixels, axis=(0, 1))))

# Read the configuration file
config_file = "config.ini"
with open(config_file, 'r') as f:
    lines = f.read().splitlines()
    target_resolution = tuple(map(int, lines[0].split(',')))
    input_dir = lines[1]
    output_dir = lines[2]
    ini_file = lines[3]
    # Option for crop mode, default to letterbox
    crop_mode = lines[4] if len(lines) > 4 else 'letterbox'
    if crop_mode not in ['crop', 'letterbox']:
        print(f"Warning: Invalid crop mode '{crop_mode}', defaulting to 'letterbox'")
        crop_mode = 'letterbox'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get a list of all images in the input directory
input_files = glob.glob(input_dir + '/**/*.*', recursive=True)
input_files = [file for file in input_files if '\\-' not in file]
output_files_dds = []

# Iterate over the input files
for input_file in input_files:
    should_refresh = True
    output_file, ext = os.path.splitext(input_file)
    output_file = os.path.join(output_dir, os.path.basename(output_file))
    output_file_png = output_file + ".png"
    output_file_dds = output_file + ".dds"
    output_files_dds.append(output_file_dds)

    # Check if the output file already exists and if the input file has been modified
    if os.path.isfile(output_file_dds):
        input_mtime = os.path.getmtime(input_file)
        output_mtime = os.path.getmtime(output_file_dds)
        should_refresh = input_mtime >= output_mtime

    if should_refresh:
        im = Image.open(input_file)
        im = apply_effect(image=im, resolution=target_resolution, crop_mode=crop_mode)
        im.save(output_file_png, 'PNG', srgb=False)
        subprocess.run(["texconv.exe", "-f", "BC7_UNORM", "-y", "-sepalpha", "-srgb", "-m", "1", "-o", output_dir, output_file_png])
        os.remove(output_file_png)

# Update ini file
with open(ini_file, "r") as f:
    ini_lines = f.readlines()
with open(ini_file, "w") as f:
    for line in ini_lines:
        if line.startswith("global $n_imgs"):
            line = f"global $n_imgs = {len(input_files)}\n"
        f.write(line)
        if line.startswith(";BEGIN_SCRIPT_GENERATED_SECTION"):
            break
    for i in range(len(input_files)):
        f.write(f"else if $is_load_prev && $curr_img == {i}\n")
        f.write(f"	this = ResourceLS.{i}\n")
    f.write("endif\n")
    f.write("endif\n")
    for i, output_file_dds in enumerate(output_files_dds):
        f.write(f"[ResourceLS.{i}]\n")
        output_file_dds_windows = output_file_dds.replace('/', '\\')
        f.write(f"filename = {output_file_dds_windows}\n")
