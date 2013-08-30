{% if template.type == 'coordinate-2dims' %}
canvas_div
{% if template.mouse_click_enabled == 'left' or template.mouse_click_enabled == 'both' %}
    .on("click", mouse_left_click)
{% endif %}
{% if template.mouse_click_enabled == 'both' %}
    .on("contextmenu", mouse_right_click)
{% endif %}
    .on("mousemove", mouse_move);

{% if template.feature_number > 0 %}
var current_label = 0;
var feature_color = d3.scale.linear().domain([0, {{ template.feature_number }}]).range(["blue", "red"]);
{% endif %}
var mouse_cursor = svg.append("circle")
        .attr("r", 6.5)
        .attr("transform", "translate(-100,-100)")
        .attr("class", "cursor");
function mouse_move() {
    if (d3.mouse(this)[0]-margin.left < 0 || d3.mouse(this)[1]-margin.top > height)
        return;
    mouse_cursor.attr("transform", "translate(" +
                (d3.mouse(this)[0]-margin.left) +","+
                (d3.mouse(this)[1]-margin.top) + ")");
}
{% if template.mouse_click_enabled == 'left' or template.mouse_click_enabled == 'both' %}
var point_set=[];
function mouse_left_click(event) {
    if (d3.mouse(this)[0]-margin.left < 0 || d3.mouse(this)[1]-margin.top > height)
        return;
    var point = d3.mouse(this);
    var e = window.event || d3.event;
    if(e.button == 2 || e.button == 3)
        return;
    point[0]-=margin.left;
    point[1]-=margin.top;
    svg.append("circle")
        .attr("class",  "dot")
        .attr("r", 6)
    {% if template.mouse_click_enabled == 'both' %}
        .style("fill", "red")
    {% endif %}
    {% if template.feature_number > 0 %}
        .style("fill", feature_color(current_label))
    {% endif%}
        .attr("cx", point[0])
        .attr("cy", point[1]);
    point_set.push( {"x": x.invert(point[0]).toFixed(3),
                     "y": y.invert(point[1]).toFixed(3),
                     {% if template.feature_number > 0 %} 
                     "label": current_label});
                     {% else %}
                     "label": +1});{% endif %}
}
{% endif %}
{% if template.mouse_click_enabled == 'both' %}
function mouse_right_click()
{
    if (d3.mouse(this)[0]-margin.left < 0 || d3.mouse(this)[1]-margin.top > height)
        return;
    var point = d3.mouse(this);
    point[0]-=margin.left;
    point[1]-=margin.top;
    svg.append("circle")
        .attr("class",  "dot")
        .attr("r", 6)
        .attr("cx", point[0])
        .attr("cy", point[1])
        .style("fill", "blue");
    point_set.push( {"x": x.invert(point[0]).toFixed(3),
                     "y": y.invert(point[1]).toFixed(3),
                     "label": -1});
}
d3.select("svg").node().oncontextmenu = function(){return false;}; //disable right click menu
{% endif %}
{% elif template.type == 'drawing' %}
var pressed = false;
var line_dots=[];
var last_dot=[];
var lines = [];
canvas_div
    .on("mousedown", mouse_down)
    .on("mousemove", mouse_move)
    .on("mouseup", mouse_up);

function mouse_move() {
    if(pressed)
    {
        if (d3.mouse(this)[0]-margin.left <= 0 
            || d3.mouse(this)[1]-margin.top >= height
            || d3.mouse(this)[0]-margin.left >= width
            || d3.mouse(this)[1]-margin.top <= 0)
        {
            mouse_up();
            return;
        }
        var point = d3.mouse(this);
        point[0]-=margin.left;
        point[1]-=margin.top;
        line_dots.push([x.invert(point[0]), y.invert(point[1])]);

        var line = d3.svg.line()
                .x(function(d) {return x(d[0]);})
                .y(function(d) {return y(d[1]);})
                .interpolate('basis');
        if(last_dot.length)
          svg.append("path")
            .attr("class", "drawing")
            .attr("d",line([[x.invert(last_dot[0]),
                             y.invert(last_dot[1])],
                            [x.invert(point[0]),
                             y.invert(point[1])]]))
            .style("stroke-width", "30")
            .style("stroke", "green")
            .style("stroke-linecap","round")
            .style("stroke-linejoin", "round")
            .style("fill", "transparent");
        last_dot = [].concat(point);
    }
}
function mouse_down(){
    pressed = true;
}
function mouse_up(){
    svg.selectAll(".drawing")
        .attr("class", "drew");
    if(line_dots.length)
        lines.push(line_dots);
    line_dots = [];
    last_dot = [];
    pressed = false;
}

{% endif %}
