import treemap_data
import webbrowser
import datetime
import os
from docopt import docopt
import tempfile
import budgetviz

help_message = """Usage:
  budgetviz [--begin=<begin_date>] [--end=<end_date>] [--config=<config_file>] <csv_file> ...

Options:
  -h --help                   Show this screen.
  -b --begin=<begin_date>     First date in YYYY-MM-DD format [default: 1970-01-01].
  -e --end=<end_date>         Last  date in YYYY-MM-DD format [default: {0}].
  -c --config=<config_file>   YAML file containing categories and regular expressions
                              [default: {1}/.config/budgetviz/config.yaml].
""".format(
  datetime.datetime.now().strftime('%Y-%m-%d'),
  os.environ['HOME']
)


def main():
  """
  This is what runs if the installed command line script is called.
  """
  arguments = docopt(help_message)
  begin = datetime.date(*(int(x) for x in arguments['--begin'].split('-')))
  end = datetime.date(*(int(x) for x in arguments['--end'].split('-')))
  csv_files = arguments['<csv_file>']
  config_file = arguments['--config']
  config = budgetviz.read_yaml(config_file)
  with tempfile.NamedTemporaryFile(delete=False) as json_file:
    for line in treemap_data.just_the_json(
      begin=begin,
      end=end,
      csv_files=csv_files,
      categories=config['categories'],
      layouts=config['layouts'],
      blacklist=config['blacklist']
    ):
      json_file.write(line)
    json_file.close()
  with tempfile.NamedTemporaryFile(delete=False) as html_file:
    html_file.write(treemap_data.complete_html(json_file.name))
    webbrowser.open(html_file.name)
