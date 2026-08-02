[app]
title = Simple Calculator
package.name = simplecalculator
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

# Android permission needed for vibration
android.permissions = VIBRATE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
