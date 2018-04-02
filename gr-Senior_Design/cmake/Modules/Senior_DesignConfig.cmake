INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SENIOR_DESIGN Senior_Design)

FIND_PATH(
    SENIOR_DESIGN_INCLUDE_DIRS
    NAMES Senior_Design/api.h
    HINTS $ENV{SENIOR_DESIGN_DIR}/include
        ${PC_SENIOR_DESIGN_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SENIOR_DESIGN_LIBRARIES
    NAMES gnuradio-Senior_Design
    HINTS $ENV{SENIOR_DESIGN_DIR}/lib
        ${PC_SENIOR_DESIGN_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SENIOR_DESIGN DEFAULT_MSG SENIOR_DESIGN_LIBRARIES SENIOR_DESIGN_INCLUDE_DIRS)
MARK_AS_ADVANCED(SENIOR_DESIGN_LIBRARIES SENIOR_DESIGN_INCLUDE_DIRS)
