
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) in vec4 center_split;
layout(location = 1) in vec4 label_size;
layout(location = 2) in vec4 atlas_rectangle;
layout(location = 0) out vec2 uv;
layout(location = 1) flat out float bottom_side;

#include "common.glsl"

void main() {
    vec2 x = add_pair(center_split.xz, -camera_split.xz);
    vec2 y = add_pair(center_split.yw, -camera_split.yw);
    vec2 corner = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1));
    vec2 center = viewport * 0.5 + vec2(x.x + x.y, y.x + y.y) * vec2(mirror_x, -1.0) * scale;
    vec2 pixel = center + (corner - 0.5) * label_size.xy;
    gl_Position = vec4(pixel / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0, 1);
    uv = mix(atlas_rectangle.xy, atlas_rectangle.zw, corner);
    bottom_side = label_size.z;
    gl_Position = clip_corr * gl_Position;
}