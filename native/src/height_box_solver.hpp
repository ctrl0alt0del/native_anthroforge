#pragma once
#include "af_smoothing/model.hpp"

namespace af::tissue {
std::unique_ptr<afs::QpSolver> make_box_heights();
}
