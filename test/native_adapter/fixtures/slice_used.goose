extern "native_sum" fn sum(values: const f32[:]) -> f32;
fn main() {
    let values: f32[2] = [1.0, 2.0];
    print(sum(values));
}
