import os
import shutil
from conans import ConanFile, CMake, tools


class XlntConan(ConanFile):
    name = "xlnt"
    version = "1.3.0"
    license = "MIT"
    url = "https://github.com/tfussell/xlnt"
    description = "Cross-platform user-friendly xlsx library for C++14"
    topics = ("Excel", "xlsx", "spreadsheet")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "build_test": [True, False],
               "build_samples": [True, False],
               "enable_benchmarks": [True, False],
               "enable_python": [True, False],
               }
    default_options = '''
shared=False
build_test=False
build_samples=False
enable_benchmarks=False
enable_python=False
    '''
    generators = "cmake"

    def source(self):

        zip_name = "xlnt.zip"
        zip_url = "https://github.com/tfussell/xlnt/archive/v%s.zip" % self.version

        print("Downloading from " + zip_url)
        tools.download(zip_url, zip_name)
        tools.unzip(zip_name)
        shutil.move("xlnt-%s" % self.version, "xlnt")
        # shutil.move(zip_name, "xlnt")
        os.unlink(zip_name)

        # self.run("git clone https://github.com/tfussell/xlnt.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly

        tools.replace_in_file("xlnt/CMakeLists.txt",
                              "project(xlnt_all)",
                              '''project(xlnt_all)
              include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
              conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if option_name == "shared":
                cmake.definitions["STATIC"] = "OFF" if activated else "ON"
            if option_name == "build_test":
                cmake.definitions["TESTS"] = "ON" if activated else "OFF"
            if option_name == "enable_python":
                cmake.definitions["PYTHON"] = "ON" if activated else "OFF"
            if option_name == "enable_benchmarks":
                cmake.definitions["BENCHMARKS"] = "ON" if activated else "OFF"
            if option_name == "build_samples":
                cmake.definitions["SAMPLES"] = "ON" if activated else "OFF"

        self.output.info(cmake.definitions)
        cmake.configure(source_folder="xlnt")
        cmake.build()

    def package(self):
        self.copy("*.hpp", dst="include", src="xlnt/include")
        self.copy("*xlnt.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["xlnt"]
        self.cpp_info.cxxflags = ["-std=c++14"]

    def configure(self):
        # self.settings.compiler.libcxx
        self.settings.compiler.cppstd = "14"

