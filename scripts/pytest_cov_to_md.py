"""
Simple script to parse pytest-cov output and create a markdown table with the coverage.
"""
import re
import argparse


def extract_coverage_section(output: str) -> str:
    """ Extract coverage section from pytest-cov output. """

    output_lines = output.splitlines()
    start_regex = r'^-+\s+coverage:'
    start_index = 0

    for idx, line in enumerate(output_lines):
        if re.match(start_regex, line):
            start_index = idx
            break

    return '\n'.join(output_lines[start_index:])


def coverage_to_markdown(coverage_section: str) -> str:
    """ Convert the coverage section to Markdown format. """
    lines = coverage_section.strip().split("\n")

    # Extract the header and the TOTAL line
    header_index = [i for i, line in enumerate(lines) if line.startswith("Name")][0]
    total_index = [i for i, line in enumerate(lines) if line.startswith("TOTAL")][0]

    # Extract the relevant sections
    header = lines[header_index]
    data = lines[header_index + 1 : total_index]
    total_line = lines[total_index]

    # Convert header to Markdown format
    header_md = (
        "| " + re.sub(r"\s{2,}", " | ", header) + " |"
    )
    separator_md = "| " + " | ".join(["---"] * len(header.split())) + " |"

    # Convert data rows to Markdown format
    data_md = []
    for row in data:
        row_md = "| " + re.sub(r"\s{2,}", " | ", row.strip()) + " |"
        data_md.append(row_md)

    # Convert TOTAL row to Markdown format
    total_md = "| " + re.sub(r"\s{2,}", " | ", total_line.strip()) + " |"

    # Combine everything into the final Markdown
    markdown_output = "\n".join(
        ["# Coverage Report", "", header_md, separator_md] + data_md + [total_md]
    )
    return markdown_output


def parse_args():
    """ Parse arguments given to this CLI. """
    parser = argparse.ArgumentParser(description="Simple script used to transform pytest-cov output to markdown.")

    parser.add_argument("--file", required=True, type=str, help="pytest-cov output.")

    return parser.parse_args()

def main():
    """ Main Command Line Interface tool entrypoint. """
    args = parse_args()

    with open(args.file, 'r') as coverage_file:
        coverage_output = coverage_file.read()

    coverage_section = extract_coverage_section(coverage_output)
    if coverage_section:
        md = coverage_to_markdown(coverage_section)
        print(md)
    else:
        raise ValueError(f"No coverage section found in the provided file:\n{coverage_output}")

if __name__ == "__main__":
    main()
