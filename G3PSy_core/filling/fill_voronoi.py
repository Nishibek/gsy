import numpy as np
    
def fill_voronoi(phase_weights, lower_corner, boxsize, grid_shape=None, boundary_conditions=('isolate', 'isolate', 'isolate', 'isolate', 'isolate', 'isolate'), random_seed=None):
    # Create Voronoi Seeds
    np.random.seed(random_seed)
    voronoi_seeds = np.random.uniform(lower_corner, lower_corner + boxsize, size=(np.sum(phase_weights), 3))
    
    # Generate grid coordinates
    grid_coords = np.mgrid[lower_corner[0]:lower_corner[0]+boxsize[0], 
                            lower_corner[1]:lower_corner[1]+boxsize[1], 
                            lower_corner[2]:lower_corner[2]+boxsize[2]]
    
    # Calculate distances
    if "periodic" in boundary_conditions:
        distance_matrix = np.zeros((boxsize[0], boxsize[1], boxsize[2], voronoi_seeds.shape[0]))
        for idx, seed in enumerate(voronoi_seeds):
            if boundary_conditions[0] == "periodic" or boundary_conditions[1] == "periodic":
                dist_x = np.minimum(np.abs(grid_coords[0] - seed[0]), grid_shape[0] - np.abs(grid_coords[0] - seed[0]))
            else:
                dist_x = grid_coords[0] - seed[0]
            if boundary_conditions[2] == "periodic" or boundary_conditions[3] == "periodic":
                dist_y = np.minimum(np.abs(grid_coords[1] - seed[1]), grid_shape[1] - np.abs(grid_coords[1] - seed[1]))
            else:
                dist_y = grid_coords[1] - seed[1]
            if boundary_conditions[4] == "periodic" or boundary_conditions[5] == "periodic":
                dist_z = np.minimum(np.abs(grid_coords[2] - seed[2]), grid_shape[2] - np.abs(grid_coords[2] - seed[2]))
            else:
                dist_z = grid_coords[2] - seed[2]

            distance_matrix[:, :, :, idx] = np.sqrt(dist_x**2 + dist_y**2 + dist_z**2)
    
    else:
        distance_matrix = np.sqrt((grid_coords[0][..., np.newaxis] - voronoi_seeds[:, 0])**2 + 
                                  (grid_coords[1][..., np.newaxis] - voronoi_seeds[:, 1])**2 + 
                                  (grid_coords[2][..., np.newaxis] - voronoi_seeds[:, 2])**2)

    # Find index of the seed with minimal distance for each point in the grid and assign the index of the nearest seed
    voronoi_map = np.argmin(distance_matrix, axis=-1)
    
    # Map Voronoi indices to phase indices
    phase_indices = np.repeat(np.arange(len(phase_weights)), phase_weights)
    voronoi_map = phase_indices[voronoi_map]

    return voronoi_map


