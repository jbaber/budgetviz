import csv
import datetime
import re
import yaml


def read_yaml(filename):
    """
    Return a dict of the contents of `filename`, a yaml file
    """
    with open(filename) as f:
        return yaml.safe_load(f)


def category(description, description_dict):
  """
  Expect `description_dict` to be

    {'description': 'category', ...}

  and return the matching category corresponding to `description`.  This is
  just a dict lookup, but if an efficient way to check a regex against keys
  could be used, that should go here.
  """
  return description_dict.get(description, None)


def inferred_layout(first_row, second_row, layouts):
  """
  Return the layout guessed at by looking at the
  first two rows of a file based on regular expressions
  stored in `layouts` which looks like

  layouts == {'abc': {'line_regexes': ['^.*$', '^.*$']}, ...}
  """
  for name, layout in layouts.iteritems():
    if re.match(layout['line_regexes'][0], first_row) and \
       re.match(layout['line_regexes'][1], second_row):
      return layout
  raise RuntimeError("Can't infer what type of account the csv file is.")


def import_csv(filename, table, connection, layout):
  """
  Given `layout` a description of `filename` like

  {'cost': 'Tranaction Amount' # or col number if no header
   'cost_multiplier': -1       # multiply expenditures by this
   'date': 'Transaction Date'  # or col number if no header
   'date_string': '%m/%d/%Y'   # strptime format of dates
   'description': "Summary"    # or col number
   'has_header_row': False     # Does the CSV have a header row?
  }

  where the values are the column headers, insert rows from `filename` into
  `table` via `connection`
  """
  with open(filename, 'rb') as csvfile:
    if layout['has_header_row']:
      rows = csv.DictReader(csvfile)
    else:
      rows = csv.reader(csvfile)
    for row in rows:
      # Ignore empty rows
      if not row:
        continue
      ins = table.insert().values(
        description=row[layout['description']],
        date=datetime.datetime.strptime(
          row[layout['date']], layout['date_string']),
        cost=layout['cost_multiplier'] * float(row[layout['cost']]),
      )
      connection.execute(ins)
