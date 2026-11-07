
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"
layout(binding = 1) uniform sampler2D strokes;
layout(location = 0) out vec4 fragment_color;

float coverage_at(ivec2 texel) {
    return texelFetch(strokes, clamp(texel, ivec2(0), textureSize(strokes, 0) - 1), 0).a;
}

void main() {
    // Preserve the last covered primitive's material.
    ivec2 texel = ivec2(gl_FragCoord.xy);
    vec4 material = texelFetch(strokes, texel, 0);
    if (material.a <= 0.0) discard;
    // Retain the net material for opaque strokes even when the fill uses layer colors.
    vec3 rgb = fill_by_net ? material.rgb : color.rgb;
    float ink = 0.0;
    if (outline) {
        // Ink the inner edge of the layer union, one logical pixel wide.
        int reach = max(1, int(round(pixel_ratio)));
        float lowest = material.a;
        for (int step = 1; step <= reach; ++step) {
            lowest = min(lowest, min(min(coverage_at(texel + ivec2(step, 0)), coverage_at(texel - ivec2(step, 0))),
                                     min(coverage_at(texel + ivec2(0, step)), coverage_at(texel - ivec2(0, step)))));
        }
        ink = clamp(material.a - lowest, 0.0, 1.0);
    }
    fragment_color = vec4(mix(rgb, material.rgb, ink), material.a * mix(color.a, 1.0, ink));
}