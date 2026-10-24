#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 texel;
    float useMaskColors;
};
layout(binding = 1) uniform sampler2D source;

vec4 edgeSample() {
    vec4 edge = texture(source, qt_TexCoord0);
    for (int y = -2; y <= 2; ++y)
        for (int x = -2; x <= 2; ++x)
            if (x*x + y*y <= 5) {
                vec4 sampleValue = texture(source, qt_TexCoord0 + vec2(x,y)*texel);
                if (max(sampleValue.r, sampleValue.g) > max(edge.r, edge.g)) edge = sampleValue;
            }
    return edge;
}

void main() {
    vec4 center = texture(source, qt_TexCoord0);
    vec4 edge = edgeSample();
    float alpha = max(0.0, max(edge.r,edge.g)-max(center.r,center.g)) * qt_Opacity;
    vec3 color = mix(vec3(1.0,0.58,0.16), edge.rgb, useMaskColors);
    fragColor = vec4(color*alpha, alpha);
}
