
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) out vec4 fragment_color;

float grid_line(vec2 world, vec2 phase, float step_size, float half_width) {
    vec2 distance = abs(fract((world + phase) / step_size + 0.5) - 0.5) * step_size * scale;
    float aa = 0.4 / pixel_ratio;
    return 1.0 - smoothstep(half_width - aa, half_width + aa, min(distance.x, distance.y));
}

void main() {
    if (modes.w < 0.5) { fragment_color = vec4(1.0); return; }
    vec2 world = (world_fragment / pixel_ratio - viewport * 0.5) * vec2(mirror_x, 1.0) / scale;
    float minor = grid_line(world, minor_phase, spacing, 0.35);
    float major = grid_line(world, major_phase, spacing * 5.0, 0.55);
    // Sampled from the user's reference: #dadaea minor / #c4c4de major.
    vec3 color = mix(vec3(1.0), vec3(218.0, 218.0, 234.0) / 255.0, minor);
    color = mix(color, vec3(196.0, 196.0, 222.0) / 255.0, major);
    fragment_color = vec4(color, 1.0);
}