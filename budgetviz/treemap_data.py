import budgetviz
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, \
                       Date, select, Float


def jsoned(name, children):
    """
    Spit out a line of JSON that d3.js wants for treemaps
    """
    category_total = sum([x['cost'] for x in children])
    to_return = '{{"name": "{}", "children": [\n'.format(name)
    to_return += ',\n'.join([
        '    {{"name": "{}", "size": {}, "category": "{}", "category_total": {}, "date": "{}"}}'.format(
          x['description'],
          x['cost'],
          name,
          category_total,
          x['date'].strftime('%b. %-d, %Y')
        )
        for x in children
    ])
    to_return += '\n]}'
    return to_return


def complete_html(json_location):
  """
  The entire html string for the d3.js treemap given the location of a JSON
  file to read.
  """
  return """
<!DOCTYPE html>
<html>
<meta charset="utf-8">
<head>
<style>

body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  margin: auto;
  position: relative;
  width: 960px;
}

form {
  position: absolute;
  right: 10px;
  top: 10px;
}

.node {
  border: solid 1px white;
  font: 10px sans-serif;
  line-height: 12px;
  overflow: hidden;
  position: absolute;
  text-indent: 2px;
}

div.tooltip {
  position: absolute;
  top: 10em;
  left: 10em;
  text-align: center;
  /*
  width: 60px;
  height: 28px;
  */
  padding: 2px;
  font: 12px sans-serif;
  background: black;
  color: grey;
  border: 0px;
  border-radius: 8px;
  pointer-events: none;
}

</style>
</head>
<body>
<form>
  <label><input type="radio" name="mode" value="size" checked> Cost</label>
  <label><input type="radio" name="mode" value="count"> Number of transactions</label>
</form>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script>

var margin = {top: 40, right: 10, bottom: 10, left: -225},
    width = 960 - margin.left - margin.right,
    height = 800 - margin.top - margin.bottom;

var color = d3.scale.category20c();

var treemap = d3.layout.treemap()
    .size([width, height])
    .sticky(true)
    .value(function(d) { return d.size; });

var div = d3.select("body").append("div")
    .style("position", "relative")
    .style("width", (width + margin.left + margin.right) + "px")
    .style("height", (height + margin.top + margin.bottom) + "px")
    .style("left", margin.left + "px")
    .style("top", margin.top + "px");

var divy = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

d3.json("%s", function(error, root) {
  var node = div.datum(root).selectAll(".node")
      .data(treemap.nodes)
      .enter()
      .append("div")
      .attr("class", "node")
      .call(position)
      .on("mouseover", function(d) {
          divy.transition()
              .duration(200)
              .style("opacity", .9);
          divy .html('<b style="color:red;">' + d.category + ' ($' + d.category_total + ')</b><br/>' + d.name + '<br/><span style="color:green;">$' + d.size + '</span><br>' + d.date)
              .style("left", (d3.event.pageX - 220) + "px")
              .style("top", (d3.event.pageY - 28) + "px");
          })
      .on("mouseout", function(d) {
          divy.transition()
              .duration(500)
              .style("opacity", 0);
      })
      .style("background", function(d) { return d.children ? color(d.name) : null; })
      .text(function(d) { return d.children ? null : d.name + "\\n$" + d.size; });

  d3.selectAll("input").on("change", function change() {
    var value = this.value === "count"
        ? function() { return 1; }
        : function(d) { return d.size; };


      node
        .data(treemap.value(value).nodes)
      .transition()
        .duration(1500)
        .call(position);
  });
});

function position() {
  this.style("left", function(d) { return d.x + "px"; })
      .style("top", function(d) { return d.y + "px"; })
      .style("width", function(d) { return Math.max(0, d.dx - 1) + "px"; })
      .style("height", function(d) { return Math.max(0, d.dy - 1) + "px"; });
}

</script>
</body>
</html>
  """ % json_location


def just_the_json(csv_files, begin, end, categories, layouts, blacklist=None):
  """
  Generator yielding the lines of JSON that can be put in a file for
  d3.js to read in and make a treemap.

  `begin` and `end` should be datetimes
  `categories` should be a dict like
    {'description': 'category', ...}
  `layouts` should be a dict like
    {'abc': {'line_regexes': ['^.*$', '^.*$']}, ...}
  `blacklist` is a list of categories to suppress in the treemap
  """
  if blacklist == None:
    blacklist = []
  # Read all the data into an in-memory sqlite table
  metadata = MetaData()
  engine = sqlalchemy.create_engine('sqlite:///:memory:')
  # All transactions stored in this table
  transactions = Table(
    'transactions',
    metadata,
    Column('ordinal', Integer, primary_key=True),
    Column('description', String),
    Column('date', Date),
    Column('cost', Float),
  )
  # Actually create the table
  metadata.create_all(engine)
  conn = engine.connect()
  for csv_file in csv_files:
    with open(csv_file, 'r') as f:
      first_row = f.readline()
      second_row = f.readline()
    budgetviz.import_csv(
      filename=csv_file,
      table=transactions,
      connection=conn,
      layout=budgetviz.inferred_layout(first_row, second_row, layouts)
    )
  s = select([
    transactions.c.description,
    transactions.c.date,
    transactions.c.cost,
  ])
  all_records = {}
  for row in conn.execute(s):
    description = row['description']
    date = row['date']
    cost = row['cost']
    cat = budgetviz.category(description, categories)
    if date < begin or date > end or cost < 0:
      continue
    new_item = {
        'date': date,
        'description': description,
        'cost': cost,
    }
    if cat in all_records:
        all_records[cat].append(new_item)
    else:
        all_records[cat] = [new_item]
  yield '{"name": "expenditures", "children": ['
  yield ",\n".join([
    jsoned(cat, [x for x in all_records[cat]])
    for cat in all_records
    if cat not in blacklist
  ])
  yield ']}'
