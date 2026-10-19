struct AfMuscleInput {
    int point_start,input_rows,input_cols,target_cols,densify,closed_u,topology_closed_v;
    int topology_flip,inflation_mode,inflation_enabled,falloff,inflation_closed_v,inflation_flip,initialize_control;
    double amount,radius,depth,b_strength,b_band,b_power,taper,control[3];
};

struct AfMuscleStats { int workers,parallel,muscles,input_points,output_points;double elapsed_ms; };
struct AfMuscleOutput { std::vector<double> boundary_weights,length_weights;std::vector<Vec> base,inflated;std::vector<int64_t> faces;int rows=0,cols=0,status=0; };
struct AfMuscleBatch { std::vector<AfMuscleOutput> outputs; };

