import asyncio
import persons
import person

TASK_COUNT = 100


async def main():
    await persons.push_people_links()  # Push person links to database
    sem = asyncio.Semaphore(TASK_COUNT)  # Allow up to X concurrent requests
    tasks = [
        asyncio.create_task(person.process_person(url, sem))
        for url in person.get_people_pages()
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
