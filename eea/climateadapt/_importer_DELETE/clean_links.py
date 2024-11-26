#!/usr/bin/python
def main():
    lines = set()
    with open('links.txt') as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith('mailto:'):
                lines.add(line.strip())

    with open('clean-links.txt', 'w') as f:
        for line in sorted(lines):
            f.write(line + '\n')

if __name__ == "__main__":
    main()

