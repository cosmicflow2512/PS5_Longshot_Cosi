/* PS5: what host/posix/win32_posix.c takes from Linux, and the console's answers (host/ps5/win32_ps5.c).

   The console is FreeBSD underneath with no /proc, no futex, no dynamic loading of our own code and a small
   flexible-memory budget beside a large direct-memory pool (PS5_PayloadSDK platform/docs/PROBE.md). The Win32 calls
   that touch those (memory, thread and fiber stacks, modules, futexes, the process's exit) are the PS5's own here;
   everything else in win32_posix.c is the Linux build's, unchanged.

   The guest window: Hookshot reserves the game's 39-bit address space at A64_HOST_BASE (16 TiB on a PC). The console
   grants nothing at or above 1 TiB, Mesa's RADV keeps [8, 12) GiB for its 32-bit window and [256, 512) GiB for device
   memory, and the platform layer's heap reserves 16 GiB at 128 GiB (PS5_HEAP_HINT). So the PS5 build puts the window at
   64 GiB and gives the game 64 GiB of it (host/hos.h HOS_GUEST_SPACE): host [64, 128) GiB, the guest's heap from 16 GiB
   and its address regions down from 64 GiB. */
#ifndef HOS_WIN32_PS5_H
#define HOS_WIN32_PS5_H
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>
#include <time.h>
#include <sys/param.h>
#include <sys/cpuset.h>
#include <pthread.h>
#include <pthread_np.h>   /* (pthread_getaffinity_np, pthread_setaffinity_np) */
typedef cpuset_t cpu_set_t;   /* (FreeBSD's name for Linux's cpu_set_t; CPU_ZERO, CPU_SET and CPU_ISSET take it) */

#ifndef A64_HOST_BASE
#error "the PS5 build sets A64_HOST_BASE (ps5/build.py)"
#endif
#ifdef __cplusplus
extern "C" {
#endif
#define HOS_PS5_GUEST_LO ((uintptr_t)A64_HOST_BASE)
#define HOS_PS5_GUEST_HI ((uintptr_t)A64_HOST_BASE + 0x1000000000ULL)   /* (64 GiB: host/hos.h HOS_GUEST_SPACE) */

/* Linux's private futex operations, as win32_posix.c names them; hos_ps5_futex does them with FreeBSD's _umtx_op */
#define FUTEX_WAIT_PRIVATE 128
#define FUTEX_WAKE_PRIVATE 129
long hos_ps5_futex(volatile uint32_t *word, int op, uint32_t value, const struct timespec *relative);
pid_t hos_ps5_tid(void);
int pthread_setname_np(pthread_t thread, const char *name);   /* (host/ps5/win32_ps5.c: none in the console's libraries) */

/* dlopen and dlsym over the libraries linked in: "hookshot_vk.dll" is the Vulkan back end, "vulkan-1.dll" RADV, and
   RTLD_DEFAULT the executable's own symbols that the Linux build finds across its .so boundary */
const char *hos_ps5_nup(void);   /* (the game's package on the console: host/ps5/win32_ps5.c) */
void *hos_ps5_dlopen(const char *path, int mode);
void *hos_ps5_dlsym(void *module, const char *name);
int hos_ps5_dlclose(void *module);
#define dlopen hos_ps5_dlopen
#define dlsym hos_ps5_dlsym
#define dlclose hos_ps5_dlclose

/* The title's executable and its folder: /app0 is the title folder, where image.bin, romfs/ and user/ go */
#define HOS_PS5_EXE "/app0/eboot.bin"

/* The process ends through the shell (sceSystemServiceLoadExec "exit"): _exit is a crash report on the console */
__attribute__((noreturn)) void hos_ps5_exit(int code);
#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
/* std::atomic_ref, which the SDK's C++ library does not have and the Vulkan back end uses on plain words and handles
   (gpu/vk/vk_draw.cpp, vk_memory.cpp, drawn_writeback.h): the compiler's atomic builtins on the object itself, for what
   the back end calls. This header comes before every other in those files (ps5/build.py's -include). */
#include <atomic>
#include <version>
#ifndef __cpp_lib_atomic_ref
namespace std {
template <class T> struct atomic_ref {
    explicit atomic_ref(T &object) : p(&object) {}
    T load(memory_order order = memory_order_seq_cst) const {
        T v;
        __atomic_load(p, &v, (int)order);
        return v;
    }
    void store(T v, memory_order order = memory_order_seq_cst) const { __atomic_store(p, &v, (int)order); }
    bool compare_exchange_strong(T &expected, T desired, memory_order order = memory_order_seq_cst) const {
        return __atomic_compare_exchange(p, &expected, &desired, false, (int)order,
                                         order == memory_order_release ? (int)memory_order_relaxed
                                         : order == memory_order_acq_rel ? (int)memory_order_acquire : (int)order);
    }
    T *p;
};
}   // namespace std
#endif
/* std::from_chars for float and double, which the SDK's C++ library does not have (its <charconv> has the integers'
   alone): ReShade FX's lexer and its preset reader (third_party/reshade_fx, gpu/vk/reshade/fx_runtime.cpp) read numbers
   with it. strtof/strtod on a copy, which ends where the number does, as from_chars does; a leading '+' or space, which
   from_chars refuses, is refused too */
#include <charconv>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <system_error>
#if !defined(__cpp_lib_to_chars)
namespace hos_ps5_charconv {
template <class T> inline std::from_chars_result parse(const char *first, const char *last, T &value) {
    char buf[128];
    const size_t n = (size_t)(last - first) < sizeof buf - 1 ? (size_t)(last - first) : sizeof buf - 1;
    if (!n || first[0] == '+' || first[0] == ' ' || first[0] == '\t') return {first, std::errc::invalid_argument};
    memcpy(buf, first, n);
    buf[n] = 0;
    char *end = buf;
    errno = 0;
    const T v = sizeof(T) == sizeof(float) ? (T)strtof(buf, &end) : (T)strtod(buf, &end);
    if (end == buf) return {first, std::errc::invalid_argument};
    if (errno == ERANGE) return {first + (end - buf), std::errc::result_out_of_range};
    value = v;
    return {first + (end - buf), std::errc{}};
}
}   // namespace hos_ps5_charconv
namespace std {
inline from_chars_result from_chars(const char *first, const char *last, float &value) {
    return hos_ps5_charconv::parse(first, last, value);
}
inline from_chars_result from_chars(const char *first, const char *last, double &value) {
    return hos_ps5_charconv::parse(first, last, value);
}
}   // namespace std
#endif
#endif
#endif
