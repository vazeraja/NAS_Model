import asyncio
import os


class Utils:
    @staticmethod
    async def compare_dicts(dict1, dict2):
        # Check for equality
        if dict1 == dict2:
            return "The channels are equal."

        # Find differing key-value pairs
        differences = {key: value for key, value in dict1.items() if dict2.get(key) != value}

        # Find missing keys in each dictionary
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())

        result = []
        if differences:
            result.append(f"Differences in key-value pairs: {differences}")
        if missing_in_dict1:
            result.append(f"Keys missing in dict1: {missing_in_dict1}")

        return result

    @staticmethod
    async def get_file_count_in_directory(directory):
        return sum(1 for item in os.listdir(directory) if
                   os.path.isfile(os.path.join(directory, item)))

    @staticmethod
    async def get_files_with_ext_full_path(directory, extension):
        """
        Returns a list of all file paths with the specified extension in the specified directory and its subdirectories.

        :param directory: Path to the directory to search.
        :param extension: File extension (e.g., '.epub').
        :return: List of full file paths ending with the specified extension.
        """
        files_with_full_path = []

        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        full_path = os.path.join(root, file)
                        files_with_full_path.append(full_path)
            return files_with_full_path
        except Exception as e:
            print(f"Error while listing files with extension {extension}: {e}")
            return []

    @staticmethod
    async def get_files_with_ext(directory, extension):
        """
        Returns a list of all .epub file paths in the specified directory and its subdirectories.

        :param directory: Path to the directory to search.
        :param extension: File extension.
        :return: List of file paths ending with .epub.
        """
        epub_files = []

        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        epub_files.append(file)
            return epub_files
        except Exception as e:
            print(f"Error while listing .epub files: {e}")
            return []

    @staticmethod
    async def confirm_and_run(func, prompt, *args, **kwargs):
        """
        Prompts the user in the command line to confirm (Y/N) before running the specified function.

        :param func: The function to run if confirmed.
        :param prompt: The prompt message displayed to the user.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: True if the function was executed, False otherwise.
        """
        while True:
            # Prompt the user for confirmation
            response = input(f"{prompt} (Y/N): ").strip().lower()

            if response == 'y' or response == 'Y':
                # Confirm and execute the function
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                return True
            elif response == 'n' or response == 'N':
                # User declined
                return False
            else:
                # Invalid input, prompt again
                print("Invalid input. Please enter 'Y' or 'N'.")
