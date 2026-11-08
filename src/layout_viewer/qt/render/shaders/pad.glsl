
// The MIT notice above applies to PyEDB modifications.
// The upstream portions retain their original license below.
// Modified for PyEDB's RHI renderer; see THIRD_PARTY_NOTICES.txt.

float pad_distance(vec4 screen) {
    float distance;
    vec4 p = delta(screen, a);
    if (flags.x < 2.5) {
        distance = radial_distance(p, vec2(params.x * 0.5, tangent.x * 0.5));
    } else {
        vec2 local = p.xy + p.zw;
        float co = cos(params.z), si = sin(params.z);
        local = vec2(co * local.x + si * local.y, -si * local.x + co * local.y);
        float corner = (detail.w > 0.5 && local.x < 0.0) ? 0.0 : detail.x;
        distance = box_distance(local, params.xy * 0.5 - corner) - corner;
    }
    if (detail.y > 0.0)
        distance = max(distance, -radial_distance(delta(screen, hole), vec2(detail.y, tangent.z)));
    return distance;
}