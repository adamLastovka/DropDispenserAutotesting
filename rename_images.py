import os

if __name__ == "__main__":
    directory = r'C:\Users\lasto\OneDrive - University of Waterloo\Desktop\Cornell\DropDispensing\Images\AT-FirstDrop-2.5Bar-3'

    # Get a list of all jpeg files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.JPG')]

    # Sort the files to ensure the order is maintained
    files.sort()

    # Rename each file
    for i, filename in enumerate(files):
        # Define the new filename
        new_filename = f"IMG_{i + 1:04}.JPG"

        # Get the full path for the old and new filenames
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)

        # Rename the file
        os.rename(old_file, new_file)
        print(f"Renamed {filename} to {new_filename}")