
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) in vec4 position_split;
layout(location = 1) in uint vertex_net;
layout(location = 0) flat out uint net_id;

// Compensated high/low subtraction, keeping geometry resident while the camera moves.
vec2 subtract_pair(vec2 a, vec2 b) {
    precise float difference = a.x - b.x;
    precise float virtual_b = difference - a.x;
    precise float residual = (a.x - (difference - virtual_b)) - (b.x + virtual_b) + a.y - b.y;
    precise float high = difference + residual;
    precise vec2 result = vec2(high, residual - (high - difference));
    return result;
}

void main() {
    net_id = rectangle_pass ? 0u : vertex_net;
    vec2 screen;
    if (rectangle_pass) {
        vec2 corners[4] = vec2[4](vec2(0, 0), vec2(1, 0), vec2(0, 1), vec2(1, 1));
        screen = mix(rectangle.xy, rectangle.zw, corners[gl_VertexIndex]);
    } else {
        vec2 x = subtract_pair(position_split.xz, camera_split.xz);
        vec2 y = subtract_pair(position_split.yw, camera_split.yw);
        screen = viewport * 0.5 + vec2(x.x + x.y, y.x + y.y) * vec2(mirror_x, -1.0) * scale;
    }
    gl_Position = vec4(screen / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0.0, 1.0);
    gl_Position = clip_corr * gl_Position;
}