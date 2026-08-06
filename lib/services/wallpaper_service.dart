import 'dart:io';
import 'package:async_wallpaper/async_wallpaper.dart' as aw;
import 'package:flutter/services.dart';
import 'package:gal/gal.dart';
import 'package:path_provider/path_provider.dart';
import '../models/wallpaper.dart';

/// Target screen for setting wallpaper on Android.
enum WallpaperTarget {
  homeScreen,
  lockScreen,
  both,
}

/// Service interface for setting device wallpapers.
abstract interface class IWallpaperService {
  Future<bool> setWallpaper(Wallpaper wallpaper, WallpaperTarget target);
}

/// Production implementation of [IWallpaperService] using [AsyncWallpaper] on Android and [Gal] on iOS.
final class LocalWallpaperService implements IWallpaperService {
  const LocalWallpaperService();

  @override
  Future<bool> setWallpaper(Wallpaper wallpaper, WallpaperTarget target) async {
    try {
      if (Platform.isAndroid) {
        final ByteData byteData = await rootBundle.load(wallpaper.imagePath);
        final Uint8List bytes = byteData.buffer.asUint8List(
          byteData.offsetInBytes,
          byteData.lengthInBytes,
        );

        final tempDir = await getTemporaryDirectory();
        final sanitizeName = wallpaper.id.replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
        final tempFile = File('${tempDir.path}/set_$sanitizeName.jpg');
        await tempFile.writeAsBytes(bytes, flush: true);

        aw.WallpaperTarget awTarget;
        switch (target) {
          case WallpaperTarget.homeScreen:
            awTarget = aw.WallpaperTarget.home;
            break;
          case WallpaperTarget.lockScreen:
            awTarget = aw.WallpaperTarget.lock;
            break;
          case WallpaperTarget.both:
            awTarget = aw.WallpaperTarget.both;
            break;
        }

        final request = aw.WallpaperRequest(
          source: tempFile.path,
          sourceType: aw.WallpaperSourceType.file,
          target: awTarget,
          goToHome: false,
        );

        final result = await aw.AsyncWallpaper.setWallpaper(request);
        if (result.isSuccess) {
          return true;
        }

        // Fallback: Open native Android wallpaper chooser if direct setting was restricted
        final chooserResult = await aw.AsyncWallpaper.openWallpaperChooser();
        return chooserResult.isSuccess;
      } else {
        // iOS: Save image to Photos library for user setup
        final ByteData byteData = await rootBundle.load(wallpaper.imagePath);
        final Uint8List bytes = byteData.buffer.asUint8List(
          byteData.offsetInBytes,
          byteData.lengthInBytes,
        );

        final sanitizeName = wallpaper.id.replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
        await Gal.putImageBytes(
          bytes,
          name: 'wallpaper_$sanitizeName',
        );
        return true;
      }
    } catch (_) {
      try {
        if (Platform.isAndroid) {
          final chooserResult = await aw.AsyncWallpaper.openWallpaperChooser();
          return chooserResult.isSuccess;
        }
      } catch (__) {}
      return false;
    }
  }
}
