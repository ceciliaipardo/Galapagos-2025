//
//  SDL_main.c - iOS Kivy app entry point
//  SDL2 calls this function after initializing the iOS app
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#include "SDL.h"
#include "Python.h"
#include <dlfcn.h>

void export_orientation();
void load_custom_builtin_importer();

// SDL2 expects applications to define SDL_main
int SDL_main(int argc, char *argv[]) {
    int ret = 0;

    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

    // Change the executing path to YourApp using absolute path
    NSString * resourcePath = [[NSBundle mainBundle] resourcePath];
    NSString * yourAppPath = [resourcePath stringByAppendingPathComponent:@"YourApp"];
    chdir([yourAppPath UTF8String]);
    NSLog(@"Changed directory to: %@", yourAppPath);

    // Special environment to prefer .pyo, and don't write bytecode if .py are found
    putenv("PYTHONOPTIMIZE=2");
    putenv("PYTHONDONTWRITEBYTECODE=1");
    putenv("PYTHONNOUSERSITE=1");
    putenv("PYTHONPATH=.");
    putenv("PYTHONUNBUFFERED=1");
    putenv("LC_CTYPE=UTF-8");
    putenv("PYTHONVERBOSE=1");

    // Kivy environment to prefer some implementation on iOS platform
    putenv("KIVY_BUILD=ios");
    putenv("KIVY_WINDOW=sdl2");
    putenv("KIVY_IMAGE=imageio,tex,gif,sdl2");
    putenv("KIVY_AUDIO=sdl2");
    putenv("KIVY_GL_BACKEND=sdl2");
    putenv("IOS_IS_WINDOWED=False");

    #ifndef DEBUG
    putenv("KIVY_NO_CONSOLELOG=1");
    #endif

    // Export orientation preferences for Kivy
    export_orientation();

    NSString *python_home = [NSString stringWithFormat:@"PYTHONHOME=%@", resourcePath, nil];
    putenv((char *)[python_home UTF8String]);

    NSString *python_path = [NSString stringWithFormat:@"PYTHONPATH=.:%@:%@/lib/python3.11/:%@/lib/python3.11/site-packages", resourcePath, resourcePath, resourcePath, nil];
    putenv((char *)[python_path UTF8String]);
    NSLog(@"PYTHONPATH: %@", python_path);

    NSString *tmp_path = [NSString stringWithFormat:@"TMP=%@/tmp", resourcePath, nil];
    putenv((char *)[tmp_path UTF8String]);

    NSLog(@"Initializing python");
    Py_Initialize();

    wchar_t** python_argv = PyMem_RawMalloc(sizeof(wchar_t *) * argc);
    for (int i = 0; i < argc; i++)
        python_argv[i] = Py_DecodeLocale(argv[i], NULL);
    PySys_SetArgv(argc, python_argv);

    PyEval_InitThreads();

    // Add an importer for builtin modules
    load_custom_builtin_importer();
    
    // Add current working directory to Python path
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("import os");
    PyRun_SimpleString("sys.path.insert(0, os.getcwd())");
    PyRun_SimpleString("print('Python sys.path:', sys.path)");
    PyRun_SimpleString("print('Current directory:', os.getcwd())");
    PyRun_SimpleString("print('Files in current directory:', os.listdir('.'))");

    // Run main_ios.py
    NSString *mainPyPath = [NSString stringWithFormat:@"%@/main_ios.py", [[NSFileManager defaultManager] currentDirectoryPath]];
    NSLog(@"Attempting to run: %@", mainPyPath);
    NSLog(@"File exists: %@", [[NSFileManager defaultManager] fileExistsAtPath:mainPyPath] ? @"YES" : @"NO");
    
    const char * prog = [mainPyPath cStringUsingEncoding:NSUTF8StringEncoding];
    FILE* fd = fopen(prog, "r");
    if ( fd == NULL ) {
        ret = 1;
        NSLog(@"Unable to open main_ios.py at: %s", prog);
    } else {
        NSLog(@"Successfully opened main_ios.py, running...");
        ret = PyRun_SimpleFileEx(fd, prog, 1);
        if (ret != 0)
            NSLog(@"Application quit abnormally!");
    }

    Py_Finalize();
    NSLog(@"Leaving");

    [pool release];

    return ret;
}

void export_orientation() {
    NSDictionary *info = [[NSBundle mainBundle] infoDictionary];
    NSArray *orientations = [info objectForKey:@"UISupportedInterfaceOrientations"];

    NSString *result = [[NSString alloc] initWithString:@"KIVY_ORIENTATION="];
    for (int i = 0; i < [orientations count]; i++) {
        NSString *item = [orientations objectAtIndex:i];
        item = [item substringFromIndex:22];
        if (i > 0)
            result = [result stringByAppendingString:@" "];
        result = [result stringByAppendingString:item];
    }

    putenv((char *)[result UTF8String]);
    NSLog(@"Available orientation: %@", result);
}

void load_custom_builtin_importer() {
    static const char *custom_builtin_importer = \
        "import sys, imp, types\n" \
        "from os import environ\n" \
        "from os.path import exists, join\n" \
        "try:\n" \
        "    # python 3\n"
        "    import _imp\n" \
        "    EXTS = _imp.extension_suffixes()\n" \
        "    sys.modules['subprocess'] = types.ModuleType(name='subprocess')\n" \
        "    sys.modules['subprocess'].PIPE = None\n" \
        "    sys.modules['subprocess'].STDOUT = None\n" \
        "    sys.modules['subprocess'].DEVNULL = None\n" \
        "    sys.modules['subprocess'].CalledProcessError = Exception\n" \
        "    sys.modules['subprocess'].CompletedProcess = None\n" \
        "    sys.modules['subprocess'].check_output = None\n" \
        "except ImportError:\n" \
        "    EXTS = ['.so']\n"
        "# Fake redirection to supress console output\n" \
        "if environ.get('KIVY_NO_CONSOLE', '0') == '1':\n" \
        "    class fakestd(object):\n" \
        "        def write(self, *args, **kw): pass\n" \
        "        def flush(self, *args, **kw): pass\n" \
        "    sys.stdout = fakestd()\n" \
        "    sys.stderr = fakestd()\n" \
        "# Custom builtin importer for precompiled modules\n" \
        "class CustomBuiltinImporter(object):\n" \
        "    def find_module(self, fullname, mpath=None):\n" \
        "        if '.' not in fullname:\n" \
        "            return\n" \
        "        if not mpath:\n" \
        "            return\n" \
        "        part = fullname.rsplit('.')[-1]\n" \
        "        for ext in EXTS:\n" \
        "           fn = join(list(mpath)[0], '{}{}'.format(part, ext))\n" \
        "           if exists(fn):\n" \
        "               return self\n" \
        "        return\n" \
        "    def load_module(self, fullname):\n" \
        "        f = fullname.replace('.', '_')\n" \
        "        mod = sys.modules.get(f)\n" \
        "        if mod is None:\n" \
        "            try:\n" \
        "                mod = imp.load_dynamic(f, f)\n" \
        "            except ImportError:\n" \
        "                mod = imp.load_dynamic(fullname, fullname)\n" \
        "            sys.modules[fullname] = mod\n" \
        "            return mod\n" \
        "        return mod\n" \
        "sys.meta_path.insert(0, CustomBuiltinImporter())";
    PyRun_SimpleString(custom_builtin_importer);
}
