canvas_div
{% if template.mouse_click_enabled == 'left' or template.mouse_click_enabled == 'both' %}
    .on("mousedown", mouse_left_click)
{% endif %}
{% if template.mouse_click_enabled == 'both' %}
    .on("contextmenu", mouse_right_click)
{% endif %}
    .on("mousemove", mouse_move);

//    .style("left", margin.left + "px")
//    .style("top", margin.top + "px");
var mouse_cursor = svg.append("circle")
        .attr("r", 3.5)
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
function mouse_left_click() {
    if (d3.mouse(this)[0]-margin.left < 0 || d3.mouse(this)[1]-margin.top > height)
        return;
    var point = d3.mouse(this);
    point[0]-=margin.left;
    point[1]-=margin.top;
    svg.append("circle")
        .attr("class",  "dot")
        .attr("r", 3.5)
    {%if template.mouse_click_enabled == 'both' %}
        .style("fill", "red")
    {% endif %}
        .attr("cx", point[0])
        .attr("cy", point[1]);
    mouse_left_click_point_set.push( {"x": x.invert(point[0]).toFixed(3),"y": y.invert(point[1]).toFixed(3)});
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
        .attr("r", 3.5)
        .attr("cx", point[0])
        .attr("cy", point[1])
        .style("fill", "blue");
    mouse_right_click_point_set.push( {"x": x.invert(point[0]).toFixed(3),"y": y.invert(point[1]).toFixed(3)});
}
d3.select("svg").node().oncontextmenu = function(){return false;}; //disable right click menu
{% endif %}
