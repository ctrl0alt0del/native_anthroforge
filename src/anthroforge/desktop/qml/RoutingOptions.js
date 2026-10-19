.pragma library

// Property projections are QObject maps; copy their public fields explicitly.
function copy(settings) {
    return {obstacle_mode:settings.obstacle_mode || "AUTO", obstacles:settings.obstacles || [],
        excluded_obstacles:settings.excluded_obstacles || [], samples:settings.samples || 64,
        radius:settings.radius || 0, accepted_steps:settings.accepted_steps || 24};
}
