import os
from asyncio import run

from dotenv import load_dotenv

import process
from common import log_str

load_dotenv()


async def main():
    input_directory_name = process.calc_input_directory_name()
    for status in process.STATUSES:
        state_directory_name = process.calc_state_directory_name(status)
        for input_id in process.read_ids(status):
            os.remove(f'{input_directory_name}/{input_id}.json')
            os.remove(f'{state_directory_name}/{input_id}.json')
            log_str(f'deleted: {input_id}')


run(main())