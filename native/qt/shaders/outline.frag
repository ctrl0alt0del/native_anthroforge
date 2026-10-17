#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 texel;
};
layout(binding = 1) uniform sampler2D source;

void main() {
    float center = texture(source, qt_TexCoord0).r;
    float edge = center;
    for (int y = -2; y <= 2; ++y)
        for (int x = -2; x <= 2; ++x)
            if (x*x + y*y <= 5)
                edge = max(edge, texture(source, qt_TexCoord0 + vec2(x,y)*texel).r);
    float alpha = max(0.0, edge-center) * qt_Opacity;
    fragColor = vec4(vec3(1.0, 0.58, 0.16)*alpha, alpha);
}
