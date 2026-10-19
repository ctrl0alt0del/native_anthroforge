static Vec af_muscle_unit(Vec value,Vec fallback={0,0,1}) {
    double length=norm(value);if(length<=1.0e-10)value=fallback,length=norm(value);
    return length<=1.0e-12?Vec{0,0,1}:mul(value,1.0/length);
}

