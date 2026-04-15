from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def generate_bright_colored_ascii(
    input_path, 
    output_path, 
    cols=150, 
    bg_color=(0, 0, 0), 
    bg_alpha=255,               
    char_cluster="@%#*+os=c~",   
    dark_threshold=5,              # Fully replaced by dark_text_color below this
    fade_threshold=40,             # NEW: Blends colors between dark_threshold and fade_threshold
    dark_text_color=(33, 40, 48)   
):
    try:
        image = Image.open(input_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    ascii_chars = char_cluster
    
    font = ImageFont.load_default() 

    char_bbox = font.getbbox("A")
    char_width = char_bbox[2] - char_bbox[0]
    char_height = char_bbox[3] - char_bbox[1] + 2 

    orig_width, orig_height = image.size
    image_aspect_ratio = orig_height / orig_width
    font_aspect_ratio = char_width / char_height
    rows = int(cols * image_aspect_ratio * font_aspect_ratio)

    resized_image = image.resize((cols, rows), Image.Resampling.LANCZOS)

    # Boost Brightness and Contrast
    enhancer_brightness = ImageEnhance.Brightness(resized_image)
    resized_image = enhancer_brightness.enhance(1.5) 
    
    enhancer_contrast = ImageEnhance.Contrast(resized_image)
    resized_image = enhancer_contrast.enhance(1.2)

    out_width = cols * char_width
    out_height = rows * char_height
    
    # Create the RGBA canvas
    rgba_bg_color = (bg_color[0], bg_color[1], bg_color[2], bg_alpha)
    output_image = Image.new('RGBA', (out_width, out_height), color=rgba_bg_color)
    draw = ImageDraw.Draw(output_image)

    for y in range(rows):
        for x in range(cols):
            # 1. Get original pixel color
            r, g, b = resized_image.getpixel((x, y))
            
            # 2. Calculate true brightness (luminance) of that pixel
            luminance = int(0.299 * r + 0.587 * g + 0.114 * b)
            
            # 3. COLOR OVERRIDE & FADING:
            if luminance <= dark_threshold:
                # If very dark, force the custom background color
                r, g, b = dark_text_color
                
            elif luminance < fade_threshold:
                # If it's in the "fade zone", smoothly blend the original color and the dark color
                # Calculate a ratio from 0.0 (near dark_threshold) to 1.0 (near fade_threshold)
                ratio = (luminance - dark_threshold) / max(1, (fade_threshold - dark_threshold))
                
                # Blend each color channel
                r = int(dark_text_color[0] + (r - dark_text_color[0]) * ratio)
                g = int(dark_text_color[1] + (g - dark_text_color[1]) * ratio)
                b = int(dark_text_color[2] + (b - dark_text_color[2]) * ratio)
            
            # 4. Map luminance to the character cluster array
            char_index = int((luminance / 255.0) * (len(ascii_chars) - 1))
            char = ascii_chars[char_index]
            
            # 5. Draw the text
            draw.text((x * char_width, y * char_height), char, font=font, fill=(r, g, b, 255))

    if output_path.lower().endswith(('.jpg', '.jpeg')) and bg_alpha < 255:
        print("Warning: JPEGs do not support transparency. Converting to solid background before saving.")
        output_image = output_image.convert('RGB')

    output_image.save(output_path)
    print(f"Colored ASCII art successfully saved to {output_path}")


if __name__ == "__main__":
    
    generate_bright_colored_ascii(
        input_path="38723483131-68161a6f69-o.jpg", 
        output_path="nebula.png", 
        cols=150, 
        
        bg_color=(33, 40, 48),        
        bg_alpha=255,                
        
        char_cluster="@%#*+os=c~", 
        
        # --- FADING CONTROLS ---
        # Pixels at 5 or below will be exactly (33, 40, 48)
        dark_threshold=5,         
        
        # Pixels between 6 and 50 will smoothly blend into the background color. 
        # Increase this to make the fading effect wider and softer!
        fade_threshold=50, 
        
        dark_text_color=(33, 40, 48) 
    )