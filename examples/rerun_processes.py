from asyncio import run

from dotenv import load_dotenv

import process
from common import async_map

load_dotenv()


def read_process_inputs():
    r = []
    for input_id in process.read_ids('initial'):
      r.append(process.read_input(input_id))
    return r


async def main():
    process_inputs = read_process_inputs()
    await async_map(process.execute_process, process_inputs)


run(main())