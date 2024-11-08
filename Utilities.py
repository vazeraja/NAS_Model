import asyncio


class Utilities:
    @staticmethod
    async def confirm_and_run(func, prompt, *args, **kwargs):
        """
        Prompts the user to confirm before running the specified function.

        :param func: The function to run if confirmed.
        :param prompt: The prompt that will be displayed to the user.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        """

        response = input(f"{prompt} (Y/N): ").strip().upper()

        if response == 'Y' or response == 'y':
            # Check if the function is awaitable
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
            return True
        elif response == 'N' or response == 'n':
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
            return await Utilities.confirm_and_run(func, prompt, *args, **kwargs)  # Retry on invalid input
