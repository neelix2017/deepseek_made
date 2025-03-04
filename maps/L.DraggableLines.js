var gpxControl = L.Control.extend({
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
        container.style.background = 'white';
        container.style.padding = '5px';
        
        var button = L.DomUtil.create('button', '', container);
        button.innerHTML = 'Load GPX';
        button.style.cursor = 'pointer';
        button.style.marginTop = '5px';
        
        var fileInput = L.DomUtil.create('input', '', container);
        fileInput.type = 'file';
        fileInput.accept = '.gpx';
        fileInput.style.display = 'none';
        
        var createBreak = L.DomUtil.create('br', '', container);        
        // Button to create track
        var createButton = L.DomUtil.create('button', '', container);
        createButton.innerHTML = 'Create Track';
        createButton.style.cursor = 'pointer';
        createButton.style.marginTop = '5px';
        
        var createBreak = L.DomUtil.create('br', '', container);        
        // Button to download track as GPX
        var downloadButton = L.DomUtil.create('button', '', container);
        downloadButton.innerHTML = 'Download GPX';
        downloadButton.style.cursor = 'pointer';
        downloadButton.style.marginTop = '5px';
        downloadButton.disabled = true; // Disabled by default
        
        // Add Undo button
        var undoButton = L.DomUtil.create('button', '', container);
        undoButton.innerHTML = 'Undo';
        undoButton.style.cursor = 'pointer';
        undoButton.style.marginTop = '5px';
        undoButton.disabled = true; // Disabled by default
        
        // Trigger file input on button click
        button.onclick = function() {
            fileInput.click();
        };

        // Handle file selection
        fileInput.onchange = function(e) {
            var file = e.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var parser = new DOMParser();
                    var xmlDoc = parser.parseFromString(e.target.result, "text/xml");
                    var trackPoints = xmlDoc.getElementsByTagName('trkpt');
                    var coords = [];
                    
                    for (var i = 0; i < trackPoints.length; i++) {
                        var pt = trackPoints[i];
                        var lat = parseFloat(pt.getAttribute('lat'));
                        var lon = parseFloat(pt.getAttribute('lon'));
                        coords.push([lat, lon]);
                    }
                    
                    // Add polyline to map
                    if (window.gpxLayer) {
                        map.removeLayer(window.gpxLayer);
                    }
                    window.gpxLayer = L.polyline(coords, {color: 'red'}).addTo(map);
                    map.fitBounds(window.gpxLayer.getBounds());
                };
                reader.readAsText(file);
            }
        };
        
        // Handle track creation
        var isCreatingTrack = false;
        var trackPoints = [];
        var tempPolyline;

        var createBreak = L.DomUtil.create('br', '', container);
        var modeSelect = L.DomUtil.create('select', '', container);
        modeSelect.innerHTML = `
            <option value="manual">Manual Creation</option>
            <option value="routing">Routing</option>
        `;
        modeSelect.style.marginTop = '5px';

        var currentMode = 'manual'; // Default mode

        // Handle mode change
        createButton.onclick = function () {
            isCreatingTrack = !isCreatingTrack; // Toggle track creation mode

            if (isCreatingTrack) {
                createButton.innerHTML = 'Stop Creating Track';
                map._container.style.cursor = 'crosshair';

                // Do not reset trackPoints here to preserve existing points
                markers.forEach(marker => map.removeLayer(marker));
                markers = []; // Reset markers
                if (tempPolyline) map.removeLayer(tempPolyline);

                // Remove any existing click listeners
                map.off('click', addTrackPoint);
                map.off('click', handleRouteClick);

                if (currentMode === 'manual') {
                    map.on('click', addTrackPoint);
                } else if (currentMode === 'routing') {
                    map.on('click', handleRouteClick);
                }
            } else {
                downloadButton.disabled = false;
                createButton.innerHTML = 'Create Track';
                map._container.style.cursor = '';
                map.off('click', addTrackPoint);
                map.off('click', handleRouteClick);

                // Add final polyline if valid
                if (trackPoints.length > 1) {
                    if (window.gpxLayer) map.removeLayer(window.gpxLayer);
                    window.gpxLayer = L.polyline(trackPoints, { color: 'blue' }).addTo(map);
                    map.fitBounds(window.gpxLayer.getBounds());
                }

                if (tempPolyline) {
                    map.removeLayer(tempPolyline);
                    tempPolyline = null;
                }
            }
        };

        // Handle mode change
        modeSelect.onchange = function () {
            currentMode = modeSelect.value;

            // If track creation is active, update the event listeners
            if (isCreatingTrack) {
                map.off('click', addTrackPoint);
                map.off('click', handleRouteClick);

                if (currentMode === 'manual') {
                    map.on('click', addTrackPoint);
                } else if (currentMode === 'routing') {
                    map.on('click', handleRouteClick);
                }
            }
        };

        // Function to add manual track points
        function addTrackPoint(e) {
			if (e.originalEvent.target != document.querySelector('div#map_9490ed55967d3527d8d8eadaa359c9a3')) return;
            var marker = L.marker(e.latlng, { draggable: true }).addTo(map);
            markers.push(marker);
            trackPoints.push([e.latlng.lat, e.latlng.lng]); // Add new point to trackPoints
			marker.on('dragend', function(event) {
				var index = markers.indexOf(marker);
				trackPoints[index] = [marker.getLatLng().lat, marker.getLatLng().lng];

				updateTempPolyline()
			});
            // Update temporary polyline
            updateTempPolyline();
            undoButton.disabled = false; // Enable undo button
        }

        // Function to handle routing points
        let clickCount = 0;
        let startPoint, endPoint;
        var handleRouteClick = (e) => {
			if (e.originalEvent.target != document.querySelector('div#map_9490ed55967d3527d8d8eadaa359c9a3')) return;
            if (clickCount === 0) {
                // If there are existing track points, use the last one as the start point
                if (trackPoints.length > 0) {
                    startPoint = L.latLng(trackPoints[trackPoints.length - 1][0], trackPoints[trackPoints.length - 1][1]);
                    clickCount++;
                    calculateRoute2(startPoint, e.latlng);
                } else {
                    // Otherwise, use the clicked point as the start point
                    startPoint = e.latlng;
					 var marker = L.marker(e.latlng, { draggable: true }).addTo(map);
					markers.push(marker);
					trackPoints.push([e.latlng.lat, e.latlng.lng]); // Add new point to trackPoints
					marker.on('dragend', function(event) {
						var index = markers.indexOf(marker);
						trackPoints[index] = [marker.getLatLng().lat, marker.getLatLng().lng];

						updateTempPolyline()
					});
                    clickCount++;
                }
            } else if (clickCount === 1) {
                // Capture end point
                calculateRoute2(startPoint, e.latlng);
            }
			
        };

        async function calculateRoute2(startPoint, endPoint) {
            clickCount = 0;
			const endMarker = L.marker(endPoint, { draggable: false }).addTo(map);
                markers.push(endMarker);
				endMarker.on('dragend', function(event) {
					var index = markers.indexOf(endMarker);
					trackPoints[index] = [endMarker.getLatLng().lat, endMarker.getLatLng().lng];

					updateTempPolyline()
				});
			const route = await fetch(`https://brouter.de/brouter?lonlats=${startPoint.lng},${startPoint.lat}|${endPoint.lng},${endPoint.lat}?profile=trekking&alternativeidx=0&format=geojson`).then((res) => res.json());
            _t = route.features[0].geometry.coordinates.map((p) => [p[0], p[1]]);
			//const route = await fetch(`https://router.project-osrm.org/route/v1/foot/${startPoint.lng},${startPoint.lat};${endPoint.lng},${endPoint.lat}?geometries=geojson`).then((res) => res.json());
			//_t = route.routes[0].geometry.coordinates.map((p) => [p[0], p[1]]);
            _t.forEach(function(point) {
                trackPoints.push([point[1], point[0]]);
            });
            updateTempPolyline();
            undoButton.disabled = false; // Enable undo button
        }

        // Function to update the temporary polyline
        function updateTempPolyline() {
            if (tempPolyline) {
                map.removeLayer(tempPolyline);
            }
            if (trackPoints.length > 1) {
                tempPolyline = L.polyline(trackPoints, { color: 'blue', dashArray: '5, 5' }).addTo(map);
            }
        }

        // Handle GPX download
        downloadButton.onclick = function() {
            if (trackPoints.length > 1) {
                var _t = [];
                map.eachLayer(function(polyline) {
                    if (polyline instanceof L.Polyline) {
                        var points = polyline.getLatLngs();
                        points.forEach(function(point) {
                            _t.push([point.lat, point.lng]);
                        });
                    }
                });
                
                var gpxContent = generateGPX(_t);
                var blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
                var link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'track.gpx';
                link.click();
            }
        };

        // Function to generate GPX content
        function generateGPX(points) {
            var gpx = '<?xml version="1.0" encoding="UTF-8"?>\n';
            gpx += '<gpx version="1.1" creator="Leaflet">\n';
            gpx += '  <trk>\n';
            gpx += '    <trkseg>\n';

            points.forEach(function(point) {
                gpx += `      <trkpt lat="${point[0]}" lon="${point[1]}"></trkpt>\n`;
            });

            gpx += '    </trkseg>\n';
            gpx += '  </trk>\n';
            gpx += '</gpx>';

            return gpx;
        }

        // Handle Undo button click
        undoButton.onclick = function() {
            if (trackPoints.length > 0) {
                trackPoints.pop(); // Remove the last point
                if (markers.length > 0) {
                    var lastMarker = markers.pop(); // Remove the last marker
                    map.removeLayer(lastMarker);
                }
                updateTempPolyline(); // Update the temporary polyline
            }
            if (trackPoints.length === 0) {
                undoButton.disabled = true; // Disable undo button if no points left
            }
        };
		map_9490ed55967d3527d8d8eadaa359c9a3.on({
			keypress: function(e) {
			if (e.originalEvent.key == '\x19')
			{
				undoButton.onclick()
			}
		}});

        return container;
    }
});

var markers = []; // Array to store draggable markers