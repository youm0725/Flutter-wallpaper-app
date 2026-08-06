# ProGuard & R8 configuration for Wallpaper Gallery

# Suppress missing class warnings for optional OkHttp and Conscrypt dependencies
-dontwarn org.conscrypt.**
-dontwarn okhttp3.internal.platform.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**

# Keep OkHttp3 classes
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# Keep Flutter plugin classes
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
