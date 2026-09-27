[app]
# (str) Title of your application
title = Игровой Центр

# (str) Package name
package.name = gamecenter

# (str) Package domain (unique identifier)
package.domain = org.gamecenter

# (str) Source code directory
source.dir = .

# (str) Application version
version = 1.0

# (str) Supported file extensions
source.include_exts = py,txt

# (str) List of inclusions using patterns
# source.include_patterns = assets/*

# (str) List of exclusions using patterns
# source.exclude_patterns = tests/*, bin/*

# (str) List of requirements
requirements = python3,kivy

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (bool) Warn if buildozer is run as root
warn_on_root = 1

[android]
# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Supported architectures
android.archs = arm64-v8a

# (bool) Enables Android app to be built with p4a
# android.private_storage = True

# (str) Android entry point, default is ok
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is None (deprecated)
# android.apptheme = "@android:style/Theme.NoTitleBar"
