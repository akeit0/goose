/* This type exists in generated C only when the extern is used. */
static float native_sum(sl_f32 values) {
    float result = 0;
    for (int64_t i = 0; i < values.len; ++i) result += values.data[i];
    return result;
}
