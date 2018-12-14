from contextlib import suppress

with open("/Users/timbrook/Downloads/data-download-pub78.txt") as data, open("/Users/timbrook/Downloads/foundations_import.csv", "w") as output:
  for line in data.readlines():
    with suppress(IndexError):
      ent = line.split('|')[1]
      output.write(f"\"{ent}\", \"{ent}\"\n")