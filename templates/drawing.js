var margin = {top: 20, right: 20, bottom: 30, left: 40};
var width = 660 - margin.left - margin.right;
var height = 610 - margin.top - margin.bottom;

var x = d3.scale.linear().range( [0, width] ).domain([0,1]);
var y = d3.scale.linear().range( [0, height] ).domain([0,1]);

var xGrid = d3.svg.axis().scale(x).orient("bottom");
var yGrid = d3.svg.axis().scale(y).orient("left");

var canvas_div = d3.select(".span9").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
var svg = canvas_div.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "grid")
    .attr("id", "x_grid")
    .attr("transform", "translate(0, " + height + ")")
    .call(xGrid
          .tickSize(-height, 0, 0)
          .ticks(20)
          .tickFormat("")
         );
svg.append("g")
    .attr("class", "grid")
    .attr("id", "y_grid")
    .call(yGrid
          .tickSize(-width, 0, 0)
          .ticks(20)
          .tickFormat("")
         );


{% include "mouse_click.js" %}
