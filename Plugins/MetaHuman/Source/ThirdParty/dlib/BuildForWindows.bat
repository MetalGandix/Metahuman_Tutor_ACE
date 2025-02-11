if exist Build (rmdir Build /s/q)
mkdir Build
cd Build

cmake -G "Visual Studio 16 2019" -T version=14.29 -DCMAKE_INSTALL_PREFIX=Install -DDLIB_USE_MKL_FFT=0 -DDLIB_USE_BLAS=0 -DDLIB_USE_LAPACK=0 -DDLIB_USE_CUDA=0 -DDLIB_JPEG_SUPPORT=0 -DDLIB_PNG_SUPPORT=0 -DDLIB_GIF_SUPPORT=0 -DDLIB_LINK_WITH_SQLITE3=0 ../Source

"%_msbuild%msbuild.exe" dlib_project.sln /t:build /p:Configuration=Release

"%_msbuild%msbuild.exe" INSTALL.vcxproj /t:build /p:Configuration=Release

copy /y Install\lib\dlib19.23.0_release_64bit_msvc1929.libb ..\Lib\Win64\Releasedlib19.23.0_release_64bit_msvc1929.lib

if exist ..\Include\dlib (rmdir ..\Include\dlib /s/q)
xcopy /y/s/i Install\include\dlib ..\Include\dlib

cd ..
