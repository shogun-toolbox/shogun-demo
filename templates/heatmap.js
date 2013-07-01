{% if template.heatmap.contour %}
function getContour(z, minimum, maximum, dom) {
    // Generate contour
    var cliff = -100;
    z.push(d3.range(z[0].length).map(function() { return cliff; }));
    z.unshift(d3.range(z[0].length).map(function() { return cliff; }));
    z.forEach(function(d) {
        d.push(cliff);
        d.unshift(cliff);
    });
    var c = new Conrec();
    var xs = d3.range(0, z.length);
    var ys = d3.range(0, z[0].length);
    var zs = d3.range(minimum, maximum, 0.1);
    var x = d3.scale.linear().range([0, width]).domain([1, z.length-2]);
    var y = d3.scale.linear().range([height, 0]).domain([1, z[0].length-2]);
    var colour_scale = d3.scale.linear().domain(dom).range(["white, white"]);

    c.contour(z, 0, xs.length-1, 0, ys.length-1, xs, ys, zs.length, zs);

    return {"contour": c, "x_scale": x, "y_scale": y, "color_scale": colour_scale};
}
{% endif %}
