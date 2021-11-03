"""
OSMNx Tools for Street Networks Case Study (oxtools.py)

This script provides the user with functions to streamline the 
steps in the case study process:
1. Compute d1, d2 for residential unit and testing site GeoDataFrames
   respectively
2. Create residential unit - testing site pair dataframe
3. Compute d3
"""
import pandas as pd
import osmnx as ox
import numpy as np
from shapely.geometry import LineString, Point

def create_paired_df(res_gdf, test_site_gdf):
    """Creates a new Pandas dataframe from residential unit and 
       testing site GeoDataFrame

    Parameters
    ----------
    res_gdf : GeoDataFrame
        GeoDataFrame containing details about residential units
    test_site_gdf : GeoDataFrame
        GeoDataFrame containing details about testing sites

    Returns
    -------
    lc_paired_df: Pandas DataFrame with columns from both
        residential unit and testing site GeoDataFrames:
        1. parish_name
        2. r_node, r_node_lat and r_node_lon
        3. t_node, t_node_lat and t_node_lon
        4. d1 and d2

    Note: list comprehension to speed up nested loop operations.
    """
    data = []
    column_names = ['parish_name', 'r_node', \
                    'r_node_lat', 'r_node_lon', 'prj_lat', 'prj_lon', \
                    't_node', 't_node_lat', 't_node_lon', \
                    'PRJ_LAT', 'PRJ_LON', 'd1', 'd2',]
    data = [[  r_row.parish_name, r_row.r_node, r_row.r_node_lat, r_row.r_node_lon, \
             r_row.prj_lat, r_row.prj_lon, t_row.t_node, t_row.t_node_lat, \
             t_row.t_node_lon, t_row.PRJ_LAT, t_row.PRJ_LON, r_row.d1, t_row.d2 ] \
              for r_row in res_gdf.itertuples() for t_row in test_site_gdf.itertuples() ]
    lc_paired_df = pd.DataFrame(data, columns=column_names)
    
    return lc_paired_df

def compute_d3(paired_df, G_proj, G):
    """Adds new columns for paired_df

    Parameters
    ----------
    paired_df : Pandas DataFrame
        Pandas DataFrame with columns from both
        residential unit and testing site GeoDataFrames
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network
    G : NetworkX MultiDigraph
        An unprojected NetworkX Graph object representing street network

    Returns
    -------
    paired_df: 
    
    Pandas DataFrame with new columns: 
        1. path_node_list: list of OSMNx nodes comprising shortest route 
           from residential unit to testing site
        2. d3: distance in kilometers between r_node and t_node
        3. d_total: sum of d1, d2 and d3
    Pandas DataFrame only contains routes that are the shortest paths

    Note: Uses vectorized pandas operation and pandas apply to speed
          up operations.
    """
    paired_df['path_node_list'] = ox.distance.shortest_path(\
                        G_proj, paired_df['r_node'].values, \
                        paired_df['t_node'].values, weight='length', cpus=2)
    paired_df['d3_euc'] = ox.distance.euclidean_dist_vec(\
                        paired_df['prj_lat'], paired_df['prj_lon'], \
                        paired_df['PRJ_LAT'], paired_df['PRJ_LON'])
    paired_df['d3_path_sum'] = paired_df['path_node_list']\
            .map(lambda x: get_d3_path_sum(x, G_proj))
    paired_df['d3_shapely'] = paired_df['path_node_list']\
            .map(lambda x: LineString(create_coords_list(x, G_proj)))
    paired_df['d3_edge_attrs'] = paired_df['path_node_list']\
            .map(lambda x: np.sum(ox.utils_graph.get_route_edge_attributes(\
                                        G, x, attribute="length")))
    paired_df['d_total'] = paired_df[['d1','d2','d3_edge_attrs']].sum(axis=1)
    
    return paired_df.sort_values(by=['d_total'])\
            .groupby(['r_node'], as_index=False).first()

def get_path_node_list(row_path_node_list):
    """Converts df path_node_list column to path node list;
       used by compute_d3()

    Parameters
    ----------
    row_path_node_list : Pandas DataFrame column
        Pandas DataFrame column of OSMNx nodes comprising a route path

    Returns
    -------
    path_node_list : list 
    """
    return [ int(item.strip()) for item in str(row_path_node_list)\
            .strip('[]').split(',') ]

def create_coords_list(row_path_node_list, G_proj):
    """Creates a list of xy coordinates from df path_node_list column
    using projected street network graph, G_proj; used by compute_d3()
    and nodes_to_linestring()

    Parameters
    ----------
    row_path_node_list : Pandas DataFrame column
        Pandas DataFrame column of OSMNx nodes comprising a route path
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    coords_list : list 
    """
    path_node_list = get_path_node_list(row_path_node_list)
    coords_list = [(G_proj.nodes[node]['x'], G_proj.nodes[node]['y']) \
                       for node in path_node_list ]
    
    return coords_list

def nodes_to_linestring(row_path_node_list, G_proj):
    """Creates a shapely LineString from df path_node_list column
    using projected street network graph, G_proj; used by compute_d3();
    to be stored in a GeoPandas GeoDataFrame geometry column

    Parameters
    ----------
    row_path_node_list : Pandas DataFrame column
        Pandas DataFrame column of OSMNx nodes comprising a route path
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    shapely object : LineString 
    """
    coords_list = create_coords_list(row_path_node_list, G_proj)    
    return LineString(coords_list)

def get_d3_path_sum(row_path_node_list, G_proj):
    """Obtains sum of euclidean distances of component edges using
    nodes from df path_node_list column and projected street 
    network graph, G_proj; used by compute_d3()

    Parameters
    ----------
    row_path_node_list : Pandas DataFrame column
        Pandas DataFrame column of OSMNx nodes comprising a route path
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    sum of list of distances : float 
    """
    path_node_list = get_path_node_list(row_path_node_list)
    dist_list = [ ox.distance.euclidean_dist_vec(\
                    G_proj.nodes[path_node_list[i]]['y'], \
                    G_proj.nodes[path_node_list[i]]['x'], \
                    G_proj.nodes[path_node_list[i+1]]['y'], \
                    G_proj.nodes[path_node_list[i+1]]['x']) \
                    for i in range(len(path_node_list)-1) ]
    
    return np.sum(dist_list)

def get_parish_route(row_path_node_list, parishes_proj_gdf, parish_list, G_proj):
    path_node_list = get_path_node_list(row_path_node_list)
    parish_route = []
    for node in path_node_list:
        node_point = Point(G_proj.nodes[node]['x'], G_proj.nodes[node]['y'])
        for parish in parish_list:
            if parishes_proj_gdf.loc[[parish]]['geometry'][0].convex_hull.contains(node_point):
                if parish not in parish_route:
                    parish_route.append(parish)
                    
    return parish_route

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()