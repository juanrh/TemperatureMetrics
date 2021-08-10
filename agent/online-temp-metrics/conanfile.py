from conans import ConanFile, CMake

class HelloConan(ConanFile):
    name = "online_temp_metrics"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "*"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("main", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ['bin']

    def deploy(self):
        # NOTE the source here is the package dir, not the source
        # we use for `conan create` but its output
        self.copy("*", dst="bin", src="bin")

