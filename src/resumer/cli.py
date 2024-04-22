import os
import sys
import argparse
sys.path.append(os.path.dirname(__file__))

from resumer.generator import Generator
from resumer.model import ResumerData

# Setting up the argument parser
parser = argparse.ArgumentParser(description='Generate resumes based on provided configuration.')
parser.add_argument('data', type=str, help='Path to the data toml')
parser.add_argument('config', type=str, help='Path to the config toml')

def main():
    args = parser.parse_args()

    # Load the data using provided arguments
    data = ResumerData.load(args.data, args.config)

    # Create a generator instance with the loaded data
    g = Generator(data)

    # Run the generator
    g.run()

if __name__ == '__main__':
    main()