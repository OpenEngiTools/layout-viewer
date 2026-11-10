
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"
void main() {
    vec2 vertices[3] = vec2[3](vec2(-1, -1), vec2(3, -1), vec2(-1, 3));
    gl_Position = vec4(vertices[gl_VertexIndex], 0, 1);
    gl_Position = clip_corr * gl_Position;
}