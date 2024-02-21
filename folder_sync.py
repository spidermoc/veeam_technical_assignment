import os
import shutil
import argparse
import time


def sync_folders(source_folder, replica_folder, log_file):
    # Check if source folder exists
    if not os.path.exists(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    # Create replica folder if it doesn't exist
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    # Synchronize folders
    for root, dirs, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        replica_path = os.path.join(replica_folder, relative_path)

        # Create directories in replica if not exist
        for dir_name in dirs:
            source_dir = os.path.join(root, dir_name)
            replica_dir = os.path.join(replica_path, dir_name)

            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                log(f"Created directory: {replica_dir}")

        # Copy files to replica folder if there is a change
        for file_name in files:
            source_file = os.path.join(root, file_name)
            replica_file = os.path.join(replica_path, file_name)

            if os.path.exists(replica_file):
                source_mtime = os.path.getmtime(source_file)
                replica_mtime = os.path.getmtime(replica_file)

                if source_mtime != replica_mtime:
                    os.remove(replica_file)
                    shutil.copy2(source_file, replica_file)
                    log(log_file, f"Updated file: {replica_file}")
                else:
                    log(log_file, f"No change in file: {replica_file}")
            else:
                shutil.copy2(source_file, replica_file)
                log(log_file, f"Copied file: {replica_file}")

    # Remove extra files in replica folder
    for root, dirs, files in os.walk(replica_folder):
        relative_path = os.path.relpath(root, replica_folder)
        source_path = os.path.join(source_folder, relative_path)

        for file_name in files:
            replica_file = os.path.join(root, file_name)
            source_file = os.path.join(source_path, file_name)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                log(f"Removed file: {replica_file}")


def log(log_file, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - {message}"
    print(log_message)

    with open(log_file, "a") as log_file:
        log_file.write(log_message + "\n")


def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source_folder", help="Path to the source folder.")
    parser.add_argument("replica_folder", help="Path to the replica folder.")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds.")
    parser.add_argument("log_file", help="Path to the log file.")

    args = parser.parse_args()

    while True:
        sync_folders(args.source_folder, args.replica_folder, args.log_file)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

    # NOTE: to run this program use the command line with the required arguments: python folder_sync.py /path/to/source_folder /path/to/replica_folder 60 /path/to/log_file
