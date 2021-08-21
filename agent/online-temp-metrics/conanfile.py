from conans import ConanFile, CMake

class HelloConan(ConanFile):
    name = "online_temp_metrics"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    # To prevent "ERROR: The file is a broken symlink" for python venv
    # we have to exclude it from the sources as documented in 
    # https://docs.conan.io/en/latest/reference/conanfile/attributes.html#exports-sources
    exports_sources = "*", "!.venv/*"

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

