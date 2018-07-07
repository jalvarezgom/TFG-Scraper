$(function() {
    $('button').click(function() {
    	//url = $("#buscador_input").val(); 
    	usuario = $("#input_usuario").val(); 
    	nivel = $("#input_nivel").val(); 
    	puntuacion = $("#input_puntuacion").val(); 
    	//alert(usuario +nivel+puntuacion);
    	window.location = "/query?usuario="+usuario+"&nivel="+nivel+"&puntuacion="+puntuacion;

    });
});

$(document).ready(function () {
	var width =$(window).width()*1;
	var height =$(window).height()*1;
	var svg = d3.select("div#chartId")
			   .append("div")
			   .classed("svg-container", true) //container class to make it responsive
			   .append("svg")
			   //responsive SVG needs these 2 attributes and no width and height attr
			   .attr("preserveAspectRatio", "xMinYMin meet")
			   .attr("viewBox", "0 0 "+width+" "+height)
			   //class to make it responsive
			   .classed("svg-content-responsive", true); 

	var color = d3.scaleOrdinal(d3.schemeCategory20);

		var simulation = d3.forceSimulation()
		    .force("link", d3.forceLink().id(function(d) { return d.user; }).distance(function(d) {return 100;}).strength(0.1))
		    .force("charge", d3.forceManyBody())
		    .force("collide", d3.forceCollide().radius(function(d) { return d.r + 10; }).iterations(10))
		    .force("center", d3.forceCenter( width / 2,  height / 2));


		var link = svg.append("g")
		    .attr("class", "links")
		    .selectAll("line")
		    .data(graph.links)
		    .enter().append("line");

		var node = svg.append("g")
			.attr("class", "nodes")
			.selectAll("circle")
			.data(graph.nodes)
			.enter().append("circle")
				.attr("r", function(d){return Math.min(Math.max(5, d.score/1000), 40);})
				.attr("fill", function(d) { return color(4); })
				.call(d3.drag()
					.on("start", dragstarted)
					.on("drag", dragged)	
					.on("end", dragended));

		node.append("title")
		    .text(function(d) {return d.user+":"+d.score; });

		simulation
		      .nodes(graph.nodes)
		      .on("tick", ticked);

		simulation.force("link")
		      .links(graph.links);

		function ticked() {
		    link
		        .attr("x1", function(d) { return d.source.x; })
		        .attr("y1", function(d) { return d.source.y; })
		        .attr("x2", function(d) { return d.target.x; })
		        .attr("y2", function(d) { return d.target.y; });

		    node
		        .attr("cx", function(d) { return d.x; })
		        .attr("cy", function(d) { return d.y; });
  		}

  		function dragstarted(d) {
			if (!d3.event.active) simulation.alphaTarget(0.3).restart();
			d.fx = d.x;
			d.fy = d.y;
		}

		function dragged(d) {
			d.fx = d3.event.x;
			d.fy = d3.event.y;
		}

		function dragended(d) {
			if (!d3.event.active) simulation.alphaTarget(0);
			d.fx = null;
			d.fy = null;
		}

});