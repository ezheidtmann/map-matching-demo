jQuery(function($) {
  var colors = {
    0: '#100',
    1: '#300',
    2: '#500',
    3: '#800',
    4: '#b00',
  }
    
  var map = window.map = L.map('map', {
    center: [ 45.52236364215647, -122.6556750350229 ],
    zoom: 13
  });

  L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'ezh.i779mp4n',
    accessToken: 'pk.eyJ1IjoiZXpoIiwiYSI6IlpQQ01TR2cifQ.LuIx3e1Ez52srjbRHymXNg',
  }).addTo(map);

  var colorscale = d3.scale.linear()
    .domain([1, 20])
    .range(['#0f0', '#f00']);

  $.ajax('/segments').done(function(data) {
    console.log(data);
    L.geoJson(data, {
      style: function(feature) {
        var color = colorscale(feature.properties.ride_count);
        console.log(color);
        return { 
          opacity: 1,
          stroke: true,
          color: color
        };
      }
    }).addTo(map);
    $('#loading').hide();
  });
});
