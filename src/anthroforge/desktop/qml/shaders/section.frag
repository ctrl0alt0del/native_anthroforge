void MAIN()
{
    if (dot(VAR_WORLD_POSITION, clipNormal) + clipOffset < 0.0)
        discard;
    BASE_COLOR = vertexColor ? VAR_COLOR : tint;
    ROUGHNESS = 0.65;
    SPECULAR_AMOUNT = 0.25;
    if (unlit) EMISSIVE_COLOR = BASE_COLOR.rgb;
}
