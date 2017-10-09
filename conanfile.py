from conans import ConanFile, CMake
from conans.tools import download, untargz, check_sha1
import os
import shutil

class JsoncppConan(ConanFile):
    name        = "jsoncpp"
    version     = "1.8.1"
    description = "A C++ library for interacting with JSON."
    url         = "https://github.com/kenfred/conan-jsoncpp"
    license     = "Public Domain or MIT (https://github.com/open-source-parsers/jsoncpp/blob/master/LICENSE)"
    FOLDER_NAME = 'jsoncpp-%s' % version
    settings    = "os", "compiler", "arch", "build_type"

    exports_sources = ["FindJsonCpp.cmake"]
    generators = "cmake", "txt"

    # Workaround for long cmake binary path
    short_paths = True

    options = {
        "shared": [True, False],
        "use_pic": [True, False]
    }
    default_options = (
        "shared=False",
        "use_pic=False"
    )

    def configure(self):
        if self.options.shared:
            self.options.use_pic = True

    def source(self):
        self.output.info("downloading source ...")
        tarball_name = self.FOLDER_NAME + '.tar.gz'
        download("https://github.com/open-source-parsers/jsoncpp/archive/%s.tar.gz" % self.version, tarball_name)
        check_sha1(tarball_name, "c91541b2dcc575ff8004e69caa5d2360bd4d042a")
        untargz(tarball_name)
        os.unlink(tarball_name)

    def build(self):
        cmake = CMake(self)

        defs = dict()
        defs['JSONCPP_WITH_CMAKE_PACKAGE'] = True
        defs['JSONCPP_WITH_TESTS'] = False
        defs['BUILD_SHARED_LIBS'] = self.options.shared
        defs['BUILD_STATIC_LIBS'] = not self.options.shared
        #defs['CMAKE_INSTALL_PREFIX'] = self.package_folder

        if self.options.use_pic:
            defs['CMAKE_POSITION_INDEPENDENT_CODE'] = True

        cmake.configure(source_dir=self.FOLDER_NAME, build_dir="./", defs=defs)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("FindJsonCpp.cmake", ".", ".")
        self.copy("license*", src=self.FOLDER_NAME, dst="licenses", ignore_case=True, keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(self.FOLDER_NAME, "include"))
        if self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            elif self.settings.os == "Windows":
                self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
                self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            if self.settings.os == "Windows":
                self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['jsoncpp']
