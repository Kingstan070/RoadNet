def save_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)

def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def delete_file(file_path):
    import os
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("The file does not exist")