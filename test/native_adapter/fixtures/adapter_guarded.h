/* The fork emits this guard. Original Goose does not. */
#ifndef GS_TYPE_sl_f32
#define GS_TYPE_sl_f32
#pragma pack(push, 1)
typedef struct { float *data; int64_t len; } sl_f32;
#pragma pack(pop)
#endif
#include "adapter.h"
