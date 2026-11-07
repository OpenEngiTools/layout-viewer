
float join_distance(vec4 screen) {
    vec4 pa = delta(screen, a);
    vec4 ab = delta(b, a);
    vec4 ac = delta(c, a);
    vec2 p = pa.xy + pa.zw;
    vec4 ad = delta(hole, a);
    vec2 vertices[4] = vec2[4](vec2(0), ab.xy + ab.zw, ac.xy + ac.zw, ad.xy + ad.zw);
    int count = int(flags.y + 0.5);
    float distance_squared = 1e30;
    float low = 1e30;
    float high = -1e30;
    for (int i = 0; i < count; i++) {
        vec2 edge = vertices[(i + 1) % count] - vertices[i];
        vec2 v = p - vertices[i];
        vec2 nearest = v - edge * clamp(dot(v, edge) / max(dot(edge, edge), 1e-30), 0.0, 1.0);
        distance_squared = min(distance_squared, dot(nearest, nearest));
        float cross = edge.x * v.y - edge.y * v.x;
        low = min(low, cross);
        high = max(high, cross);
    }
    return sqrt(distance_squared) * ((low >= 0.0 || high <= 0.0) ? -1.0 : 1.0);
}