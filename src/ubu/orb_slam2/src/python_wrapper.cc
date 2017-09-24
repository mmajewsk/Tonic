#include "System.h"
#define PY_ARRAY_UNIQUE_SYMBOL PYVISION_ARRAY_API
#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <boost/python.hpp>
#include "include/pyboostcvconverter.h"
using namespace boost::python;
using namespace ORB_SLAM2;

class SystemWrapper: public System{
    public:
        SystemWrapper(){};
        void TrackMonocular(PyObject* im, const double &timestamp){
            cv::Mat in = pbcvt::fromNDArrayToMat(im);
            this->System::TrackMonocular(in, timestamp);
        }
        SystemWrapper(const string &strVocFile, const string &strSettingsFile, const eSensor sensor, const bool bUseViewer = true
            ):System(strVocFile, strSettingsFile,sensor,bUseViewer){};


};

static void init_ar( )
{
    // initialize
    Py_Initialize();

    // defined in numpy
    import_array();
}

BOOST_PYTHON_MODULE(orb_slam2py)
{
    /*class_<System>("BaseSystem", init<
            const std::string&,
            const std::string&,
            const SystemWrapper::System::eSensor,
            const bool
        >()
        )
    ;
    class_<SystemWrapper, bases<System>>("System")
        .def("TrackMonocular", &SystemWrapper::TrackMonocular)
        .def("GetKeyFrameTrajectoryTUM", &SystemWrapper::GetKeyFrameTrajectoryTUM)
        .def("Shutdown", &SystemWrapper::Shutdown)
    ;
*/

    init_ar();
    class_<SystemWrapper>("System"
        , init<
            const std::string&,
            const std::string&,
            const SystemWrapper::System::eSensor,
            const bool
        >()
        )
        .def("TrackMonocular", &SystemWrapper::TrackMonocular)
        .def("GetKeyFrameTrajectoryTUM", &SystemWrapper::GetKeyFrameTrajectoryTUM)
        .def("Shutdown", &SystemWrapper::Shutdown)
    ;
    enum_<SystemWrapper::eSensor>("eSensor")
        .value("MONOCULAR", SystemWrapper::MONOCULAR)
        .value("STEREO", SystemWrapper::STEREO)
        .value("RGBD", SystemWrapper::RGBD)
        .export_values()
        ;
}
