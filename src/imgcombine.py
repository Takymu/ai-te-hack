from PIL import Image
import io
import math

def combine_images_to_file(image_bytes_list: list[bytes], output_path: str) -> None:
    first_image = Image.open(io.BytesIO(image_bytes_list[0]))
    width, height = first_image.size
    num_images = len(image_bytes_list)
    num_rows = math.ceil(num_images / 2)
    output_width = width * 2
    output_height = height * num_rows
    result_image = Image.new('RGB', (output_width, output_height), color='white')
    
    for i, img_bytes in enumerate(image_bytes_list):
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        row = i // 2
        col = i % 2
        if i == num_images - 1 and num_images % 2 == 1:
            x_offset = width // 2
        else:
            x_offset = col * width
        y_offset = row * height
        result_image.paste(img, (x_offset, y_offset))
    
    result_image.save(output_path, format='PNG')