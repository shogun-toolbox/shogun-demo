var points = {};
var feature_type = "a";
var fill = d3.scale.category10();

var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 640 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var svg = d3.select("div.svg-container").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .on("mousedown", mousedown)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
  .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")

svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
  .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")

function mousedown() {
    var point = d3.mouse(this);

    point[0] -= margin.left;
    point[1] -= margin.top;

    if (point[0] < 0 || point[1] < 0 || point[0] > width || point[1] > height) {
        return;
    }

    svg.append("circle")
        .attr("r", 5)
        .attr("cx", point[0])
        .attr("cy", point[1])
        .attr("class", feature_type)
        .attr("opacity", 0)
      .transition()
        .duration(200)
        .ease("linear")
        .attr("opacity", 1);

    point[0] /= width;
    point[1] /= height;

    if (feature_type in points) {
        points[feature_type].push(point);
    } else {
        points[feature_type] = [point];
    }
}

function change_features(feature) {
    feature_type = feature;
    d3.selectAll("button")
        .classed("btn-primary", 0);
    d3.select("#" + feature + "_button")
        .classed("btn-primary", 1);
}

function classify(url) {
    c = parseInt(d3.select("input#c-param").property("value"));
    if (!c) {
        c = 1;
    }
    kernel = d3.select("select#kernel-param").property("value");
    if (!kernel) {
        kernel = "gaussian";
    }
    sigma = parseFloat(d3.select("input#sigma-param").property("value"));
    if (!sigma) {
        sigma = 10000;
    }
    degree = parseInt(d3.select("input#degree-param").property("value"));
    if (!degree) {
        degree = 2;
    }

    data = {
        "points": JSON.stringify(points),
        "C": JSON.stringify(c),
        "width": JSON.stringify(width),
        "height": JSON.stringify(height),
        "kernel": JSON.stringify(kernel),
        "sigma": JSON.stringify(sigma),
        "degree": JSON.stringify(degree),
    };
    request_clasify(data, url);
}

function request_clasify(message, url) {
    $.ajax({
        url:url,
        type: "GET",
        contentType: "application/json",
        dataType: 'text',
        data: message,
        success: recv,
    });
}

function clear_demo() {
    //Remove points
    svg.selectAll("circle")
        .remove();
    points = {};

    // Remove paths
    svg.selectAll("path")
        .remove();
}

function recv(data) {
    data = JSON.parse(data);

    if (data["status"] != "ok") {
        alert(data["status"]);
        return;
    }

    // Grid data
    z = data["z"];

    // Generate contour
    var cliff = -100;
    z.push(d3.range(z[0].length).map(function() { return cliff; }));
    z.unshift(d3.range(z[0].length).map(function() { return cliff; }));
    z.forEach(function(d) {
        d.push(cliff);
        d.unshift(cliff);
    });

    var c = new Conrec(),
        xs = d3.range(0, z.length),
        ys = d3.range(0, z[0].length),
        zs = d3.range(data["min"], data["max"], 0.1),
        x = d3.scale.linear().range([0, width]).domain([0, z.length]),
        y = d3.scale.linear().range([0, height]).domain([0, z[0].length]),
        colours = d3.scale.linear().domain(data["domain"]).range(["blue", "red"]);

    c.contour(z, 0, xs.length-1, 0, ys.length-1, xs, ys, zs.length, zs);

    // Remove old paths
    svg.selectAll("path")
        .remove();
    // Create new paths
    svg.selectAll("path").data(c.contourList())
        .enter().append("svg:path")
        .style("fill", function(d) { return colours(d.level);})
        .attr("class", "path")
        .attr("d",d3.svg.line()
            .x(function(d) { return x(d.x); })
            .y(function(d) { return y(d.y); })
        );
    // Sort points
    svg.selectAll("circle")
        .each(function(d, i) {
            this.parentNode.appendChild(this);
        });

    svg.selectAll("text")
        .each(function(d, i) {
            this.parentNode.appendChild(this);
        });

}

