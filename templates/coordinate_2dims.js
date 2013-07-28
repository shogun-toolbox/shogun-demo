var margin = {top: 20, right: 20, bottom: 30, left: 40};
var width = 660 - margin.left - margin.right;
var height = 610 - margin.top - margin.bottom;

var x = d3.scale.linear().range( [0, width] );
var y = d3.scale.linear().range( [height, 0] );
var horizontal_max=1, horizontal_min=0;
var vertical_max=1, vertical_min=0;
var color = d3.scale.linear()
    .domain([0,1])
    .range(["blue","red"]);

{% if template.coordinate_system.horizontal_axis.range %}
x.domain({{ template.coordinate_system.horizontal_axis.range }}).nice();
{% else %}
x.domain([0, 1]);
{% endif %}
{% if template.coordinate_system.vertical_axis.range %}
y.domain({{ template.coordinate_system.vertical_axis.range }}).nice();
{% else %}
y.domain([0, 1]);
{% endif %}

var xAxis = d3.svg.axis().scale(x).orient("bottom");
var yAxis = d3.svg.axis().scale(y).orient("left");

var xGrid = d3.svg.axis().scale(x).orient("bottom");
var yGrid = d3.svg.axis().scale(y).orient("left");

var canvas_div = d3.select(".span9").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
var svg = canvas_div.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
{% include "mouse_click.js" %}

svg.append("g")
    .attr("class", "grid")
    .attr("id", "x_grid")
    .attr("transform", "translate(0, " + height + ")")
    .call(xGrid
          .tickSize(-height, 0, 0)
          .tickFormat("")
         );
svg.append("g")
    .attr("class", "grid")
    .attr("id", "y_grid")
    .call(yGrid
          .tickSize(-width, 0, 0)
          .tickFormat("")
         );

svg.append("g")
    .attr("class", "axis")
    .attr("id", "x_axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text("{{ template.coordinate_system.horizontal_axis.label }}");

svg.append("g")
    .attr("class", "axis")
    .attr("id", "y_axis")
    .call(yAxis)
    .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("{{ template.coordinate_system.vertical_axis.label }}");

function reset_axis(){
    horizontal_max = vertical_max = 1;
    horizontal_min = vertical_min = 0;
    x.domain([horizontal_min, horizontal_max]);
    y.domain([vertical_min, vertical_max]);
    var t = svg.transition().duration(750);
    t.select("#x_axis").call(xAxis);
    t.select("#y_axis").call(yAxis);
    t.select("#x_grid").call(xGrid);
    t.select("#y_grid").call(yGrid);
}

var area_end = d3.svg.area()
    .x(function(d) { return x(d.x);})
    .y0(function(d) { return y(d.range_lower);})
    .y1(function(d) { return y(d.range_upper);});
var end = d3.svg.line()
    .x(function (d) { return x(d.x); })
    .y(function (d) { return y(d.y); })
    .interpolate('basis');
var start = d3.svg.line()
    .x(function (d) {return x(d.x); })
    .y(function (d) {return y(0); })
    .interpolate('basis');

{% if template.heatmap %}
var heatmap_legend = document.createElement("div");
$('.span9').append(heatmap_legend);
heatmap_legend.id = "legend";
$('#legend').css("background-image", "-webkit-gradient(linear, left top, right bottom, color-stop(0.00, " + color.range()[0] + "), color-stop(1.00, " + color.range()[1] + "))");
$('#legend').html("<span id='lower' style='float:left; color:white;'>" + Math.round(color.domain()[0]) + "</span><span id='upper' style='float:right; color:white;'>" + Math.round(color.domain()[1]) + "</span>") ;
{% include "heatmap.js" %}
{% endif %}
