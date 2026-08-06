# ProGuard & R8 configuration for Wallpaper Gallery Production Release

# Suppress missing class warnings for optional OkHttp and Conscrypt dependencies
-dontwarn org.conscrypt.**
-dontwarn okhttp3.internal.platform.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**
-dontwarn javax.annotation.**
-dontwarn com.google.android.play.core.**

# Keep OkHttp3 classes
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# Keep Flutter Engine and Plugin classes
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.embedding.engine.** { *; }
-keep class io.flutter.embedding.android.** { *; }

# Keep Native Plugins (async_wallpaper, gal, share_plus, in_app_review, etc.)
-keep class com.codenameakshay.async_wallpaper.** { *; }
-keep class tech.bymin.gal.** { *; }
-keep class dev.fluttercommunity.plus.share.** { *; }
-keep class io.flutter.plugins.sharedpreferences.** { *; }
-keep class io.flutter.plugins.urllauncher.** { *; }
-keep class dev.flutter.plugins.inappreview.** { *; }

# Keep all annotated classes and members
-keepattributes *Annotation*, Signature, InnerClasses, EnclosingMethod
-keepclassmembers class * {
    @androidx.annotation.Keep <fields>;
    @androidx.annotation.Keep <methods>;
}
