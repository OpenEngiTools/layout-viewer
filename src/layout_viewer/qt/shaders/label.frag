
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) in vec2 uv;
layout(location = 1) flat in float bottom_side;
layout(binding = 1) uniform sampler2D atlas;
layout(location = 0) out vec4 fragment_color;

void main() {
    vec4 glyph = texture(atlas, uv);
    if (glyph.a <= 0.0) discard;
    // Use only the glyph ink mask, leaving out the atlas's old neutral halo.
    fragment_color = vec4(label_color, glyph.a * (1.0 - glyph.r) * opacity);
}