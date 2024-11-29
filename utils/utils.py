import asyncio

class Utils:

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
