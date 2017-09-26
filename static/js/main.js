$(function() {
    $('#loading').spin();
    $('#loading').hide();

    $( "#bt_go" ).click(function() {
        refresh_wordcloud();
    });

    $(document).keypress(function(e) {
        if(e.which == 13) {
            refresh_wordcloud();
        }
    });

    function refresh_wordcloud () {
        var place = $('#input_place').val();

        if (place.length == 0) {
            alert('You must input a place name');
        } else {
            $('#svg').empty();
            $('#loading').show();

            var url = document.URL + 'json';

            $.getJSON( url, { place: place }, function( json ) {

              var data = json['msg'];

              var fill = d3.scale.category20();

              d3.layout.cloud().size([1100, 500])
                .words(data.map(function(d) {
                  return {
                    text: d[0],
                    size: d[1] * 8
                  };
                }))
                .padding(3)
                .rotate(function() {
                  return~~ (Math.random()) * 90;
                })
                .font("Impact")
                .fontSize(function(d) {
                  return d.size;
                })
                .on("end", draw)
                .start();

              function draw(words) {
                d3.select("#svg").append("svg")
                  .attr("width", 1140)
                  .attr("height", 540)
                  .append("g")
                  .attr("transform", "translate(550, 250)")
                  .selectAll("text")
                  .data(words)
                  .enter().append("text")
                  .style("font-size", function(d) {
                    return d.size + "px";
                  })
                  .style("font-family", "Impact")
                  .style("fill", function(d, i) {
                    return fill(i);
                  })
                  .attr("text-anchor", "middle")
                  .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                  })
                  .text(function(d) {
                    return d.text;
                  })
              }
            })
            .always(function() {
                $('#loading').hide();
            });
        };
    }
});
