import pandas as pd
import osmnx as ox
import numpy as np

def compute_d2(test_site_gdf, G_proj):
    """Computes d2 and adds columns to testing site GeoDataFrame

    Parameters
    ----------
    test_site_gdf : GeoDataFrame
        GeoDataFrame containing details about testing sites
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    test_site_gdf: GeoDataFrame with additional columns:
        t_node: nearest OSMNx node to testing site lat/lon
        d2: distance in meters between t_node and testing site lat/lon
        t_node_lat: t_node latitude in decimal degrees
        t_node_lon: t_node longitude in decimal degrees
        t_node_x: t_node X projected coordinate
        t_node y: t_node Y projected coordinate
        d2_euc: Euclidean distance between t_node (x,y) and projected 
                centroid lat/lon (PRJ_LAT and PRJ_LON) for testing site

    Note: Uses vectorized pandas operation and pandas apply to speed
          up operations.
    """
    
    test_site_gdf['t_node'], test_site_gdf['d2'] \
        = ox.distance.nearest_nodes(G_proj, \
                                    test_site_gdf['PRJ_LON'].values, \
                                    test_site_gdf['PRJ_LAT'].values, return_dist=True)
    test_site_gdf['t_node_lat'] = test_site_gdf['t_node'].map(lambda x: G_proj.nodes[x]['lat'])
    test_site_gdf['t_node_lon'] = test_site_gdf['t_node'].map(lambda x: G_proj.nodes[x]['lon'])
    test_site_gdf['t_node_x'] = test_site_gdf['t_node'].map(lambda x: G_proj.nodes[x]['x'])
    test_site_gdf['t_node_y'] = test_site_gdf['t_node'].map(lambda x: G_proj.nodes[x]['y'])
    test_site_gdf['d2_euc'] = ox.distance.euclidean_dist_vec(\
                test_site_gdf['PRJ_LAT'].values, test_site_gdf['PRJ_LON'].values, \
                test_site_gdf['t_node_y'].values, test_site_gdf['t_node_x'].values)
    
    return test_site_gdf

def compute_d2_loop(test_site_gdf, G_proj):
    """Computes d2 and adds columns to testing site GeoDataFrame

    Parameters
    ----------
    test_site_gdf : GeoDataFrame
        GeoDataFrame containing details about testing sites
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    test_site_gdf: GeoDataFrame with additional columns:
        t_node: nearest OSMNx node to testing site lat/lon
        d2: distance in meters between t_node and testing site lat/lon
        t_node_lat: t_node latitude in decimal degrees
        t_node_lon: t_node longitude in decimal degrees
        t_node_x: t_node X projected coordinate
        t_node y: t_node Y projected coordinate
        d2_euc: Euclidean distance between t_node (x,y) and projected 
                centroid lat/lon (PRJ_LAT and PRJ_LON) for testing site

    Note: Uses vectorized pandas operation and pandas apply to speed
          up operations.
    """
    test_site_gdf['t_node'] = 0
    test_site_gdf['d2'] = 0.0
    test_site_gdf['d2_euc'] = 0.0
    test_site_gdf['t_node_lat'] = 0.0
    test_site_gdf['t_node_lon'] = 0.0
    test_site_gdf['t_node_x'] = 0.0
    test_site_gdf['t_node_y'] = 0.0
    for index, r in test_site_gdf.iterrows():
        t_node, d2 = ox.distance.nearest_nodes(G_proj, \
                                    r.PRJ_LON, r.PRJ_LAT, return_dist=True)
        test_site_gdf.at[index,'t_node'] = t_node
        test_site_gdf.at[index, 'd2'] = d2
        t_node_lat = G_proj.nodes[t_node]['lat']
        t_node_lon = G_proj.nodes[t_node]['lon']
        t_node_x = G_proj.nodes[t_node]['x']
        t_node_y = G_proj.nodes[t_node]['y']
        test_site_gdf.at[index, 't_node_lat'] = t_node_lat
        test_site_gdf.at[index, 't_node_lon'] = t_node_lon
        test_site_gdf.at[index, 't_node_x'] = t_node_x
        test_site_gdf.at[index, 't_node_y'] = t_node_y
        d2_euc = ox.distance.euclidean_dist_vec(\
                r.PRJ_LAT, r.PRJ_LON, r.t_node_y, r.t_node_x)
        test_site_gdf.at[index, 'd2_euc'] = d2_euc
    
    return test_site_gdf

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()