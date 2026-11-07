
// The MIT notice above applies to PyEDB modifications.
// The upstream portions retain their original license below.
// Modified for PyEDB's RHI renderer; see THIRD_PARTY_NOTICES.txt.

vec2 add_pair(vec2 a, vec2 b) {
    precise float sum = a.x + b.x;
    precise float v = sum - a.x;
    precise float error = (a.x - (sum - v)) + (b.x - v) + a.y + b.y;
    precise float high = sum + error;
    precise vec2 result = vec2(high, error - (high - sum));
    return result;
}

vec2 multiply_pair(vec2 a, vec2 b) {
    precise float ca = 4097.0 * a.x;
    precise float ah = ca - (ca - a.x);
    precise float al = a.x - ah;
    precise float cb = 4097.0 * b.x;
    precise float bh = cb - (cb - b.x);
    precise float bl = b.x - bh;
    precise float product = a.x * b.x;
    precise float error = ((ah * bh - product) + ah * bl + al * bh) + al * bl + a.x * b.y + a.y * b.x;
    return add_pair(vec2(product, 0), vec2(error, 0));
}

vec4 delta(vec4 p, vec4 q) {
    precise vec2 x = add_pair(p.xz, -q.xz);
    precise vec2 y = add_pair(p.yw, -q.yw);
    return vec4(x.x, y.x, x.y, y.y);
}

float precise_dot(vec4 p, vec4 q) {
    precise vec2 sum = add_pair(multiply_pair(p.xz, q.xz), multiply_pair(p.yw, q.yw));
    return sum.x + sum.y;
}

float radial_distance(vec4 p, vec2 radius) {
    precise vec2 squared = add_pair(multiply_pair(p.xz, p.xz), multiply_pair(p.yw, p.yw));
    precise vec2 difference = add_pair(squared, -multiply_pair(radius, radius));
    return (difference.x + difference.y) / max(length(p.xy + p.zw) + radius.x + radius.y, 1e-30);
}

float box_distance(vec2 p, vec2 extent) {
    precise vec2 q = abs(p) - extent;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}