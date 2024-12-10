import asyncio
import logging
import os
import shutil
from argparse import ArgumentParser
from pathlib import Path

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_arguments():
    parser = ArgumentParser(description="sort files into subfolders based on file extensions")
    parser.add_argument("--source", required=True, help="path to the source folder")
    parser.add_argument("--output", required=True, help="path to the output folder")
    return parser.parse_args()


async def read_folder(source: Path, output: Path):
    try:
        if not source.exists() or not source.is_dir():
            logging.error(f"source folder does not exist or is not a directory: {source}")
            return

        tasks = []
        for root, _, files in os.walk(source):
            for file in files:
                file_path = Path(root) / file
                tasks.append(copy_file(file_path, output))

        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"error reading folder: {e}")


async def copy_file(file_path: Path, output: Path):
    try:
        extension = file_path.suffix.lower().strip('.') or 'unknown'
        target_dir = output / extension
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / file_path.name
        await asyncio.to_thread(shutil.copy2, file_path, target_file)
    except Exception as e:
        logging.error(f"error copying file {file_path}: {e}")


async def main():
    args = parse_arguments()
    source = Path(args.source)
    output = Path(args.output)

    await read_folder(source, output)


if __name__ == "__main__":
    asyncio.run(main())
