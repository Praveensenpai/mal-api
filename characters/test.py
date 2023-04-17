import asyncio
from characters import get_characters_pages, process_character
from rich import print


async def main():
    tasks = []
    async for urls in get_characters_pages():
        tasks.extend(asyncio.create_task(process_character(url)) for url in urls)
        results = await asyncio.gather(*tasks)
        print(f"Processed {len(results)} characters")


if __name__ == "__main__":
    asyncio.run(main())
