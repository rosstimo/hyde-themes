import re
import os
import argparse
import logging
import mimetypes

def extract_colors(css_content):
    # Regular expressions for different color formats
    hex_pattern = r'#[0-9a-fA-F]{3,8}'
    rgba_pattern = r'rgba?\(([^)]+)\)'  # Matches rgba(anything)
    hex_rgba_pattern = r'0x[0-9a-fA-F]{8}'
    
    # Find all matches
    hex_colors = re.findall(hex_pattern, css_content)
    rgba_colors = re.findall(rgba_pattern, css_content)
    hex_rgba_colors = re.findall(hex_rgba_pattern, css_content)
    
    # Combine all colors and remove duplicates
    all_colors = set(hex_colors + 
                     [f'rgba({color})' for color in rgba_colors] + 
                     hex_rgba_colors)
    
    return all_colors

def process_file(file_path):
    with open(file_path, 'r') as file:
        css_content = file.read()
    return extract_colors(css_content)

def is_text_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is None or mime_type.startswith('text/'), mime_type
    # return mime_type is not None and mime_type.startswith('text/'), mime_type

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract unique color codes from a text file or directory.")
    parser.add_argument('input_path', help="Path to the input text file or directory")
    parser.add_argument('output_file', help="Path to the output file where unique colors will be listed")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Increase output verbosity (e.g., -v, -vv, -vvv)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = log_levels[min(len(log_levels) - 1, args.verbose)]
    logging.basicConfig(level=log_level, format='%(message)s')
    
    colors_by_file = {}
    
    if os.path.isdir(args.input_path):
        logging.info(f"Processing directory: {args.input_path}")
        # Traverse the directory tree
        for root, _, files in os.walk(args.input_path):
            for file in files:
                file_path = os.path.join(root, file)
                is_text, mime_type = is_text_file(file_path)
                if is_text:
                    logging.debug(f"Processing file: {file_path} (MIME type: {mime_type})")
                    try:
                        colors_by_file[file_path] = process_file(file_path)
                    except Exception as e:
                        logging.error(f"Error processing file {file_path}: {e}")
                else:
                    logging.debug(f"Skipping file: {file_path} (MIME type: {mime_type})")
    else:
        is_text, mime_type = is_text_file(args.input_path)
        if is_text:
            logging.info(f"Processing file: {args.input_path} (MIME type: {mime_type})")
            try:
                # Process a single file
                colors_by_file[args.input_path] = process_file(args.input_path)
            except Exception as e:
                logging.error(f"Error processing file {args.input_path}: {e}")
        else:
            logging.error(f"The file {args.input_path} is not a text file (MIME type: {mime_type}).")
            return
    
    # Write unique colors to the output file, organized by file path
    with open(args.output_file, 'w') as file:
        for file_path, colors in colors_by_file.items():
            file.write(f"File: {file_path}\n")
            for color in colors:
                file.write(f"  {color}\n")
            file.write("\n")
    
    logging.info(f"Unique colors have been written to {args.output_file}")

if __name__ == "__main__":
    main()

