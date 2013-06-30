var margin = {top: 20, right: 20, bottom: 30, left: 40};
var width = 660 - margin.left - margin.right;
var height = 610 - margin.top - margin.bottom;

var x = d3.scale.linear().range( [0, width] );
var y = d3.scale.linear().range( [height, 0] );


{% if template.coordinate_system.horizontal_axis.range %}
x.domain({{ template.coordinate_system.horizontal_axis.range }}).nice();
{% else %}
x.domain([0, 1]);
{% endif %}
{% if template.coordinate_system.vertical_axis.range %}
y.domain({{ template.coordinate_system.vertical_axis.range }}).nice();
{% else %}
y.domain([0,0.8]);
{% endif %}

var xAxis = d3.svg.axis().scale(x).orient("bottom");
var yAxis = d3.svg.axis().scale(y).orient("left");

function make_x_axis(){
    return d3.svg.axis().scale(x).orient("bottom").ticks(10);
}
function make_y_axis(){
    return d3.svg.axis().scale(y).orient("left").ticks(8);
}

var canvas_div = d3.select(".span9").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
var svg = canvas_div.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
{% include "mouse_click.js" %}

svg.append("g")
    .attr("class", "grid")
    .attr("transform", "translate(0, " + height + ")")
    .call(make_x_axis()
          .tickSize(-height, 0, 0)
          .tickFormat("")
         );
svg.append("g")
    .attr("class", "grid")
    .call(make_y_axis()
          .tickSize(-width, 0, 0)
          .tickFormat("")
         );

svg.append("g")
    .attr("class", "axis")
{% if template.coordinate_system.horizontal_axis.position == 'bottom' %}
    .attr("transform", "translate(0," + height + ")")
{% elif template.coordinate_system.horizontal_axis.position == 'top' %}
    .attr("transform", "translate(0," + 0 + ")")
{% else %}
    .attr("transform", "translate(0," + height/2 + ")")
{% endif %}

    .call(xAxis)
    .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text("{{ template.coordinate_system.horizontal_axis.label }}");

svg.append("g")
    .attr("class", "axis")
{% if template.coordinate_system.vertical_axis.position == 'left' %}
{% elif template.coordinate_system.vertical_axis.position == 'right' %}
    .attr("transform", "translate(" + width + ")")
{% else %}
    .attr("transform", "translate(" + width/2 + ")")
{% endif %}
    .call(yAxis)
    .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("{{ template.coordinate_system.vertical_axis.label }}");

{% if template.heatmap %}
var color = d3.scale.linear()
    .domain([0,1])
    .range(["blue","red"]);
var heatmap_legend = document.createElement("div");
$('.span9').append(heatmap_legend);
heatmap_legend.id = "legend";
$('#legend').css("background-image", "-webkit-gradient(linear, left top, right bottom, color-stop(0.00, " + color.range()[0] + "), color-stop(1.00, " + color.range()[1] + "))");
$('#legend').html("<span id='lower' style='float:left; color:white;'>" + Math.round(color.domain()[0]) + "</span><span id='upper' style='float:right; color:white;'>" + Math.round(color.domain()[1]) + "</span>") ;
{% include "heatmap.js" %}
{% endif %}
