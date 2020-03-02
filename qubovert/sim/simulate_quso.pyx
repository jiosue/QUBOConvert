# distutils: language=c
#   Copyright 2020 Joseph T. Iosue
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

cimport cython
from libc.stdlib cimport malloc


cdef extern from "_simulate_quso.h":
    void simulate_quso(
        int len_state, int *state, double *h,
        int *num_neighbors, int *neighbors, double *J,
        int len_Ts, double *Ts, int *num_updates,
        int seed
    ) nogil


def _simulate_quso(len_state, state, h, num_neighbors,
                   neighbors, J, len_Ts, Ts, num_updates, seed):


    # convert all Python types to C
    cdef int c_len_state = len_state
    cdef int *c_state
    cdef double *c_h
    cdef int *c_num_neighbors
    cdef int *c_neighbors
    cdef double *c_J
    cdef int c_len_Ts = len_Ts
    cdef double *c_Ts
    cdef int *c_num_updates
    cdef int c_seed = seed

    c_state = <int *>malloc(len_state * cython.sizeof(int))
    c_h = <double *>malloc(len_state * cython.sizeof(double))
    c_num_neighbors = <int *>malloc(len_state * cython.sizeof(int))
    c_neighbors = <int *>malloc(len(neighbors) * cython.sizeof(int))
    c_J = <double *>malloc(len(J) * cython.sizeof(double))
    c_Ts = <double *>malloc(len(Ts) * cython.sizeof(double))
    c_num_updates = <int *>malloc(len(Ts) * cython.sizeof(int))

    for i in range(len_state):
        c_state[i] = state[i]
        c_h[i] = h[i]
        c_num_neighbors[i] = num_neighbors[i]
    for i in range(len(J)):
        c_neighbors[i] = neighbors[i]
        c_J[i] = J[i]
    for i in range(len_Ts):
        c_Ts[i] = Ts[i]
        c_num_updates[i] = num_updates[i]


    with nogil:
        simulate_quso(
            c_len_state, c_state, c_h,
            c_num_neighbors, c_neighbors, c_J,
            c_len_Ts, c_Ts, c_num_updates,
            c_seed
        )

    return [c_state[i] for i in range(len_state)]
