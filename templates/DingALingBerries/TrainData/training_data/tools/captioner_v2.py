import os
import sys

def create_caption_files(directory, keyword, image_extensions=None, video_extensions=None):
    if image_extensions is None:
        # Default image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    if video_extensions is None:
        # Default video extensions
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']

    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # Iterate through all files in the directory and its first-level subdirectories
    for root, _, files in os.walk(directory):
        # Limit to one level of recursion (parent and its first-level subdirectories)
        if root != directory and os.path.relpath(root, directory).count(os.sep) > 1:
            continue

        for filename in files:
            file_lower = filename.lower()
            if any(file_lower.endswith(ext) for ext in image_extensions + video_extensions):
                # Create the corresponding text file
                base_name, _ = os.path.splitext(filename)
                txt_filename = f"{base_name}.txt"
                txt_path = os.path.join(root, txt_filename)

                try:
                    with open(txt_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(keyword)
                    print(f"Created: {txt_path}")
                except Exception as e:
                    print(f"Failed to create {txt_filename}: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_captions.py <directory_path> <keyword>")
        print("Example: python create_captions.py \"C:\\Media\" \"keyword\"")
        sys.exit(1)

    directory = sys.argv[1]
    keyword = sys.argv[2]

    create_caption_files(directory, keyword)

if __name__ == "__main__":
    main()
