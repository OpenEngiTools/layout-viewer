
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(binding = 1) uniform sampler2D net_palette;
layout(location = 0) flat in uint net_id;
layout(location = 0) out vec4 fragment_color;

void main() {
    // Display-space straight alpha. No second gamma conversion at Qt composition.
    fragment_color = color;
    if (color_by_net && !rectangle_pass && net_id > 0u) {
        int index = int((net_id - 1u) % uint(textureSize(net_palette, 0).x));
        fragment_color.rgb = texelFetch(net_palette, ivec2(index, 0), 0).rgb;
    }
}