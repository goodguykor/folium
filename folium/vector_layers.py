# -*- coding: utf-8 -*-

"""
Wraps leaflet Polyline, Polygon, Rectangle, Circlem and CircleMarker

"""

from __future__ import (absolute_import, division, print_function)

import json

from branca.element import (CssLink, Element, Figure, JavascriptLink, MacroElement)  # noqa
from branca.utilities import (_locations_tolist, _parse_size, image_to_url, iter_points, none_max, none_min)  # noqa

from folium.map import Marker, Layer

from jinja2 import Template


def path_options(**kwargs):
    """
    Contains options and constants shared between vector overlays
    (Polygon, Polyline, Circle, CircleMarker, and Rectangle).

    Parameters
    ----------
    stroke: Bool, True
        Whether to draw stroke along the path.
        Set it to false to disable borders on polygons or circles.
    color: str, '#3388ff'
        Stroke color.
    weight: int, 3
        Stroke width in pixels.
    opacity: float, 1.0
        Stroke opacity.
    line_cap: str, 'round' (lineCap)
        A string that defines shape to be used at the end of the stroke.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-linecap
    line_join: str, 'round' (lineJoin)
        A string that defines shape to be used at the corners of the stroke.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-linejoin
    dash_array: str, None (dashArray)
        A string that defines the stroke dash pattern.
        Doesn't work on Canvas-powered layers in some old browsers.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
    dash_offset:, str, None (dashOffset)
        A string that defines the distance into the dash pattern to start the dash.
        Doesn't work on Canvas-powered layers in some old browsers.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dashoffset
    fill: Bool, False
        Whether to fill the path with color.
        Set it to false to disable filling on polygons or circles.
    fill_color: str, default to `color` (fillColor)
        Fill color. Defaults to the value of the color option.
    fill_opacity: float, 0.2 (fillOpacity)
        Fill opacity.
    fill_rule: str, 'evenodd' (fillRule)
        A string that defines how the inside of a shape is determined.
        https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/fill-rule
    bubbling_mouse_events: Bool, True (bubblingMouseEvents)
        When true a mouse event on this path will trigger the same event on the
        map (unless L.DomEvent.stopPropagation is used).

    Note that the presence of `fill_color` will override `fill=False`.


    http://leafletjs.com/reference-1.2.0.html#path

    """
    valid_options = (
        'bubbling_mouse_events',
        'color',
        'dash_array',
        'dash_offset',
        'fill',
        'fill_color',
        'fill_opacity',
        'fill_rule',
        'line_cap',
        'line_join',
        'opacity',
        'stroke',
        'weight',
    )
    non_valid = [key for key in kwargs.keys() if key not in valid_options]
    if non_valid:
        raise ValueError(
            '{non_valid} are not valid options, '
            'expected {valid_options}'.format(non_valid=non_valid, valid_options=valid_options)
        )

    color = kwargs.pop('color', '#3388ff')
    fill_color = kwargs.pop('fill_color', False)
    if fill_color:
        fill = True
    elif not fill_color:
        fill_color = color
        fill = kwargs.pop('fill', False)

    return {
        'stroke': kwargs.pop('stroke', True),
        'color': color,
        'weight': kwargs.pop('weight', 3),
        'opacity': kwargs.pop('opacity', 1.0),
        'lineCap': kwargs.pop('line_cap', 'round'),
        'lineJoin': kwargs.pop('line_join', 'round'),
        'dashArray': kwargs.pop('dash_array', None),
        'dashOffset': kwargs.pop('dash_offset', None),
        'fill': fill,
        'fillColor': fill_color,
        'fillOpacity': kwargs.pop('fill_opacity', 0.2),
        'fillRule': kwargs.pop('fill_rule', 'evenodd'),
        'bubblingMouseEvents': kwargs.pop('bubbling_mouse_events', True),
    }


def _parse_options(line=False, radius=False, **kwargs):
    extra_options = {}
    if line:
        extra_options = {
            'smoothFactor': kwargs.pop('smooth_factor', 1.0),
            'noClip': kwargs.pop('no_clip', False),
        }
    if radius:
        extra_options.update({'radius': radius})
    options = path_options(**kwargs)
    options.update(extra_options)
    return json.dumps(options, sort_keys=True, indent=2)


class PolyLine(Marker):
    """
    Class for drawing polyline overlays on a map.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: str or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.
    smooth_factor: float, default 1.0
        How much to simplify the polyline on each zoom level.
        More means better performance and smoother look,
        and less means more accurate representation.
    no_clip: Bool, default False
        Disable polyline clipping.


    http://leafletjs.com/reference-1.2.0.html#polyline

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.polyline(
                    {{this.location}},
                    {{ this.options }}
                    )
                    .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)  # noqa

    def __init__(self, locations, popup=None, tooltip=None, **kwargs):
        super(PolyLine, self).__init__(location=locations, popup=popup,
                                       tooltip=tooltip)
        self._name = 'PolyLine'
        self.options = _parse_options(line=True, **kwargs)


class Polygon(Marker):
    """
    Class for drawing polygon overlays on a map.

    Extends :func:`folium.vector_layers.PolyLine`.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: string or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.


    http://leafletjs.com/reference-1.2.0.html#polygon

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}

            var {{this.get_name()}} = L.polygon(
                {{this.location}},
                {{ this.options }}
                )
                .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)

    def __init__(self, locations, popup=None, tooltip=None, **kwargs):
        super(Polygon, self).__init__(locations, popup=popup, tooltip=tooltip)
        self._name = 'Polygon'
        self.options = _parse_options(line=True, **kwargs)


class Rectangle(Marker):
    """
    Class for drawing rectangle overlays on a map.

    Extends :func:`folium.vector_layers.Polygon`.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: string or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.


    http://leafletjs.com/reference-1.2.0.html#rectangle

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}

            var {{this.get_name()}} = L.rectangle(
                {{this.location}},
                {{ this.options }}
                )
                .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)

    def __init__(self, bounds, popup=None, tooltip=None, **kwargs):
        super(Rectangle, self).__init__(location=bounds, popup=popup,
                                        tooltip=tooltip)
        self._name = 'rectangle'
        self.options = _parse_options(line=True, **kwargs)


class Circle(Marker):
    """
    Class for drawing circle overlays on a map.

    It's an approximation and starts to diverge from a real circle closer to poles
    (due to projection distortion).

    Extends :func:`folium.vector_layers.CircleMarker`.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: string or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.
    radius: float
        Radius of the circle, in meters.


    http://leafletjs.com/reference-1.2.0.html#circle

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}

            var {{this.get_name()}} = L.circle(
                [{{this.location[0]}}, {{this.location[1]}}],
                {{ this.options }}
                )
                .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)

    def __init__(self, location, radius, popup=None, tooltip=None, **kwargs):
        super(Circle, self).__init__(location=location, popup=popup,
                                     tooltip=tooltip)
        self._name = 'circle'
        self.options = _parse_options(line=False, radius=radius, **kwargs)


class CircleMarker(Marker):
    """
    A circle of a fixed size with radius specified in pixels.

    See :func:`folium.vector_layers.path_options` for the `Path` options.

    Parameters
    ----------
    locations: list of points (latitude, longitude)
        Latitude and Longitude of line (Northing, Easting)
    popup: string or folium.Popup, default None
        Input text or visualization for object displayed when clicking.
    tooltip: str or folium.Tooltip, default None
        Display a text when hovering over the object.
    radius: float, default 10
        Radius of the circle marker, in pixels.


    http://leafletjs.com/reference-1.2.0.html#circlemarker

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
            var {{this.get_name()}} = L.circleMarker(
                [{{this.location[0]}}, {{this.location[1]}}],
                {{ this.options }}
                )
                .addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)

    def __init__(self, location, radius=10, popup=None, tooltip=None, **kwargs):
        super(CircleMarker, self).__init__(location=location, popup=popup,
                                           tooltip=tooltip)
        self._name = 'CircleMarker'
        self.options = _parse_options(line=False, radius=radius, **kwargs)

class VectorGridNaverMap(Layer):
    """
    An implementation of VectorGrid.protobuf plugin to display gridded vector data as a layer
    src:    https://github.com/Leaflet/Leaflet.VectorGrid
    docs:   http://leaflet.github.io/Leaflet.VectorGrid/vectorgrid-api-docs.html

    Parameters
    ----------
    tiles: location of the tiles (i.e. url)
    name: name of the layer
    options: options to pass to VectorGrid protobuf (i.e. styles)

    Usage
    -----
    See examples/VectorGrid.ipynb

    """
    _template = Template(u"""
            {% macro script(this, kwargs) -%}
            L.Icon.Default.mergeOptions({
              shadowUrl: "",
              iconRetinaUrl: "",
              iconSize:     [41, 41], // size of the icon
              shadowSize:   [41, 41], // size of the shadow
              iconAnchor:   [20, 37], // point of the icon which will correspond to marker's location
              shadowAnchor: [20, 37],  // the same for the shadow
              popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
            });
            var vectorTileStyling = {
                    water: {
                            fill: true,
                            weight: 1,
                            fillColor: '#9db6ff',
                            color: '#9db6cc',
                            fillOpacity: 1.0,
                            opacity: 1.0,
                    },

                    park: {
                            fill: true,
                            weight: 0.9,
                            fillColor: '#9fca97',
                            color: '#00ff00',
                            fillOpacity: 0.4,
                            opacity: 0.0
                    },

                    road: {	// mapbox & nextzen only
                            fill: true,
                            weight: 1,
                            // fillColor: '#fcfabf',
                            fillColor: '#fcfcfc',
                            color: '#a0a0a0',
                            fillOpacity: 1.0,
                            opacity: 0.0
                    },
                    road2: {	// mapbox & nextzen only
                            fill: true,
                            weight: 1,
                            // fillColor: '#fcfabf',
                            fillColor: '#fcfcfc',
                            color: '#fcfcfc',
                            fillOpacity: 1.0,
                            opacity: 1.0
                    },
                    building: {
                            fill: true,
                            weight: 0.1,
                            fillColor: '#f8f6f1',
                            color: '#000000',
                            fillOpacity: 0.3,
                            opacity: 1.0
                    },
                    sisul: {
                            fill: true,
                            weight: 0.2,
                            fillColor: '#f8f6f1',
                            color: '#a0a0a0',
                            fillOpacity: 0.3,
                            opacity: 1.0
                    },
                    test: {
                            fill: true,
                            weight: 0.2,
                            fillColor: '#000000',
                            color: '#000000',
                            fillOpacity: 1.0,
                            opacity: 1.0
                    },
                    empty: [ ],

            };
            vectorTileStyling.bg_building_a  = vectorTileStyling.building;  // building
            vectorTileStyling.bg_danji_a  = vectorTileStyling.building;             // 단지 묶음
            vectorTileStyling.bg_rd_sisul_a  = vectorTileStyling.sisul;     // 지하철, 지상으로통하는 통로들
            vectorTileStyling.bg_park_a  = vectorTileStyling.park;
            vectorTileStyling.bg_rd_width_a  = vectorTileStyling.road;      // 도로폭
            vectorTileStyling.bg_aptpy_a  = vectorTileStyling.building;     // 아파트단지

            vectorTileStyling.bg_rd_sisul_l  = vectorTileStyling.sisul;
            vectorTileStyling.bg_water_a  = vectorTileStyling.water;
            vectorTileStyling.bg_water_l  = vectorTileStyling.water;
            vectorTileStyling.bg_rd_link_l  = vectorTileStyling.road2;


            // Unused terms
            vectorTileStyling.bg_ferry_l  = vectorTileStyling.empty;
            vectorTileStyling.bg_contour_a  = vectorTileStyling.empty;
            vectorTileStyling.bg_oneway_l  = vectorTileStyling.empty;
            vectorTileStyling.bg_thm_ydo_a  = vectorTileStyling.empty;
            vectorTileStyling.bg_adm_l  = vectorTileStyling.empty;
            vectorTileStyling.bg_thm_jigu_a  = vectorTileStyling.empty;
            vectorTileStyling.bg_rail_l  = vectorTileStyling.empty;
            vectorTileStyling.bg_rd_label_highway_l  = vectorTileStyling.road;
            vectorTileStyling.bg_thm_width_a  = vectorTileStyling.empty;
            vectorTileStyling.bg_subwayrail_label_l  = vectorTileStyling.empty;     // 지하철
            vectorTileStyling.bg_rd_label_general_l  = vectorTileStyling.empty;     // 도로 라벨


            // Unused marks
            vectorTileStyling.nk_bg_adm_l  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_rail_l  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_park_a  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_rd_link_l  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_danji_a  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_water_l  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_water_a  = vectorTileStyling.empty;
            vectorTileStyling.nk_bg_building_a  = vectorTileStyling.empty;
            vectorTileStyling.uturn_p  = vectorTileStyling.empty;
            vectorTileStyling.na_poi_db_p  = vectorTileStyling.empty;
            var vectorTileOptions = {
                vectorTileLayerStyles: vectorTileStyling,
            };

            var {{this.get_name()}} = L.vectorGrid.protobuf(
                '{{this.tiles}}', vectorTileOptions).addTo({{this._parent.get_name()}});
            {%- endmacro %}
            """)  # noqa

    def __init__(self, tiles, name, options):
        self.tile_name = (name if name is not None else
                          ''.join(tiles.lower().strip().split()))
        super(VectorGridNaverMap, self).__init__(name=self.tile_name)
        self.tiles = tiles
        self._name = 'VectorGrid'
        if(options):
            self.options = options

class VectorGrid(Layer):
    """
    An implementation of VectorGrid.protobuf plugin to display gridded vector data as a layer
    src:    https://github.com/Leaflet/Leaflet.VectorGrid
    docs:   http://leaflet.github.io/Leaflet.VectorGrid/vectorgrid-api-docs.html

    Parameters
    ----------
    tiles: location of the tiles (i.e. url)
    name: name of the layer
    options: options to pass to VectorGrid protobuf (i.e. styles)

    Usage
    -----
    See examples/VectorGrid.ipynb

    """
    _template = Template(u"""
            {% macro script(this, kwargs) -%}
            var {{this.get_name()}} = L.vectorGrid.protobuf(
                '{{this.tiles}}',
                {{ this.options }}).addTo({{this._parent.get_name()}});
            {%- endmacro %}
            """)  # noqa

    def __init__(self, tiles, name, options):
        self.tile_name = (name if name is not None else
                          ''.join(tiles.lower().strip().split()))
        super(VectorGrid, self).__init__(name=self.tile_name)
        self.tiles = tiles
        self._name = 'VectorGrid'
        if(options):
            self.options = options

class VectorGridChoropleth(Layer):
    """
    Returns a vector grid based Choropleth, tiles are protobuf based and data is a JSON dictionary,
    linked by the key in (field)
    Parameters
    ----------
    tiles: location of the tiles (i.e. url)
    name: name of the layer
    options: options to pass to VectorGrid protobuf (i.e. styles)
    data: JSON dictionary containing unique keyfield values as keys and color (idealy generated by a color map) as value
    field: linking key field

    Usage
    -----
    See examples/VectorChoropleth.ipynb (may need ipythonwidgets installed)
    """

    _template = Template(u"""
            {% macro script(this, kwargs) -%}
            var vectorTileStyling = {
            {{this.tile_name}} : function(properties,zoom) {
            if(properties.{{this.field}} in  {{this.data}} )
            { 
                     return {
                        "fillColor": {{this.data}}[properties.{{this.field}}],
                        "fillOpacity": 1,
                        "fill": true,
                        "color": '#FFD3D3D3',
                        "opacity": 1,
                        "weight" : 1
                 }
    
            }
            else
            {
            return {
            "color": "#FFD3D3D3",
            "weight": 1,
            "opacity": 0.65
    
                 }
            }
             }
        };
    
            let featureFunction = function(feat) {
            return feat.properties.{{this.field}}; }
        var mapboxVectorTileOptions = {
            rendererFactory: L.canvas.tile,
            attribution: 'none',
            vectorTileLayerStyles: vectorTileStyling,
            interactive	: true,
            getFeatureId : featureFunction
        };
    
            var {{this.get_name()}} = L.vectorGrid.protobuf(
                '{{this.tiles}}', mapboxVectorTileOptions
                ).addTo({{this._parent.get_name()}});
            {%- endmacro %}
            """)  # noqa

    def __init__(self, tiles, name, data, field, options):
        self.tile_name = (name if name is not None else
                          ''.join(tiles.lower().strip().split()))
        super(VectorGridChoropleth, self).__init__(name=self.tile_name)
        self.tiles = tiles
        self._name = 'VectorGridChoropleth'
        self.data = data
        self.field = field
        if (options):
            self.options = options
