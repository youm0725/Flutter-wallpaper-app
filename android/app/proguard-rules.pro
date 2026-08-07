# Flutter & Android ProGuard / R8 Configuration

# 1. Keep Flutter Engine, Main Activity, and Generated Registrants
-keep class com.example.wallpaper_app.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.GeneratedPluginRegistrant { *; }
-keep class io.flutter.app.FlutterApplication { *; }

# 2. Keep Flutter Plugin Android Packages
-keep class com.codenameakshay.async_wallpaper.** { *; }
-keep class tech.bymin.gal.** { *; }
-keep class dev.fluttercommunity.plus.share.** { *; }
-keep class dev.fluttercommunity.plus.packageinfo.** { *; }
-keep class dev.flutter.plugins.inappreview.** { *; }
-keep class io.flutter.plugins.sharedpreferences.** { *; }
-keep class io.flutter.plugins.urllauncher.** { *; }
-keep class io.flutter.plugins.pathprovider.** { *; }
-keep class dart.jni.** { *; }

# 3. Keep Kotlin & Coroutines
-dontwarn kotlin.**
-keep class kotlin.** { *; }
-keep class kotlinx.coroutines.** { *; }

# 4. Keep AndroidX & Lifecycle components
-dontwarn androidx.**
-keep class androidx.** { *; }

# 5. Keep OkHttp3 & Network classes
-dontwarn org.conscrypt.**
-dontwarn okhttp3.internal.platform.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**
-dontwarn javax.annotation.**
-dontwarn com.google.android.play.core.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# 6. Preserve annotations, generic signatures, inner classes, and exception attributes
-keepattributes *Annotation*, Signature, InnerClasses, EnclosingMethod
-keepclassmembers class * {
    @androidx.annotation.Keep <fields>;
    @androidx.annotation.Keep <methods>;
}

# 7. Keep Resource R classes to prevent resource shrinking issues
-keep class **.R$* { *; }
