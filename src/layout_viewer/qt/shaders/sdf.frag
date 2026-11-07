
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) flat in vec4 a;
layout(location = 1) flat in vec4 b;
layout(location = 2) flat in vec4 c;
layout(location = 3) flat in vec4 params;
layout(location = 4) flat in vec4 flags;
layout(location = 5) flat in vec4 detail;
layout(location = 6) flat in vec4 hole;
layout(location = 7) flat in vec4 tangent;
layout(binding = 1) uniform sampler2D net_palette;
layout(location = 0) out vec4 fragment_color;

#include "common.glsl"
#include "trace.glsl"
#include "pad.glsl"
#include "join.glsl"

void main() {
    // Native stencil_mark's deterministic tie-break keeps pixel-aligned hairlines visible.
    vec2 screen_xy = ((world_fragment + vec2(1.0 / 256.0)) / pixel_ratio - viewport * 0.5)
                     * vec2(mirror_x, 1.0) / scale;
    vec4 screen = vec4(screen_xy, 0, 0);
    float distance;
    float envelope_edge = 0.0;
    if (drill_pass) {
        distance = radial_distance(delta(screen, hole), vec2(detail.y, tangent.z));
    } else if (flags.x < 0.5) {
        distance = line_distance(screen);
    } else if (flags.x < 1.5) {
        distance = arc_distance(screen);
    } else if (flags.x < 3.5) {
        distance = pad_distance(screen);
    } else if (flags.x > 4.5) {
        envelope_edge = abs(pad_distance(screen));
        distance = envelope_edge - 0.8 / (scale * pixel_ratio);
    } else {
        distance = join_distance(screen);
    }
    float aa = 0.65 / (scale * pixel_ratio);
    float coverage = 1.0 - smoothstep(-aa, aa, distance);
    if (coverage <= 0.0) discard;
    if (!multisampled) {
        if (coverage <= 0.5) discard;
        coverage = 1.0;
    }
    vec3 material = layer_color.rgb;
    int net = int(flags.w + 0.5);
    if (color_by_net && net > 0)
        material = texelFetch(net_palette, ivec2((net - 1) % textureSize(net_palette, 0).x, 0), 0).rgb;
    fragment_color = vec4(material, coverage);
}