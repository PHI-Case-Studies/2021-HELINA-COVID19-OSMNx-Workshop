import pandas as pd
import osmnx as ox
import numpy as np

from shapely.geometry import LineString, Point

def compute_d1(res_gdf, G_proj):
    """Computes d1 and adds columns to residential centroid GeoDataFrame

    Parameters
    ----------
    res_gdf : GeoDataFrame
        GeoDataFrame containing details about residential units
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    res_gdf: GeoDataFrame with additional columns:
        r_node: nearest OSMNx node to residential unit centroid
        d1: distance in meters between r_node and centroid
        r_node_lat: r_node latitude in decimal degrees
        r_node_lon: r_node longitude in decimal degrees
        r_node_x: r_node X projected coordinate
        r_node y: r_node Y projected coordinate
        d1_euc: Euclidean distance between r_node (x,y) and projected 
                centroid lat/lon (prj_lat and prj_lon) for residential unit
                
    Note: Uses vectorized pandas operation and pandas apply to speed
          up operations.
    """
    res_gdf['r_node'], res_gdf['d1'] \
        = ox.distance.nearest_nodes(G_proj, \
                                    res_gdf['prj_lon'].values, \
                                    res_gdf['prj_lat'].values, return_dist=True)
    res_gdf['r_node_lat'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['lat'])
    res_gdf['r_node_lon'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['lon'])
    res_gdf['r_node_x'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['x'])
    res_gdf['r_node_y'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['y'])
    res_gdf['d1_euc'] = ox.distance.euclidean_dist_vec(\
                res_gdf['prj_lat'].values, res_gdf['prj_lon'].values, \
                res_gdf['r_node_y'].values, res_gdf['r_node_x'].values)
    
    return res_gdf

def compute_d1_loop(res_gdf, G_proj):
    """Computes d1 and adds columns to residential centroid GeoDataFrame

    Parameters
    ----------
    res_gdf : GeoDataFrame
        GeoDataFrame containing details about residential units
    G_proj : NetworkX MultiDigraph
        A projected NetworkX Graph object representing street network

    Returns
    -------
    res_gdf: GeoDataFrame with additional columns:
        r_node: nearest OSMNx node to residential unit centroid
        d1: distance in meters between r_node and centroid
        r_node_lat: r_node latitude in decimal degrees
        r_node_lon: r_node longitude in decimal degrees
        r_node_x: r_node X projected coordinate
        r_node y: r_node Y projected coordinate
        d1_euc: Euclidean distance between r_node (x,y) and projected 
                centroid lat/lon (prj_lat and prj_lon) for residential unit
                
    Note: Uses vectorized pandas operation and pandas apply to speed
          up operations.
    """
    res_gdf['r_node'] = 0
    res_gdf['d1'] = 0.0
    res_gdf['d1_euc'] = 0.0
    res_gdf['r_node_lat'] = 0.0
    res_gdf['r_node_lon'] = 0.0
    res_gdf['r_node_x'] = 0.0
    res_gdf['r_node_y'] = 0.0
    for index, r in res_gdf.iterrows():
        r_node, d1 = ox.distance.nearest_nodes(G_proj, \
                                    r.prj_lon, \
                                    r.prj_lat, return_dist=True)
        res_gdf.at[index,'r_node'] = r_node
        res_gdf.at[index, 'd1'] = d1
        r_node_lat = G_proj.nodes[r_node]['lat']
        r_node_lon = G_proj.nodes[r_node]['lon']
        r_node_x = G_proj.nodes[r_node]['x']
        r_node_y = G_proj.nodes[r_node]['y']
        res_gdf.at[index, 'r_node_lat'] = r_node_lat
        res_gdf.at[index, 'r_node_lon'] = r_node_lon
        res_gdf.at[index, 'r_node_x'] = r_node_x
        res_gdf.at[index, 'r_node_y'] = r_node_y
        d1_euc = ox.distance.euclidean_dist_vec(\
                r.prj_lat, r.prj_lon, r.r_node_y, r.r_node_x)
        res_gdf.at[index, 'd1_euc'] = d1_euc
    #res_gdf['r_node_lat'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['lat'])
    #res_gdf['r_node_lon'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['lon'])
    #res_gdf['r_node_x'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['x'])
    #res_gdf['r_node_y'] = res_gdf['r_node'].map(lambda x: G_proj.nodes[x]['y'])
    
    
    return res_gdf

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()