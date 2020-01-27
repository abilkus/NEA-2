import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import box
from shapely.geometry import LineString, Point
place_name = "Kamppi, Helsinki, Finland"
graph = ox.graph_from_place(place_name , network_type='drive')
fig, ax = ox.plot_graph(graph)
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
graph_proj = ox.project_graph(graph)
fig, ax = ox.plot_graph(graph_proj)
plt.tight_layout()
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
edges_proj.head()
stats = ox.basic_stats(graph_proj)
area = edges_proj.unary_union.convex_hull.area
stats = ox.basic_stats(graph_proj, area=area)
extended_stats = ox.extended_stats(graph_proj, ecc=True, bc=True, cc=True)
for key, value in extended_stats.items():
    stats[key] = value

pd.Series(stats)

edges_proj.bounds.head()

bbox = box(*edges_proj.unary_union.bounds)
print(bbox)
orig_point = bbox.centroid
print(orig_point)
nodes_proj['x'] = nodes_proj.x.astype(float)
maxx = nodes_proj['x'].max()
target_loc = nodes_proj.loc[nodes_proj['x']==maxx, :]
print(target_loc)
target_point = target_loc.geometry.values[0]
print(target_point)
orig_xy = (orig_point.y, orig_point.x)
target_xy = (target_point.y, target_point.x)
orig_node = ox.get_nearest_node(graph_proj, orig_xy, method='euclidean')
target_node = ox.get_nearest_node(graph_proj, target_xy, method='euclidean')
o_closest = nodes_proj.loc[orig_node]
t_closest = nodes_proj.loc[target_node]
print(orig_node)
print(target_node)
od_nodes = gpd.GeoDataFrame([o_closest, t_closest], geometry='geometry', crs=nodes_proj.crs)
route = nx.shortest_path(G=graph_proj, source=orig_node, target=target_node, weight='length')
print(route)
fig, ax = ox.plot_graph_route(graph_proj, route, origin_point=orig_xy, destination_point=target_xy)
plt.tight_layout()
route_nodes = nodes_proj.loc[route]
route_line = LineString(list(route_nodes.geometry.values))
print(route_line)
route_geom = gpd.GeoDataFrame(crs=edges_proj.crs)
route_geom['geometry'] = None
route_geom['osmids'] = None
route_geom.loc[0, 'geometry'] = route_line
route_geom.loc[0, 'osmids'] = str(list(route_nodes['osmid'].values))
route_geom['length_m'] = route_geom.length
od_points = gpd.GeoDataFrame(crs=edges_proj.crs)
od_points['geometry'] = None
od_points['type'] = None
od_points.loc[0, ['geometry', 'type']] = orig_point, 'Origin'
od_points.loc[1, ['geometry', 'type']] = target_point, 'Target'
od_points.head()
buildings = ox.buildings_from_place(place_name)
buildings_proj = buildings.to_crs(crs=edges_proj.crs)
fig, ax = plt.subplots()
edges_proj.plot(ax=ax, linewidth=0.75, color='gray')
nodes_proj.plot(ax=ax, markersize=2, color='gray')
buildings_proj.plot(ax=ax, facecolor='khaki', alpha=0.7)
route_geom.plot(ax=ax, linewidth=4, linestyle='--', color='red')
od_points.plot(ax=ax, markersize=24, color='green')
place_name_out = place_name.replace(' ', '_').replace(',','')
streets_out = r"/home/geo/%s_streets.shp" % place_name_out
route_out = r"/home/geo/Route_from_a_to_b_at_%s.shp" % place_name_out
nodes_out = r"/home/geo/%s_nodes.shp" % place_name_out
buildings_out = r"/home/geo/%s_buildings.shp" % place_name_out
od_out = r"/home/geo/%s_route_OD_points.shp" % place_name_out
invalid_cols = ['lanes', 'maxspeed', 'name', 'oneway', 'osmid']

for col in invalid_cols:
    edges_proj[col] = edges_proj[col].astype(str)
edges_proj.to_file(streets_out)
route_geom.to_file(route_out)
nodes_proj.to_file(nodes_out)
od_points.to_file(od_out)
buildings[['geometry', 'name', 'addr:street']].to_file(buildings_out)

